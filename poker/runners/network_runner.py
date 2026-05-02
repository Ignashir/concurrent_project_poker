import time
import threading
import socket
from typing import List
import json

from poker.network.utils import send_msg, recive_msg
from poker.player.network_player import NetworkPlayer

HOST = "127.0.0.1"
PORT = 1978
MAX_TIME_FOR_PLAYERS_TO_LOG_IN = 100  # s
HEALTH_CHECK_PERIOD = 5
TIMEOUT_MSG = "To much time has passed, we need to close the session"
REJECT_MSG = "The lobby is full, you have been disconnected"
WELCOME_MSG = "Welcome to the Console Texas Hold'em Game!"
SERVER_STOP_MSG = "Stopping server..."


from enum import Enum

class ServerState(Enum):
    LOBBY = 1
    GAME = 2


class NetworkRunner:

    def __init__(self, game):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen()
        self.server.settimeout(1)

        self.game = game
        self.connected_players = 0

        self.lock = threading.Lock()
        self.start_condition = threading.Condition(self.lock)

        self.ready_flag = False
        self.running = True

        self.players = game.players
        self.connections = []

        self.state = ServerState.LOBBY

    def run(self):

        print("Server is up, waiting for connections...")

        # Admin thread
        threading.Thread(target=self.server_control, daemon=True).start()
        # Health check thread
        threading.Thread(target=self.connection_monitor, daemon=True).start()

        while self.running and not self.ready_flag:
            try:
                conn, addr = self.server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            thread = threading.Thread(
                target=self.manage_client,
                args=(conn, addr),
                daemon=True
            )
            thread.start()

            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        
        self.server.close()
        self.state = ServerState.GAME
        self.start_game()
        self.state = ServerState.LOBBY
    
    def lobby_listener(self, player):
        conn = player.conn

        try:
            while self.running and conn is not None:
                msg = recive_msg(conn)

                if msg == "QUIT":
                    print(f"[LOBBY QUIT] {player.name}")
                    self.handle_disconnect(conn)
                    return

        except Exception:
            # socket died
            print(f"[LOBBY DISCONNECT] {player.name}")
            self.handle_disconnect(conn)

    def start_game(self):
        
        while self.running:
            print(WELCOME_MSG)
            self.broadcast(WELCOME_MSG)
            winner = self.game.run_single_game()

            self.game.brodcast_msg(
                f"The winner is: {winner.name} with hand strength: "
                f"{winner.hand.evaluate_hand(self.game.community_cards)[0].name}"
            )
            #TODO ask all players if they want to play again

    
    def server_control(self):
        """Allows stopping server from console"""
        while True:
            cmd = input()
            if cmd == "help":
                options = {"stop": "Stop the server"}
                print(options) 
            if cmd == "stop":
                print(SERVER_STOP_MSG)
                self.save_game_state()
                self.broadcast(SERVER_STOP_MSG)
                time.sleep(0.5) 
                self.running = False
                with self.start_condition:
                    self.start_condition.notify_all()
                
                self.terminate_all_connections()

                self.server.close()
                break

    def terminate_all_connections(self):
        self.broadcast("=========STATE OF THE GAME=========")
        for player in self.players:
            self.broadcast(f"{player.name} (Chips: {player.chips}, My Bet: {player.my_current_bet})")
        
        for conn in self.connections:
            self.handle_disconnect(conn)

    
    def manage_client(self, conn, address):
        print(f"[NEW CONNECTION] {address} connected.")
        player = self.register_client(conn)
        
        if player:
            print(f"{player.name} assigned to {address}")

            threading.Thread(
                target=self.lobby_listener,
                args=(player,),
                daemon=True
            ).start()

            self.wait_for_all_players_to_be_registered(player)

        else:
            send_msg(REJECT_MSG, conn)
            conn.close()    

    def register_client(self, conn):
        with self.start_condition:
            if self.connected_players >= len(self.players):
                return None
            player = None
            for p in self.players:
                if p.conn is None:
                    player = p
                    break

            if player is None:
                raise ValueError("How the player got here when there are no more spots left")
            
            player.conn = conn
            self.connections.append(conn)
            self.connected_players += 1
            register_msg = "You have been registered"
            send_msg(register_msg, player.conn)

            status = f"[PLAYERS] {self.connected_players}/{len(self.players)}"
            print(status)
            self.broadcast(status)

            if self.connected_players == len(self.players):
                print("All players connected. Starting game...")
                self.ready_flag = True
                self.start_condition.notify_all()

            return player

    def wait_for_all_players_to_be_registered(self, player):
        start = time.time()
        while True:
            with self.start_condition:
                if self.ready_flag or not self.running:
                    return
                if player.conn is None: 
                    print(f"Thread for {player.name} exiting due to disconnect.")
                    return

                elapsed = time.time() - start
                if elapsed > MAX_TIME_FOR_PLAYERS_TO_LOG_IN:
                    conn = player.conn
                    break
                self.start_condition.wait(timeout=1)

        print("[TIMEOUT TRIGGERED]")
        send_msg(TIMEOUT_MSG, conn)
        self.handle_disconnect(conn)

    def broadcast(self, msg: str):
        dead_connections = []

        for conn in list(self.connections):
            try:
                send_msg(msg, conn)
            except Exception:
                dead_connections.append(conn)

        for conn in dead_connections:
            print("[DISCONNECT] Removing dead connection")
            self.handle_disconnect(conn)

    def connection_monitor(self):
        while self.running:
            time.sleep(HEALTH_CHECK_PERIOD)

            dead_connections = []

            for conn in list(self.connections):
                try:
                    send_msg("PING", conn)
                except:
                    dead_connections.append(conn)
            if dead_connections:
                for conn in dead_connections:
                    print("[DISCONNECT] Player lost connection")
                    self.handle_disconnect(conn)
    
    def handle_disconnect(self, conn):
        with self.start_condition:
            if conn in self.connections:
                self.connections.remove(conn)

            for p in self.players:
                if p.conn == conn:
                    print(f"[REMOVING PLAYER] {p.name}")
                    p.conn = None
                    break

            self.connected_players = len([c for c in self.connections])

            active_players = [p for p in self.players if p.conn is not None]

            if self.state == ServerState.LOBBY:
                if len(active_players) <= 1:
                    msg = "[LOBBY] Not enough players, waiting..."
                    print(msg)
                    self.broadcast(msg)
                    self.ready_flag = False

            elif self.state == ServerState.GAME:
                if len(active_players) <= 1:
                    msg = "[GAME] Only one player left → ending game"
                    print(msg)
                    self.broadcast(msg)
                    #TODO add some handling of the game state do not know rn
                    self.running = False

            self.start_condition.notify_all()

        try:
            conn.close()
        except:
            pass

        status = f"[PLAYERS] {self.connected_players}/{len(self.players)}"
        print(status)
        self.broadcast(status)

    def save_game_state(self):
        state = {
            "players": [
                {
                    "name": p.name,
                    "chips": p.chips,
                    "bet": p.my_current_bet,
                    "active": p.is_playing
                }
                for p in self.players
            ],
            "pot": self.game.pot,
            "community_cards": [str(c) for c in self.game.community_cards]
        }

        with open("game_state.json", "w") as f:
            json.dump(state, f, indent=4)