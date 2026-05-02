import socket
from poker.network.utils import send_msg, recive_msg
from poker.game_logic.action import ActionType
from poker.runners.network_runner import HOST, PORT, WELCOME_MSG, REJECT_MSG, TIMEOUT_MSG,HEALTH_CHECK_PERIOD, SERVER_STOP_MSG
from poker.player.network_player import YOUR_TURN_MSG, AMOUNT_MSG
import threading 
from queue import Queue
import time
import os

class Client():

    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.possible_actions = [action for action in ActionType]
        self.cmd_options = {"quit": "Stops the client"}
        
        self.active = threading.Event()
        self.active.set()

        self.command_queue = Queue()
        self.msg_queue = Queue()
        
        self.last_server_msg_time = time.time()
        self.ping_timeout = 10 * HEALTH_CHECK_PERIOD


    def run(self):
        
        self.control_thread = threading.Thread(target=self.client_control, daemon=True)
        self.control_thread.start()

        self.health_thread = threading.Thread(target=self.server_watchdog, daemon=True)
        self.health_thread.start()

        self.listener_thread = threading.Thread(target=self.server_listener, daemon=True)
        self.listener_thread.start()

        print("Connected to server.")

        self.registration_loop()

        try:
            self.game_loop()

        except Exception as e:
            print("Disconnected:", e)

        finally:
            self.active.clear()
            self.client.close()

            if self.control_thread.is_alive():
                self.control_thread.join(timeout=1)

    def registration_loop(self):
        try:
            while self.active.is_set():
                try:
                    msg = self.msg_queue.get(timeout=0.1)
                except:
                    continue
                if msg == WELCOME_MSG:                
                    break
                elif msg == REJECT_MSG or msg == TIMEOUT_MSG:
                    self.active.clear()

        except Exception as e:
            print("Disconnected:", e)

    def game_loop(self):
        while self.active.is_set():
            try:
                msg = self.msg_queue.get(timeout=0.1)
            except:
                continue

            if msg == YOUR_TURN_MSG:
                action = self.get_action_input()
                if action is None:
                    break
                self.send_msg_to_server(str(action))

            elif msg == AMOUNT_MSG:
                amount = self.get_amout_input()
                if amount is None:
                    break
                self.send_msg_to_server(str(amount))

    def get_action_input(self):
        while self.active.is_set(): 
            print(self.possible_actions)
            cmd = self.get_next_command()

            if cmd is None:
                return None

            if cmd == "quit":
                return None

            try:
                val = int(cmd)
                if 1 <= val <= 6:
                    return val
            except ValueError:
                pass

            print("Invalid input, try again.")

        return None

    def get_amout_input(self):
        while self.active.is_set():
            print("Enter amount: ")
            cmd = self.get_next_command()

            if cmd is None:
                return None

            if cmd == "quit":
                return None

            try:
                val = int(cmd)
                if val > 0:
                    return val
            except ValueError:
                pass

            print("Invalid input, try again.")

        return None

    def client_control(self):
        while self.active.is_set():
            try:
                cmd = input()
            except EOFError:
                break
            if not self.active.is_set():
                break
            self.command_queue.put(cmd)
            
            if cmd == "quit":
                self.disconnect()
                break
            elif cmd == "help":
                print(self.cmd_options)

    def disconnect(self):
        print("Quitting the game")

        try:
            send_msg("QUIT", self.client)
        except:
            pass

        self.active.clear()

    def get_next_command(self):
        while self.active.is_set():
            try:
                return self.command_queue.get(timeout=0.1)
            except:
                continue
        return None 

    def send_msg_to_server(self, msg):
        if self.active.is_set():
            send_msg(msg, self.client)


    def server_watchdog(self):
        while self.active.is_set():
            time.sleep(1)

            if time.time() - self.last_server_msg_time > self.ping_timeout:
                print("[WATCHDOG] No PING from server. Disconnecting...")
                self.active.clear()

                try:
                    self.client.shutdown(socket.SHUT_RDWR)
                    self.client.close()
                except:
                    pass
                break

    def server_listener(self):
        while self.active.is_set():
            try:
                msg = recive_msg(self.client)
            except:
                print("[DISCONNECTED FROM SERVER]")
                self.active.clear()
                break
            self.last_server_msg_time = time.time()
            if msg == "PING":
                continue


            if msg == SERVER_STOP_MSG:
                print("[SERVER STOP]")
                self.active.clear()

                try:
                    self.client.shutdown(socket.SHUT_RDWR)
                    self.client.close()
                except:
                    pass

                os._exit(0)
            
            print(msg)
            self.msg_queue.put(msg)
    
if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.run()