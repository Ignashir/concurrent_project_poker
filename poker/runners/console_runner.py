from poker.game.game import Game


class ConsoleRunner:
    def __init__(self, game: Game):
        self.game = game

    def run(self):
        print("Welcome to the Console Texas Hold'em Game!")
        self.game.start_game()
        while True:
            winner = self.game.run_single_game()

            print(f"The winner is: {winner.name} with hand strength: {winner.hand.evaluate_hand(self.game.community_cards)[0].name}")

            play_again = input("Do you want to play another game? (y/n): ")
            if play_again.lower() != 'y':
                print("Thanks for playing!")
                break