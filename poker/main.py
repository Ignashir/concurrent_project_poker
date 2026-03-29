import argparse

from poker.game.game import Game
from poker.player.console_player import ConsolePlayer

def console_main():
    num_players = int(input("Enter the number of players: "))
    players = ConsolePlayer.create_players(num_players, Game.STARTING_CHIPS)
    game = Game(players)
    game.run_single_game()

def network_main():
    pass

def test_main():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poker Game")
    parser.add_argument('--mode', choices=['console', 'network', 'test'], default='console', help='Mode to run the poker game (default: console)')
    args = parser.parse_args()

    if args.mode == 'console':
        console_main()
    elif args.mode == 'network':
        network_main()
    elif args.mode == 'test':
        test_main()
    else:
        print("Invalid mode selected. Please choose 'console' or 'network'.")



# TODO
# - Now all players can fold - there is no check if there is only one player left in the game. We should end the game immediately and declare the winner.
# - something might be off with counting of pot 