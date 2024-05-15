# This is where you build your AI for the Chess game.

from joueur.base_ai import BaseAI
from games.chess import my_game_logic as logic
from games.chess.get_move import Move
from copy import deepcopy
import time

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>

class AI(BaseAI):
    """ The AI you add and improve code inside to play Chess. """

    @property
    def game(self) -> 'games.chess.game.Game':
        """games.chess.game.Game: The reference to the Game instance this AI is playing.
        """
        return self._game # don't directly touch this "private" variable pls

    @property
    def player(self) -> 'games.chess.player.Player':
        """games.chess.player.Player: The reference to the Player this AI controls in the Game.
        """
        return self._player # don't directly touch this "private" variable pls

    def get_name(self) -> str:
        """This is the name you send to the server so your AI will control the player named this string.

        Returns:
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "Chess Python Player" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self) -> None:
        """This is called once the game starts and your AI knows its player and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your start logic
        # <<-- /Creer-Merge: start -->>

    def game_updated(self) -> None:
        """This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your game updated logic
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won: bool, reason: str) -> None:
        """This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why your AI won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>
    def make_move(self) -> str:
        """This is called every time it is this AI.player's turn to make a move.

        Returns:
            str: A string in Universal Chess Inferface (UCI) or Standard Algebraic Notation (SAN) formatting for the move you want to make. If the move is invalid or not properly formatted you will lose the game.
        """
        #fen_string = self.game.fen
        #return Move(self.game.fen)
        
        beginning_time = time.time()
        FEN = self.game.fen
        # Getting the color of the player
        color = self.player.color
        # Creating a gameboard
        my_gameBoard = logic.FEN_to_board(FEN)
        # Generating all valid moves of all players on the board
        all_valid_moves = logic.generate_all_moves(deepcopy(my_gameBoard),FEN,color)
        
        # Time-Limited Iterative-Deepening Depth-Limited MiniMax with Alpha-Beta Pruning 
        
        #Record the time of the given move
        time_moment = time.time()
        used_time = time_moment - beginning_time

        # Speed starting at the lowest level
        speed = 1

        # Avg num of mvoes
        MOVES_PER_GAME_AVG = 40

        # Cases where game is greater than 9, 11 and 13 minutes
        if MOVES_PER_GAME_AVG<25 and used_time>540:
            speed = 2
        elif MOVES_PER_GAME_AVG < 30 and used_time > 660:
            speed = 3
        elif MOVES_PER_GAME_AVG < 35 and used_time > 780:
            speed = 4

        logic.speed_of_thinking(speed)

        #Storing a move and its heuristic value
        move_values_dictionary = {} 
        
        # Initialize all values to be "impossibly low"
        for i in all_valid_moves:
          move_values_dictionary[i] = -100
         
        # Looping through each move
        for i in all_valid_moves: 
            # grab heuristic of the board state
            target_value = logic.boardGame_value(deepcopy(my_gameBoard), logic.change_color(color))
            # Make another move
            board_after_move = logic.move(deepcopy(my_gameBoard), i)
            # Get the heuristic value of the performed move
            heuristic_value = target_value - logic.boardGame_value(deepcopy(board_after_move), logic.change_color(color))
            # enerate opposite player's moves
            opposite_player_moves = logic.generate_all_moves(deepcopy(board_after_move), FEN, logic.change_color(color))
            # Set the inital value of the heuristic in the dictionary
            move_values_dictionary[i] = heuristic_value
            # Going over opposite player's moves
            for j in opposite_player_moves:
                # Take its heuristic
                heuristic_value_opposite = logic.boardGame_value(deepcopy(board_after_move), color)
                # Move
                postOppMoveBoard = logic.move(deepcopy(board_after_move), j)
                # Get new value
                new_value = heuristic_value_opposite - logic.boardGame_value(deepcopy(postOppMoveBoard), color)
                #The final value is the value of the difference between previous moves and opponents' best move  value
                final_value = heuristic_value - new_value
                # If less than value from dictionary, then update dictionary
                if final_value < move_values_dictionary[i]: 
                    move_values_dictionary[i] = final_value 
        # The highest heuristic value is the best.
        my_move = max(move_values_dictionary, key=move_values_dictionary.get)
        
        logic.print_gameBoard(my_gameBoard)
        print("Given the board above, my chosen move is: ",my_move)
        return my_move
        # <<-- /Creer-Merge: makeMove -->>

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    # <<-- /Creer-Merge: functions -->>
