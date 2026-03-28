from poker.game.game import Game

def main():
    num_players = int(input("Enter the number of players: "))
    game = Game(num_players)
    game.run_single_game()


if __name__ == "__main__":
    main()



# TODO
# - Now all players can fold - there is no check if there is only one player left in the game. We should end the game immediately and declare the winner.
# - 