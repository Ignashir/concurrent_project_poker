import socket
from poker.network.utils import send_msg, recive_msg
from poker.game_logic.action import ActionType
from poker.runners.network_runner import HOST, PORT, WELCOME_MSG, REJECT_MSG, TIMEOUT_MSG
from poker.player.network_player import YOUR_TURN_MSG, AMOUNT_MSG

class Client():

    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.active = True  
        self.possible_actions = [action for action in ActionType]

    def recive_server_msg(self) -> str:
            msg = recive_msg(self.client)
            if not msg:
                print("Server disconnected.")
                self.active = False
                return None
            
            if msg == "PING":
                return None

            print(f"[SERVER]: {msg}")
            return msg


    def run(self):
        print("Connected to server.")

        self.registration_loop()

        try:
            self.game_loop()

        except Exception as e:
            print("Disconnected:", e)

        finally:
            self.client.close()

    def registration_loop(self):
        try:
            while True:

                msg = self.recive_server_msg()
                if msg == WELCOME_MSG:                
                    break
                elif msg == REJECT_MSG or msg == TIMEOUT_MSG:
                    self.active = False
                    break

        except Exception as e:
            print("Disconnected:", e)

    def game_loop(self):
        while self.active:
            msg = self.recive_server_msg()

            if msg == YOUR_TURN_MSG:
                action = self.get_action_input()
                send_msg(str(action), self.client)

            elif msg == AMOUNT_MSG:
                amount = input("Enter amount: ")
                send_msg(amount, self.client)

    def get_action_input(self):

        print(self.possible_actions)
        while True:
            try:
                val = int(input("Action: "))
                if 1 <= val <= 6:
                    return val
            except ValueError:
                pass

            print("Invalid input, try again.")


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.run()