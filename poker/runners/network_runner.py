import time
import threading
import socket
from typing import List

from poker.network.utils import send_msg, recive_msg
from poker.player.network_player import NetworkPlayer

HOST = "127.0.0.1"
PORT = 1978
MAX_TIME_FOR_PLAYERS_TO_LOG_IN = 120  # s
HEALTH_CHECK_PERIOD = 10
TIMEOUT_MSG = "To much time has passed, we need to close the session"
REJECT_MSG = "The lobby is full, you have been disconnected"
WELCOME_MSG = "Welcome to the Console Texas Hold'em Game!"

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
        self.start_game()
    
    def start_game(self):
        
        print(WELCOME_MSG)
        self.broadcast(WELCOME_MSG)
        while True:
            winner = self.game.run_single_game()

            print(f"The winner is: {winner.name} with hand strength: {winner.hand.evaluate_hand(self.game.community_cards)[0].name}")

            play_again = input("Do you want to play another game? (y/n): ")
            if play_again.lower() != 'y':
                print("Thanks for playing!")
                break
    
    #TODO extend 
    def server_control(self):
        """Allows stopping server from console"""
        while True:
            cmd = input()
            print(cmd)
            if cmd == "stop":
                print("Stopping server...")
                self.running = False
                with self.start_condition:
                    self.start_condition.notify_all()
                self.server.close()
                break


    def manage_client(self, conn, address):
        print(f"[NEW CONNECTION] {address} connected.")
        player = self.register_client(conn)
        
        if player:
            print(f"{player.name} assigned to {address}")
            try:
                self.wait_for_all_players_to_be_registered(player)
            except TimeoutError as e:
                conn.close()
        else:
            send_msg(REJECT_MSG, conn)
            conn.close()
        # do not know rn

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
        with self.start_condition:
            while not self.ready_flag and self.running:
                if player.conn is None: 
                    print(f"Thread for {player.name} exiting due to disconnect.")
                    return

                elapsed = time.time() - start
                if elapsed > MAX_TIME_FOR_PLAYERS_TO_LOG_IN:
                    send_msg(TIMEOUT_MSG, player.conn)
                    raise TimeoutError("Players did not logged in in the required time")
                
                self.start_condition.wait(timeout=1)
    
    def broadcast(self, msg: str):
        for conn in self.connections:
            try:
                send_msg(msg, conn)
            except Exception as e:
                raise ValueError("broadcast something went wrong in the server")

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
            
            self.connected_players -= 1

            if self.ready_flag:
                print("Game interrupted due to disconnect")
                self.running = False
                self.broadcast("A player disconnected. Game stopped.")
                self.server.close()
            else:
                self.broadcast(f"[PLAYERS] {self.connected_players}/{len(self.players)}")

            self.start_condition.notify_all()