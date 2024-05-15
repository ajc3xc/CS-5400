import numpy as np



#main game logic for generating pseudovalid moves
class Board:
    def __init__(self, fen_string: str):
        # testing custom fen strings
        # fen_string = "rnbqkb1r/ppppppPp/5n2/8/8/8/Q3B3/RNB1K1NR w KQkq - 0 1"

        self.piece_symbols = {
            "r": 1,
            "n": 2,
            "b": 3,
            "q": 4,
            "k": 5,
            "p": 6,
            "R": 7,
            "N": 8,
            "B": 9,
            "Q": 10,
            "K": 11,
            "P": 12,
        }

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

        pieces_string = fen_string.split(" ")[0]
        self.color_active = fen_string.split(" ")[1]
        self.board, self.piece_positions = self.fen_to_matrix(pieces_string)

        #generate masks of where enemy and allied positions are
        self.enemy_mask = (
            (self.board < 7) & (self.board != 0)
            if self.color_active == "w"
            else (self.board > 6)
        )
        self.ally_mask = ~self.enemy_mask & (self.board != 0)

        # show list of possible castling options
        self.castling_string = fen_string.split(" ")[2]
        # show list of possible en passants possible
        possible_en_passant_string = fen_string.split(" ")[3]
        print(possible_en_passant_string)
        if len(possible_en_passant_string) == 2:
            # Extract file (column) and rank (row) from SAN
            file = possible_en_passant_string[0]
            rank = possible_en_passant_string[1]

            # Convert file to column: 'a' should correspond to column 0
            self.passant_col = ord(file) - ord("a")

            # Convert rank to row: '1' should correspond to row 7
            self.passant_row = 8 - int(rank)
        # in case of no passant
        else:
            self.passant_row = -1
            self.passant_col = -1

        # the other parts afterwards show # of halfmoves and fullmoves,
        # so they don't really matter that much

        # print current state of the board as-is
        self.print_board()

        # get list of potentially valid moves
        # self.get_all_pseudovalid_moves()

    # function that collects every single possible psuedo-legal move
    # TODO: make the functions use bitboards in the future
    def get_all_pseudovalid_moves(self):
        pseudovalid_moves = []
        pseudovalid_moves.extend(self.get_rook_moves())
        pseudovalid_moves.extend(self.get_bishop_moves())
        pseudovalid_moves.extend(self.get_queen_moves())
        pseudovalid_moves.extend(self.get_knight_moves())
        pseudovalid_moves.extend(self.get_king_moves())
        pseudovalid_moves.extend(self.get_pawn_moves())
        print(pseudovalid_moves)
        return pseudovalid_moves

    # get valid moves for sliding pieces (bishop, rook, queen)
    def get_moves(self, key: str, directions: list[tuple], is_slider=True):
        moves = []
        for position in self.piece_positions[key]:
            # Assuming position is a tuple (row, col)
            row, col = position
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
                        moves.append(self.move_to_san([row, col], [n_row, n_col]))
                        if self.enemy_mask[n_row, n_col]:
                            break
        return moves

    # get basic valid moves for non sliding pieces (knights, kings)
    # done in parallel with numpy masking
    # currently being unused because it would make invalid moves on occasion
    # for the next assigment, I may want to use this function again
    '''def get_non_sliding_moves(
        self, key: str, directions: list[tuple], non_pawn_capture=False
    ):
        moves = []

        positions = self.piece_positions[key]
        # Calculate possible moves for each position and each direction
        # Filter moves within board boundaries using NumPy array operations
        # First, ensure all are within the valid index range for an 8x8 chess board
        valid_moves = np.array(
            [
                [direction[0] + pos[0], direction[1] + pos[1]]
                for direction in directions
                for pos in positions
                if 0 <= direction[0] + pos[0] < 8 and 0 <= direction[1] + pos[1] < 8
            ]
        )
        valid_moves_starts = np.array(
            [
                pos
                for direction in directions
                for pos in positions
                if 0 <= direction[0] + pos[0] < 8 and 0 <= direction[1] + pos[1] < 8
            ]
        )

        # Convert list of tuples to a tuple of arrays for indexing
        rows, cols = valid_moves[:, 0], valid_moves[:, 1]

        # if it is a pawn not capturing, can't capture an enemy moving straight
        if non_pawn_capture:
            mask = ~self.ally_mask[rows, cols] & ~self.enemy_mask[rows, cols]
        else:
            # Simultaneously check if the moves are not blocked by allies
            mask = ~self.ally_mask[rows, cols]

        unblocked_moves = valid_moves[mask]
        unblocked_starts = valid_moves_starts[mask]

        moves = []
        for start_position, end_position in zip(
            unblocked_starts.reshape(-1, 2), unblocked_moves.reshape(-1, 2)
        ):
            print(start_position)
            moves.append(self.move_to_san(start_position, end_position))
        return moves'''

    def move_to_san(self, start_move, finish_move):
        # Assuming 'K' for king, add capture notation if applicable
        return f"{chr(start_move[1] + ord('a'))}{8 - start_move[0]}{chr(finish_move[1] + ord('a'))}{8 - finish_move[0]}"

    # customized function for getting pawn moves only
    def get_valid_pawn_moves(self, key, direction):
        positions = self.piece_positions[key]
        moves = []

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

        valid_forward_one_starts = forward_one_starts[valid_one_step_mask]
        valid_forward_one_ends = forward_one_moves[valid_one_step_mask]
        # Iterate over elements and print pairs
        moves.extend(
            self.pawn_moves_to_san(valid_forward_one_starts, valid_forward_one_ends)
        )

        # capture moves
        capture_directions = [(direction, -1), (direction, 1)]
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

        valid_capture_mask = (self.enemy_mask[tuple(capture_moves.T)]) | (
            (capture_moves[:, 0] == self.passant_row)
            & (capture_moves[:, 1] == self.passant_col)
        )

        valid_capture_starts = capture_moves_start[valid_capture_mask]
        valid_capture_ends = capture_moves[valid_capture_mask]

        # Iterate over elements and print pairs
        moves.extend(
            self.pawn_moves_to_san(
                valid_capture_starts, valid_capture_ends, capture=True
            )
        )

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
        '''[
                [position[0] + 2 * direction, position[1]]
                for position in positions
                if (position[0] + (2 * direction)) in {3, 4}
                and position[0] % 5 == 1
                and self.board[position[0]+1, position[1]] == 0
                and self.board[position[0]+2, position[1]] == 0
            ]
        
        )
        if forward_two_moves.size > 0:
            forward_two_starts = np.array(
                [
                    [position[0] - 2 * direction, position[1]]
                    for position in positions
                    if (position[0] + (2 * direction)) in {3, 4}
                    and position[0] % 5 == 1
                ]
            )

            valid_two_steps_mask = (
                ~self.board[tuple(forward_two_moves.T)]
            )
            
            print(tuple(forward_two_moves.T))

            valid_forward_two_starts = forward_two_starts[valid_two_steps_mask]
            valid_forward_two_ends = forward_two_moves[valid_two_steps_mask]'''
            # Iterate over elements and print pairs
        if forward_two_starts_list:
            moves.extend(
                self.pawn_moves_to_san(valid_forward_two_starts, valid_forward_two_ends)
            )

        return moves

    def pawn_moves_to_san(self, start_moves, end_moves, capture=False):
        # Convert the moves to SAN notation and handle promotions
        san_moves = []
        promotion_pieces = ["q", "r", "n", "b"]
        for i in range(start_moves.shape[0]):
            start_column = chr(start_moves[i, 1] + ord("a"))
            start_cell = f"{start_column}{8 - start_moves[i,0]}"
            end_row = end_moves[i, 0]
            end_cell = f"{chr(end_moves[i,1] + ord('a'))}{8 - end_moves[i,0]}"
            # promotion logic
            if end_row == 0 or end_row == 7:
                san_moves.extend(
                    [
                        f"{start_cell}{end_cell}{promotion_piece}"
                        for promotion_piece in promotion_pieces
                    ]
                )
            else:
                san_moves.append(f"{start_cell}{end_cell}")
        return san_moves

    # one of the simpler functions, gets the rook moves
    def get_rook_moves(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        if self.color_active == "w":
            key = "R"
        else:
            key = "r"
        return self.get_moves(key, directions)

    # one of the simpler functions for getting the bishop moves
    def get_bishop_moves(self):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # diagonal
        if self.color_active == "w":
            key = "B"
        else:
            key = "b"
        return self.get_moves(key, directions)

    # one of the simpler functions for getting the queen moves
    def get_queen_moves(self):
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]  # up, down, left, right + diagonals
        if self.color_active == "w":
            key = "Q"
        else:
            key = "q"
        return self.get_moves(key, directions)

    # one of the simpler functions for getting the knight moves
    def get_knight_moves(self):
        directions = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        ]  # all L directions
        if self.color_active == "w":
            key = "N"
        else:
            key = "n"
        return self.get_moves(key, directions, is_slider=False)

    # gets the king moves, checks for castling
    def get_king_moves(self):
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]  # up, down, left, right + diagonals
        if self.color_active == "w":
            key = "K"
        else:
            key = "k"
        # moves not involving castling
        moves = self.get_moves(key, directions, is_slider=False)

        #castling logic
        if self.color_active == "w":
            # Check for white's castling options
            king_row, king_col = (7, 4)
            if "K" in self.castling_string and not np.any(
                self.board[king_row, king_col + 1 : 7]
            ):
                moves.append("e1g1")
            if "Q" in self.castling_string and not np.any(
                self.board[king_row, 1:king_col]
            ):
                moves.append("e1c1")
        elif self.color_active == "b":
            king_row, king_col = (0, 3)
            # Check for black's castling options
            if "k" in self.castling_string and not np.any(
                self.board[king_row, 1:king_col]
            ):
                moves.append("e8g8")
            if "q" in self.castling_string and not np.any(
                self.board[king_row, king_col + 1 : 7]
            ):
                moves.append("e8c8")
        return moves

    def get_pawn_moves(self):
        if self.color_active == "w":
            key = "P"
            direction = -1
        else:
            key = "p"
            direction = 1

        return self.get_valid_pawn_moves(key, direction)

    def coordinate_to_algebraic(self, row, col):
        # Convert board coordinates to algebraic notation (e.g., (7, 0) -> "a8")
        return chr(col + ord("a")) + str(8 - row)

    def fen_to_matrix(self, positions_string: str):
        board = np.zeros(64, dtype=np.uint8)
        rows = positions_string.split("/")

        # set which pieces are your enemies based on active color
        if self.color_active == "w":
            enemies = 0
        else:
            enemies = 1

        # Dictionary to hold the positions of each type of piece, excluding enemies
        piece_positions = {
            key: []
            for key in self.piece_symbols.keys()
            if self.piece_symbols[key] // 7 != enemies
        }

        for i, row in enumerate(rows):
            pos = 0
            for char in row:
                if char.isdigit():
                    pos += int(char)
                else:
                    board[i * 8 + pos] = self.piece_symbols[char]
                    piece_code = self.piece_symbols[char]
                    if piece_code // 7 != enemies:
                        piece_positions[char].append((i, pos))
                    pos += 1
        # return board as 2d array
        # It should be a 2d array in the first place, but I don't feel like
        # changing up the code
        return board.reshape((8, 8)), piece_positions

    # utility function for seeing state of board
    def print_board(self):
        value_to_piece = {v: k for k, v in self.piece_symbols.items()}
        value_to_piece[0] = "."
        for row in self.board:
            print(" ".join(value_to_piece[val] for val in row))
