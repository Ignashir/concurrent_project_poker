import argparse

from poker.game.game import Game
from poker.player.console_player import ConsolePlayer
from poker.runners.console_runner import ConsoleRunner
from poker.runners.runner import Runner

from poker.runners.network_runner import NetworkRunner
from poker.player.network_player import NetworkPlayer

def console_main() -> Runner:
    num_players = int(input("Enter the number of players: "))
    players = ConsolePlayer.create_players(num_players, Game.STARTING_CHIPS)
    game = Game(players, "console")
    runner = ConsoleRunner(game)
    return runner

def network_main() -> Runner:
    num_players = 3#int(input("Enter the number of players: "))

    players = NetworkPlayer.create_players(num_players, Game.STARTING_CHIPS) 
    game = Game(players, "network")
    runner = NetworkRunner(game)
    return runner



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poker Game")
    parser.add_argument('--mode', choices=['console', 'network', 'test'], default='console', help='Mode to run the poker game (default: console)')
    args = parser.parse_args()

    if args.mode == 'console':
        runner = console_main()
    elif args.mode == 'network':
        runner = network_main()
    else:
        print("Invalid mode selected. Please choose 'console' or 'network'.")
    
    runner.run()



# TODO
# - Now all players can fold - there is no check if there is only one player left in the game. We should end the game immediately and declare the winner.
# - something might be off with counting of pot 