from games.chess.board import Board
import numpy as np
import random
from copy import deepcopy

#this class is used to find the best move to make using minimax algorithm
#simulates a bunch of moves until it can find the best locally optimal one, which it returns

class Move():    
    def __new__(self, fen_string: str):
        pieces_string = fen_string.split(" ")[0]
        self.color_active = fen_string.split(" ")[1]
        # show list of possible castling options
        self.castling_string = fen_string.split(" ")[2]
        player_castling, enemy_castling = False, False
        if self.color_active == 'w':
            if 'K' or 'Q' in self.castling_string:
                player_castling = True
            if 'k' or 'q' in self.castling_string:
                enemy_castling = True
        else:
            if 'K' or 'Q' in self.castling_string:
                enemy_castling = True
            if 'k' or 'q' in self.castling_string:
                player_castling = True
        # show list of possible en passants possible
        possible_en_passant_string = fen_string.split(" ")[3]
        
        #(-1, -1) is never on the board
        self.passant_cell = (-1, -1)
        if len(possible_en_passant_string) == 2:
            # Extract file (column) and rank (row) from SAN
            file = possible_en_passant_string[0]
            rank = possible_en_passant_string[1]

            # Convert file to column: 'a' should correspond to column 0
            passant_col = ord(file) - ord("a")

            # Convert rank to row: '1' should correspond to row 7
            passant_row = 8 - int(rank)
            passant_cell = (passant_row, passant_col)
        
        self.board, self.piece_symbols = Move.create_board_from_matrix(pieces_string)
        
        # = turns / 2
        moves_limit = 6
        
        #initialize, play move
        board = Board(self.board, self.piece_symbols, self.passant_cell, self.color_active, player_castling, enemy_castling, moves_limit)
        potential_moves: list[tuple[tuple, tuple, str]] = board.get_all_valid_moves()
        #print(potential_moves)
        #print([move for move in potential_moves])
        moves_stack = [{"board": deepcopy(board), "move": move} for move in potential_moves]
        if not potential_moves: return ""
        max_score = -9999999999
        #placeholder value
        max_score_move = potential_moves[0]       
        print("starting")
        #minimax algorithm
        while moves_stack:
            #print("...")
            move = moves_stack.pop(0)
            move_tuple = move["move"]
            move["board"].make_move(start_position=move_tuple[0], end_position=move_tuple[1], special_move_type=move_tuple[2])
            #I don't know why, but something here causes it to go into an infinite loop
            #Thus, I'm switching back to 
            potential_moves = move["board"].get_all_valid_moves()
            #hit the wall in terms of turns
            if move["board"].moves_count > moves_limit: continue
            #opposing player
            elif move["board"].moves_count %2 == 1:
                local_min_score = 99999999
                local_min_move = None
                min_board = None
                if not potential_moves: continue
                for move in potential_moves:
                    board_copy = deepcopy(move["board"])
                    #print(board_copy)
                    board_copy.make_move(move)
                    score = board_copy.calculate_score()
                    if score < local_min_score:
                        local_min_move = move
                        min_board = board
                potential_moves.append({"board": deepcopy(min_board), "move": local_min_move})
                if local_min_score > max_score:
                    max_score = local_min_score
                    max_score_move = move["board"].first_move
            #current player
            else:
                potential_moves.extend([{"board": deepcopy(board), "move": move} for move in potential_moves])
        
        return board.convert_to_uci(max_score_move[0], max_score_move[1], max_score_move[2])
            
        
            
        
        #return a move randomly
        if potential_moves:
            move = random.choice(potential_moves)
            moves_stack = [{"board": deepcopy(board), "move": move} for move in potential_moves]
            #print(move)
            #return "a2a4"
            return board.convert_to_uci(move[0], move[1], move[2])
        #no valid moves found
        else: return ""
        
        
        #create minimax (depth = 1)
        moves_stack = []
        
        
    
    @staticmethod   
    def create_board_from_matrix(pieces_str):
        piece_symbols = {
            "p": 1,
            "n": 2,
            "b": 3,
            "r": 4,
            "q": 5,
            "k": 6,
            "P": 7,
            "N": 8,
            "B": 9,
            "R": 10,
            "Q": 11,
            "K": 12,
        }
        
        rows = pieces_str.split("/")
        
        board = np.zeros(64, dtype=np.uint8)
        for i, row in enumerate(rows):
            pos = 0
            for char in row:
                if char.isdigit():
                    pos += int(char)
                else:
                    board[i*8 + pos] = piece_symbols[char]
                    pos += 1
                    
        # return board as 2d array
        # It should be a 2d array in the first place, but I don't feel like
        # changing up the code
        return board.reshape((8, 8)), piece_symbols
        