import numpy as np
from copy import deepcopy


class Board:
    def __init__(self, board: np.ndarray, piece_symbols: dict, passant_cell: tuple, color_active: str, player_castling: bool, enemy_castling: bool, moves_limit: int):
        # testing custom fen strings
        # fen_string = "rnbqkb1r/ppppppPp/5n2/8/8/8/Q3B3/RNB1K1NR w KQkq - 0 1"

        self.col_to_letter = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
        }
        
        #initialize directions for all pieces except pawns
        #whose direction depends on what side you are playing as
        self.knight_moves = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        ]  # all L directions
        
        self.king_moves = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]  # up, down, left, right + diagonals
        
        self.queen_directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]  # up, down, left, right + diagonals
        
        self.bishop_directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]  # up, down, left, right + diagonals
        
        self.rook_directions = [
            (-1, 0),
            (0, -1),
            (0, 1),
            (1, 0),
        ]  # up, down, left, right + diagonals

        self.board = board
        self.piece_symbols = piece_symbols
        self.passant_cell = passant_cell
        self.player_castling = player_castling
        self.enemy_castling = enemy_castling
        #self.moves_limit = moves_limit
        #2 moves per turn. 1 by white, 1 by black
        self.moves_count = 0
        self.first_move = None           
        
        #create 2 lists of dictionaries storing locations of enemy and friendly piece locations for each type
        self.set_color_and_pieces(color_active)

        self.enemy_mask = (
            (self.board < 7) & (self.board != 0)
            if self.color_active == "w"
            else (self.board > 6)
        )
        self.ally_mask = ~self.enemy_mask & (self.board != 0)

        # the other parts afterwards show # of halfmoves and fullmoves,
        # so they don't really matter that much

        # print current state of the board as-is
        self.print_board()
        
        
    def set_color_and_pieces(self, color: str):
        #set active color
        self.color_active = color
        
        #set enemy and ally masks
        self.enemy_mask = (
            (self.board < 7) & (self.board != 0)
            if self.color_active == "w"
            else (self.board > 6)
        )
        self.ally_mask = ~self.enemy_mask & (self.board != 0)
        
        self.set_pieces()
        
    
    def set_pieces(self):        
        # set which pieces are your enemies based on active color
        if self.color_active == "w":
            enemies = 0
        else:
            enemies = 1
        
        #the piece symbols stores the positions of each of the respective allied and enemy piece types
        #for convenience, both enemy and friendly piece types are stored as lowercase to make them easier to index
        #as it is assumed they are stored in seperate data structures
        piece_type_hash = {value: key.lower() for key, value in self.piece_symbols.items()} 

        # Dictionary to hold the positions of each type player piece
        self.player_piece_positions = {
            value: []
            for key, value in piece_type_hash.items()
            if key // 7 != enemies
        }
        
        #dictionary to hold the positions of each type of enemy piece
        self.enemy_piece_positions = {
           value: []
            for key, value in piece_type_hash.items()
            if key // 7 == enemies
        }
        
        #Dictionary to hold the positions of all enemy pieces
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                cell = self.board[i][j]
                if cell != 0:
                    cell_value = piece_type_hash[cell]
                    if cell // 7 == enemies:
                        self.enemy_piece_positions[cell_value].append((i, j))
                    else:
                        self.player_piece_positions[cell_value].append((i, j))                    
        return
        


    #calculate checks, pins and danger zones for the king piece
    def calculate_checks(self):
        #see what direction the enemy pieces would be attacking from
        if self.color_active == 'w':
            #attack down the board
            enemy_attacking_direction = 1
        else:
            enemy_attacking_direciton = -1
            
        #get the position of the king cell
        self.king_cell = self.player_piece_positions['k'][0]
        
        # Define the range of possible row and column shifts to find adjacent cells
        shifts = [-1, 0, 1]
        
        #Create a list of the values adjacent to the king on the board
        #squares that are 'danger zones' are removed from the adjacent squares
        self.king_available_moves = set()
        
        # Iterate over all possible shifts
        row, col = self.king_cell[0], self.king_cell[1]
        for row_shift in shifts:
            for col_shift in shifts:
                # Calculate the new row and column indices
                new_row, new_col = row + row_shift, col + col_shift                
                # Check if the new row and column are within bounds
                if (0 <= new_row < 8 and 0 <= new_col < 8)\
                    and not (row_shift == 0 and col_shift == 0)\
                    and not self.ally_mask[new_row, new_col]:
                    # Append the value at the adjacent cell to the list
                    self.king_available_moves.append((new_row, new_col))
                        
        #the positions checking the king,
        #and pinned positions
        self.check_positions, self.pinned_positions = set(), set()
        
        #calculate potential checks and no move zones using king, pawns and knights
        self.calculate_non_sliding_checks('n', self.knight_moves)
        self.calculate_non_sliding_checks('k', self.king_moves)
        #black pawns attack downwards, white pawns attack upwards
        #calculating for enemy pawns, not friendly pawns
        if self.color_active == "w":
            pawn_capture_moves = [
                (1, -1),
                (1, 1)
            ]
        else:
            pawn_capture_moves = [
                (-1, -1),
                (-1, 1)
            ]
        self.calculate_non_sliding_checks('p', pawn_capture_moves)
        
        #now calculate checks, no move zones and pins using queen, bishops and rooks
        self.calculate_sliding_checks('q', self.queen_directions)
        self.calculate_sliding_checks('r', self.rook_directions)
        self.calculate_sliding_checks('b', self.bishop_directions)
                    
    #calculate checks and no move zones by opposing king, knights and pawn
    def calculate_non_sliding_checks(self, piece: str, directions: list[tuple[int]]):
        for position in self.enemy_piece_positions[piece]:
            row, col = position
            for d in directions:
                move_cell = (row + d[0], col + d[1])
                if move_cell == self.king_cell:
                    self.check_positions.add(move_cell)
                elif move_cell in self.king_available_moves:
                    self.king_available_moves.discard(move_cell)
                            
    #calcualte checks and no move zones by opposing queen, rooks and bishops
    def calculate_sliding_checks(self, piece: str, directions: list[tuple[int]]):
        for position in self.enemy_piece_positions[piece]:
            #iterate through each direction, check if it has a potential attack vector to the king
            #since there is only one potential attack vector since they move in a line, break afterwards
            row, col = position
            for d in directions:
                #how many rows and cols do you have to move from the piece to the king
                attack_vector = (self.king_cell[0] - position[0], self.king_cell[1] - position[1])
                #variable determining whether or not this vector can check the king
                #needs to be a perfect diagonal or a straight line, and in the direction of the king
                rows_distance, cols_distance = abs(attack_vector[0]), abs(attack_vector[1])
                rows_sign, cols_sign = np.sign(self.king_cell[0]), np.sign(self.king_cell[1])
                can_check = ((rows_distance - cols_distance == 0 or rows_distance == cols_distance) and ((rows_sign, cols_sign) == d))
                #check if this attack vector is within a 90 degree angle of the king
                if rows_sign * d[0] >= 0 and cols_sign * d[1] >= 0:
                    #iterate through all diagonal or straight cells until you hit the king position                                        
                    pinned_cell = None
                    pinning_piece, passed_king = False, False
                    offset = 1
                    current_cell = row + d[0] * offset, col + d[1] * offset
                    while 0 <= current_cell[0] <= 7 and 0 <= current_cell[1] <= 7:
                        #check if this cell is within the square of adjacent squares the king can move to
                        if current_cell in self.king_available_moves:
                            self.king_available_moves.discard(current_cell)
                        #check if it hit another enemy piece, thus blocking it
                        if self.enemy_mask[current_cell]:
                            break
                        #is in line of sight of player piece
                        elif self.ally_mask[current_cell]:
                            #player piece is the king, not blocked by another piece
                            if current_cell == self.king_cell:
                                passed_king = True
                                #no piece is blocking it's line of sight
                                if not pinning_piece and can_check:
                                    self.check_positions.add(position)
                            #found piece blocking
                            elif not pinning_piece and can_check:
                                pinning_piece = True
                                pinned_piece = current_cell
                            #hit another player piece before hitting the king
                            #thereby, don't add the piece as pinned since it isn't pinned
                            elif not passed_king:
                                pinned_piece = None
                          
                        
    
    # function that collects every single possible psuedo-legal move
    # TODO: make the functions use bitboards in the future
    def get_all_valid_moves(self):
        #calculate checks, pins and danger zones
        #print(".")
        self.calculate_checks()
        
        valid_moves = []
        #Is the king under check by more than 2 pieces?
        #print(len(self.check_positions), len(self.pinned_positions))
        print(".")
        if len(self.check_positions) <= 1:
            valid_moves.extend(self.get_rook_moves())
            valid_moves.extend(self.get_bishop_moves())
            valid_moves.extend(self.get_queen_moves())
            valid_moves.extend(self.get_knight_moves())
            valid_moves.extend(self.get_pawn_moves())
        print("..")
        valid_moves.extend(self.get_king_moves())
        print("...")
        #print(self.moves_count, valid_moves)
        return valid_moves
    
    # get valid moves for sliding pieces (bishop, rook, queen)
    def get_moves(self, piece: str, directions: list[tuple], is_slider=True):       
        moves = []
        # print(key)
        for position in self.player_piece_positions[piece]:
            #don't move a pinned piece
            if position in self.pinned_positions: continue            
            elif self.check_positions:
                #this function only gets called if there is <= 1 checks on the king
                check_position = next(iter(self.check_positions))
                #go through every potential direction vector, see if any end on the check position
                for d in directions:
                    #knight logic only
                    if not is_slider:
                        if (position[0] + d[0], position[1] + d[1]) == check_position:
                            moves.append((position, check_position, "normal"))
                            break
                    #slider logic (queen, bishop, rook)
                    else:
                        attack_vector = (check_position[0] - position[0], check_position[1] - position[1])
                        #variable determining whether or not this vector can check the king
                        #needs to be a perfect diagonal or a straight line, and in the direction of the king
                        rows_distance, cols_distance = abs(attack_vector[0]), abs(attack_vector[1])
                        diagonal_or_straight = ((rows_distance - cols_distance == 0 or rows_distance == cols_distance) and ((rows_sign, cols_sign) == d))
                        #general attack direction, estimated by about 45 degrees on average
                        attack_direction = (np.sign(attack_vector[1]), np.sign(attack_vector[0]))
                        if d == attack_direction and diagonal_or_straight: 
                            moves.append((position, check_position, "normal"))
                            break
            else:                
                # Assuming position is a tuple (row, col)
                row, col = position
                # print(self.board[row, col])
                piece_type = self.board[row, col]
                if is_slider:
                    max_range = 8
                else:
                    max_range = 2
                for d in directions:
                    for offset in range(1, max_range):
                        n_row, n_col = row + d[0] * offset, col + d[1] * offset
                        if 0 <= n_row < 8 and 0 <= n_col < 8:
                            if self.ally_mask[n_row, n_col]:
                                break  # Not blocked by an ally
                            moves.append(([row, col], [n_row, n_col], "normal"))
                            if self.enemy_mask[n_row, n_col]:
                                break
        return moves

    #def move_to_san(self, start_move, finish_move):
    #    # Assuming 'K' for king, add capture notation if applicable
    #    return f"{chr(start_move[1] + ord('a'))}{8 - start_move[0]}{chr(finish_move[1] + ord('a'))}{8 - finish_move[0]}"

    # customized function for getting pawn moves only
    def get_valid_pawn_moves(self, key, direction):
        positions = self.player_piece_positions[key]
        moves = []
        
        #logic if king is in check
        if self.check_positions:
            capture_directions = [-1, 1]
            #this function only gets called if there is <= 1 checks on the king
            check_position = next(iter(self.check_positions))
            for position in positions:
                for capture_direction in capture_directions:
                    #where new move would end up at
                    move = (position[0] + direction, position[1] + capture_direction)
                    if move == check_position:
                        moves.append((position, move, "normal"))
                        break
        
        #king is not in check
        else:
            positions_np = np.array(positions)
            # One-step moves
            # get list of moves  that when transformed will stay in bounds
            forward_one_moves = np.array(
                [
                    [move[0] + direction, move[1]]
                    for move in positions
                    if 0 <= move[0] + direction < 8
                ]
            )

            forward_one_starts = np.array(
                [position for position in positions if 0 <= position[0] + direction < 8]
            )

            valid_one_step_mask = (
                ~self.ally_mask[tuple(forward_one_moves.T)]
                & ~self.enemy_mask[tuple(forward_one_moves.T)]
            )

            #lambda for setting promotions or not depending on final end position
            def move_output(start_cell, end_cell):
                if end_cell[0] == 7 or end_cell[0] == 0:
                    #since the queen combines the power of both the rook and bishop, no need to promote to them,
                    #but for the sake of getting all moves I'm adding them
                    promotion_types = ["promotion_queen", "promotion_knight", "promotion_bishop", "promotion_rook"]
                    return [(start_cell.tolist(), end_cell.tolist(), promotion_type) for promotion_type in  promotion_types]
                else: return [(start_cell.tolist(), end_cell.tolist(), "normal")]

            valid_forward_one_starts = forward_one_starts[valid_one_step_mask]
            valid_forward_one_ends = forward_one_moves[valid_one_step_mask]
            
            # Iterate over elements and print pairs
            moves.extend(
                [item for index, end in enumerate(valid_forward_one_ends) for item in move_output(valid_forward_one_starts[index], end)]
            )

            # capture moves
            '''capture_directions = [(direction, -1), (direction, 1)]
            capture_moves = np.array(
                [
                    [direction[0] + pos[0], direction[1] + pos[1]]
                    for pos in positions
                    for direction in capture_directions
                    if 0 <= direction[0] + pos[0] < 8 and 0 <= direction[1] + pos[1] < 8
                ]
            )

            capture_moves_start = np.array(
                [
                    pos
                    for pos in positions
                    for direction in capture_directions
                    if 0 <= direction[0] + pos[0] < 8 and 0 <= direction[1] + pos[1] < 8
                ]
            )

            valid_capture_mask = (self.enemy_mask[tuple(capture_moves.T)])
            print(valid_capture_mask)

            valid_capture_starts = capture_moves_start[valid_capture_mask].tolist()
            valid_capture_ends = capture_moves[valid_capture_mask].tolist()

            # Iterate over elements and print pairs
            moves.extend(
                [item for index, end in enumerate(valid_capture_ends) for item in move_output(valid_capture_starts[index], end)]
            )'''
            
            #also get any passant captures
            for position in positions:
                if (position[0], position[1] + 1) == self.passant_cell:
                    moves.append((position.tolist(), (position[0]+direction, position[1]+1).tolist(), "passant_capture"))
                    break
                elif (position[0], position[1] - 1) == self.passant_cell:
                    moves.append((position.tolist(), (position[0]+direction, position[1]-1).tolist(), "passant_capture"))
                    break
                for capture_direction in (-1, 1):
                    move_cell = position[0] + direction, position[1] + capture_direction
                    if 0 <= move_cell[1] < 8 and self.enemy_mask[move_cell]:
                        moves.append((position.tolist(), move_cell.tolist(), "normal"))

            # Two step moves
            # The start position must be either 6 or 1 (from 0 -7)
            # and must end in rows 3 to 4
            #i.e. x2x4 or x1x3
            #thus, we can ensure that the moves are valid
            # Since I need to vali
            forward_two_starts_list = [
                    position
                    for position in positions
                    if (position[0] + (2 * direction)) in {3, 4}
                    and position[0] % 5 == 1
                    and not any(self.board[position[0]:position[0]+3*direction, position[1]])
                ]
            valid_forward_two_ends = np.array([[position[0] + 2 * direction, position[1]] for position in forward_two_starts_list])
            valid_forward_two_starts = np.array(forward_two_starts_list)
            
            # Iterate over elements and print pairs
            if forward_two_starts_list:
                moves.extend(
                    [(start.tolist(), valid_forward_two_ends[index].tolist(), "normal") for index, start in enumerate(valid_forward_two_starts)]
                )
        #print("pawn moves")
        #print(moves)
        return moves

    # one of the simpler functions, gets the rook moves
    def get_rook_moves(self):
        return self.get_moves('r', self.rook_directions)

    # one of the simpler functions for getting the bishop moves
    def get_bishop_moves(self):
        return self.get_moves('b', self.bishop_directions)

    # one of the simpler functions for getting the queen moves
    def get_queen_moves(self):
        return self.get_moves('q', self.queen_directions)

    # one of the simpler functions for getting the knight moves
    def get_knight_moves(self):
        return self.get_moves('n', self.knight_moves, is_slider=False)

    # gets the king moves, checks for castling
    def get_king_moves(self):
        # moves not involving castling
        moves = [(self.king_cell, final_position, "normal") for final_position in self.king_available_moves]

        #castling logic
        #Can't castle if king is in check.
        #Also can't castle if the king moves or through a position in check,
        #but that logic would be too complicated, and any moves doing that in minimax will have a score resulting in 0,
        #if not in the last branch of minimax (which is extremely unlikely for a rarely used move)
        if not self.check_positions:
            # Check for white's castling options
            king_row, king_col = self.king_cell
            if self.player_castling:
                if not np.any(self.ally_mask[king_row, king_col + 1 : 7]):
                    moves.append(((king_row,4),(king_row,6), 'castle'))
                if  not np.any(self.ally_mask[king_row, 1:king_col]):
                    moves.append(((king_row,4),(king_row,2), "castle"))
        return moves

    def get_pawn_moves(self):
        key = "p"
        if self.color_active == "w":
            direction = -1
        else:
            direction = 1

        return self.get_valid_pawn_moves(key, direction)
    
    # utility function for seeing state of board
    def print_board(self):
        value_to_piece = {v: k for k, v in self.piece_symbols.items()}
        value_to_piece[0] = "."
        print(self.color_active)
        for row in self.board:
            print(" ".join(value_to_piece[val] for val in row))
    
    @staticmethod
    def convert_to_uci_cell(row, col):
        return chr(col + ord("a")) + str(8 - row)
    
    def convert_to_uci(self, start_cell, end_cell, special_move_type="normal"):
        # Convert board coordinates to algebraic notation (e.g., (7, 0) -> "a8")
        promotion_types = {
            "promotion_queen": "q",
            "promotion_rook": "r",
            "promotion_bishop": "b",
            "promotion_knight": "n"           
        }
        basic_uci_move = f"{Board.convert_to_uci_cell(start_cell[0], start_cell[1])}{Board.convert_to_uci_cell(end_cell[0], end_cell[1])}"
        if "promotion" not in special_move_type:
            return basic_uci_move
        else:   return f"{basic_uci_move}{promotion_types[special_move_type]}"
            
    def calculate_score(self):
        piece_value_dictionary = {
            "p": 100,
            "b": 300,
            "n": 300,
            "r": 500,
            "q": 900,
            "k": 100000
        }
        
        #get pieces value + .005 * the number of pieces in the center of the board
        total_score_player = sum(len(piece_list) * piece_value_dictionary[piece_type] for piece_type, piece_list in self.player_piece_positions) + 5 * np.count_nonzero(self.ally_mask[3:5])
        total_score_enemy = sum(len(piece_list) * piece_value_dictionary[piece_type] for piece_type, piece_list in self.enemy_piece_positions) + 5 * np.count_nonzero(self.ally_mask[3:5])
        
        #gets score for current piece played
        assert self.moves_count %2 == 0, "score gotten not after enemy player has played turn"
        #since doing after end of enemy player (and results are flipped bc data structures are flipped)
        return total_score_enemy - total_score_player
        
        
    
    #function for moving pieces along the board
    #contains logic for promotions, castling and en passant
    def make_move(self, start_position=None, end_position=None, special_move_type="normal"):
        #check if this is the first move.
        #If it is, convert it to uci
        if not self.moves_count:
            self.first_move = self.convert_to_uci(start_position, end_position, special_move_type)
            
        
        #save passant counter to temporary variable, wipe it
        passant_cell = self.passant_cell
        self.passant_cell = (-1, -1)
        
        #data structures used if promoting a piece
        if self.color_active == 'w':    starter_value = 6
        else: starter_value = 0
        
        #move piece
        print(end_position, self.board[end_position[0], end_position[1]], start_position, self.board[start_position[0], start_position[1]])
        self.board[end_position[0], end_position[1]] = self.board[start_position[0], start_position[1]]
        self.board[start_position[0], start_position[1]] = 0
        #special logic for double forward (initial pawn move), en passant or castling move
        if special_move_type == "passant_capture":
            self.board[passant_cell] = 0
        #move pawn forward 2 spaces
        elif special_move_type == "double_forward":
            self.passant_cell = end_position
        #castle
        elif special_move_type == "castle":
            #move corresponding rook for castling
            self.player_castling = False
            if end_position[1] == 6:
                start_column, end_column = 7, 5
            else:
                start_column, end_column = 0, 3
            self.board[end_position[0], end_column] == self.board[end_position[0], start_column]
            self.board[end_position[0], start_column] = 0
        #promotion types
        elif special_move_type == "promotion_queen":
            self.board[end_position[0], end_position[1]] = starter_value + self.piece_symbols['q']
        elif special_move_type == "promotion_rook":
            self.board[end_position[0], end_position[1]] = starter_value + self.piece_symbols['r']
        elif special_move_type == "promotion_bishop":
            self.board[end_position[0], end_position[1]] = starter_value + self.piece_symbols['b']
        elif special_move_type == "promotion_knight":
            self.board[end_position[0], end_position[1]] = starter_value + self.piece_symbols['n']
        
        #switch castling rights (since the board is being flipped)
        self.player_castling, self.enemy_castling = self.enemy_castling, self.player_castling
        
        #switch color and pieces    
        if self.color_active == 'w':
            self.set_color_and_pieces('b')
        else:
            self.set_color_and_pieces('w')
        self.moves_count += 1
        #self.score = self.calculate_score()
        #should be an even number
        #if self.moves_count == self.moves_limit:
        #    self.score = self.calculate_score()
            
        # print current state of the board as-is
        self.print_board()
        return