from copy import copy, deepcopy

#this is backup code in case I was not able to get my code completed on time
#slower, more inefficient method of calculating the optimal move
       
'''
GLOBAL VARIABLES:
'''
FIGURES = "rnbqkpRNBQKP" 
# 2 variables that represent rows and columns of a chess board.
ROWS = "01234567" 
COLUMNS = "abcdefgh" 
# Invalid figures to capture by colors
ILEGAL_CAPTURING_PAWN_WHITE = "RNBQKP k"
ILEGAL_CAPTURING_PAWN_BLACK = "rnbqkp K" 
ILEGAL_CAPTURING_ROOK_WHITE = "RNBQKPk"
ILEGAL_CAPTURING_ROOK_BLACK = "rnbqkpK" 
LEGAL_CAPTURING_ROOK_WHITE =  "rnbqp"
LEGAL_CAPTURING_ROOK_BLACK = "RNBQP" 
# List of figures on the board
FIGURES = "rnbqkpRNBQKP" 
# List of figures that we are going to use to score the board off of
VALUABLE_FIGURES_WHITE = "PRNBQ"
VALUABLE_FIGURES_BLACK = "prnbq"
# Number of points each figure is worth
VALUES_OF_FIGURES = "15339" 
# All possible knight directions
POSSIBLE_POSITIONS_KNIGHT = [   (-1,-2),
                                    (-1, 2),
                                    ( 1,-2),
                                    ( 1, 2),
                                    (-2, 1),
                                    (-2,-1),
                                    ( 2, 1),
                                    ( 2,-1)]
# Castling marks
CASTLING_K = False
CASTLING_Q = False

'''
DESCRIPTION: This function is going to calculate the value for hte board usid in ID-DLMM.
PRECONDITION: Required gameboard and color.
POSTCONDITION: Returns an int value fot the boardstate for the given color.
''' 
def boardGame_value(current_gameBoard, color):
    final_value = 0
    if color == "white":
        valuable_figures = VALUABLE_FIGURES_WHITE
    else:
        valuable_figures = VALUABLE_FIGURES_BLACK
    # Loop through entire board
    for k in range(8):
        for m in range(8):
            # Check if a found piece matches with one of teh valuable pieces
            if current_gameBoard[k][m] in valuable_figures: 
                found_piece = current_gameBoard[k][m]
                # Take the index of the found figure in the VALUABLE FIGURES list so you can get its value from the VALUES_OF_FIGURES
                figure_index = valuable_figures.find(found_piece)
                # Get the value of the figure using the index
                figure_value = VALUES_OF_FIGURES[figure_index] 
                # Increment the total value based on that figure
                final_value += int(figure_value) 
    return final_value

'''
DESCRIPTION: This function is going to change the color from black to white and oposite.
PRECONDITION: Required color strnig "white" or "black".
POSTCONDITION: Returns the string for oposite color of the color of input.
''' 
def change_color(color):
    if color == "white":
        oposite = "black"
    else:
        oposite = "white"
    return oposite
'''
DESCRIPTION: This function is going to generate all possible moves for all the figures on the board.
PRECONDITION: Required board, string fen and color for which to find moves for.
POSTCONDITION: Returns a list of all valid moves for all the players of a given color in a single list.
''' 
def generate_all_moves(current_board, FEN, color):
    # Promotion squares for pawns
    zone_of_promotion = ["a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"]
    
    # Figures to be promoted in 
    figures_for_promotion = ["Q","N","B","R"]
    
    legal_moves=[]
    
    pawn_all_moves = []
    pawn_all_moves += generate_pawn_moves(FEN, color)
     
    for k in pawn_all_moves:
        # Check if pawn is in the promotion zone
        if k[2:5] in zone_of_promotion:
            # Add valid moves when promote to Q,N,B,R
            for l in figures_for_promotion:
                if color == "black":
                    #append Q,N,B,R to moves
                    pawn_all_moves.append(k+l.lower()) 
                else:
                    pawn_all_moves.append(k+l)
            # Removing the move that lead into the promotion since now we have instead of b7b8, we have b7b8Q for instance
            pawn_all_moves.remove(k)
    # Adding valid moves from all of the players
    legal_moves += pawn_all_moves
    legal_moves += generate_rook_moves(FEN, color, 'R')
    legal_moves += generate_bishop_moves(FEN, color, 'B')
    legal_moves += generate_queen_moves(FEN, color)
    legal_moves += generate_king_moves(FEN, color)
    legal_moves += generate_night_rider_moves(FEN, color)
    
    
    
    legal_moves_no_check = []
    for i in legal_moves:
        # check if the move does not put the king in check and add it to valid moves
        if not is_in_check( move(deepcopy(current_board),i) , color):
            legal_moves_no_check.append(i)
            
    return legal_moves_no_check

'''
DESCRIPTION: This function is going to parse FEN string (EX. rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 )
            and create a SD array board. It will use only a part of the string that represents slots on the board (up to char 'R').
            '. will represent an empty space on the map.
PRECONDITION: FEN string must be passed as a parameter. We are able to hardcode number of rows and columns at the beginning
                since we know that it must be 8.
POSTCONDITION: Returning 2D array board.
'''
def FEN_to_board(FEN):
    # Getting the only part of the FEN string that is needed for this function.
    necessary_FEN = ""
    s=0
    while FEN[s]!=" ":
        necessary_FEN += FEN[s]
        s += 1
    # Creating an empty 2D array / gameBoard that consists of '.' signs.
    gameBoard = []
    for q in range(0,8):
        current_row = []
        for w in range(0,8):
            current_row.append(' ')
        gameBoard.append(current_row)
    # Translating neccessary_FEN string to the gameBoard 
    row = 0
    column = 0
    # Checking if the char is a figure and placing it on the board, otherwise it will be a number 
    # that tells how many open spaces and that many times we are going to skip the slot 
    for read_character in necessary_FEN:
        # If a figure, place it on the board
        if read_character in FIGURES:
            gameBoard[row][column] = read_character
        # If it is a '/' then move onto the next row and reset the column to 0
        elif read_character == '/':
            row += 1
            column = 0
            continue
        # Otherwise it will be a number of empty spaces
        else:
            num_empty_spaces = int(read_character)
            # skip num_empty_spaces for column
            column += num_empty_spaces
            continue
        # If it is non of that then move to the next slot in the row
        column += 1
        # If the column needs to be reset to the beginning 
        if column >= 8:
            column = 0
    return gameBoard

'''
DESCRIPTION: This function makes a certain move on the board and returns a gameoard with figures in order after the move is executed.
PRECONDITION: Requires a gameboard and a move that is a string.
POSTCONDITION: Returning a gameboard with figures in order after the move is executed.
'''
def move(current_board, action):
    # Again converting the notation to numeric for easier manipulation.
    # Since a move consists of 2 fields, the convert_notation_to_int() will be called twice.
    integer_notation = convert_notation_to_int(action[0]+action[1])+convert_notation_to_int(action[2]+action[3])
    numeric_notation_first_int = int(integer_notation[0])
    numeric_notation_second_int = int(integer_notation[1])
    numeric_notation_third_int = int(integer_notation[2])
    numeric_notation_fourth_int = int(integer_notation[3])
    
    # Selecting the piece that needs to be moved.
    moving_figure = current_board[8-numeric_notation_second_int][numeric_notation_first_int]
    
    # Set the previous position to empty '.'
    current_board[8-numeric_notation_second_int][numeric_notation_first_int] = ' '
    
    # Move the figure to its new position
    current_board[8-numeric_notation_fourth_int][numeric_notation_third_int] = moving_figure
    
    # Returning a deep copy of the board
    return deepcopy(current_board)

'''
DESCRIPTION: This function will find a list of all instances of a certain figure on the board and return the list of their coordinates.
            The numbering will be for 1 less than in real world for the purposes of iterations. If it needs to be displayed in future, we will add 1 to it.
            Returning yx instead of xy because we want letters/columns to be first in the notation.
PRECONDITION: GameBoard and desired fiure must be passed in as parameters.
POSTCONDITION: Returning a list of coordinates of each instance of the passed figure on the board
'''
def find_figure_occurance(gameBoard, figure):
    coordinates = []
    for row in range(0,8):
        for column in range (0,8):
            if gameBoard[row][column] == figure:
                yx = COLUMNS[column]+ROWS[row]
                coordinates.append(yx)
    return coordinates

'''
DESCRIPTION: This function inverts a move so it can be readable properly since the board in code is inverted.
PRECONDITION: Given a move.
POSTCONDITION: Returned a n inverted move.
'''
def invert_action(action):
    readable_action = ""
    # Add first character as it is and convert the second one to the oposite side
    readable_action += action[0]
    readable_action += str(8 - int(action[1]))
    # Add third character as it is and convert the fourth one to the oposite side
    readable_action += action[2]
    readable_action += str(8 - int(action[3]))
    return readable_action


'''
DESCRIPTION: This function inverts a given coordinate to the opposite side so it can be used when generating pawn moves.
PRECONDITION: Given a coordinate.
POSTCONDITION: Returns an inverted coordinate.
'''
def invert_coordinate(previous_coordinate):
    new_coordinate = ""
    new_coordinate += previous_coordinate[0]
    new_coordinate += str(8 - int(previous_coordinate[1]))
    return new_coordinate

'''
DESCRIPTION: This function's purpose is to convert the notation such as a3 to 03 in onrder to easily manipulate the strings.
            a --> 0
            b --> 1
            c --> 2
            d --> 3
            e --> 4
            f --> 5
            g --> 6
            h --> 7
PRECONDITION: The string that is being passed needs to be in Algebraic chess notation
POSTCONDITION: Returning the string converted in integers only
'''
def convert_notation_to_int(notation_string):
    int_notation = ""
    # Find the first letter of the notation in the column_letters string and use its index in int_notation
    int_letter = COLUMNS.find(notation_string[0])
    int_notation += str(int_letter)
    # Add another integer of the string as it is
    int_notation += notation_string[1]
    return int_notation

'''
DESCRIPTION: This function will filter moves to be without the ones that end up in check.
PRECONDITION: Required legal moves, game board and color.
POSTCONDITION: Returns legal moves without ones that could lead to the check.
'''
def filter_moves(legal_moves,current_gameBoard,color ):
    legal_moves_no_check = []
    for i in legal_moves:
        # check if the move does not put the king in check and add it to valid moves
        if not is_in_check( move(deepcopy(current_gameBoard),i) , color):
            legal_moves_no_check.append(i)
    return legal_moves_no_check

'''
DESCRIPTION: This function will generate valid moves for pawn.
             A pawn moves straight forward one square, if that square is vacant. If it has not yet moved, 
             a pawn also has the option of moving two squares straight forward, provided both squares are vacant. Pawns cannot move backwards. 
             A pawn can capture an enemy piece on either of the two squares diagonally in front of the pawn (but cannot move to those squares if they are vacant).
PRECONDITION: Required are FEN string and color that represents what side we are on.
POSTCONDITION: Returning list of valid moves for a pawn.
'''
def generate_pawn_moves(FEN, color):
    # Positions of all pawns on the board
    pawn_positions=[]
    # Valid moves for all pawns
    legal_moves=[]
    # Store positions from which pawns can make a 2 slot move
    black_move_2_enabled = ["h1", "g1", "f1", "e1", "d1", "c1", "b1", "a1"]
    white_move_2_enabled = ["h6", "g6", "f6", "e6", "d6", "c6", "b6", "a6"]
    
    # Getting the value for en passant
    en_passant = FEN.split()[3]

    # Getting the initial board
    current_gameBoard = FEN_to_board(FEN)
    
    # Set variables depending on colors
    if color == "black":
        increment_or_decrement = -1
        increment_or_decrement_2 = 1
        pawn_character = 'p'
        ilegal_capturing_string = ILEGAL_CAPTURING_PAWN_BLACK
        double_move_enabled = black_move_2_enabled
        double_inc_or_dec = 2
    elif color == "white":
        increment_or_decrement = 1
        increment_or_decrement_2 = -1
        pawn_character = 'P'
        ilegal_capturing_string = ILEGAL_CAPTURING_PAWN_WHITE
        double_move_enabled = white_move_2_enabled
        double_inc_or_dec = -2
        
    legal_moves.clear()
    # Checking for en passant if it is available by checking if the length of the string is 2
    if len(en_passant)==2:
        # Invert the en passant coordinate
        en_passant_inverted = invert_coordinate(en_passant)
        #Convert the en passant coordinate to integer notation
        numeric_notation =  convert_notation_to_int(en_passant_inverted)
        numeric_notation_first_int = int(numeric_notation[0])
        numeric_notation_second_int = int(numeric_notation[1])
        
        inc_or_dec_list=[]
        #Check available moves for en passant
        if numeric_notation_first_int - 1 >= 0:
            if current_gameBoard[numeric_notation_second_int + increment_or_decrement][numeric_notation_first_int - 1] == pawn_character:
                legal_move = COLUMNS[numeric_notation_first_int - 1] + str(numeric_notation_second_int + increment_or_decrement) + en_passant_inverted
                legal_moves.append(invert_action(legal_move))
        if numeric_notation_first_int + 1 <= 7:
            # inc_or_dec_list.append(1)
            if current_gameBoard[numeric_notation_second_int + increment_or_decrement][numeric_notation_first_int + 1] == pawn_character:
                legal_move = COLUMNS[numeric_notation_first_int + 1] + str(numeric_notation_second_int + increment_or_decrement) + en_passant_inverted
                legal_moves.append(invert_action(legal_move))
    
    # Search for all available pawns of the given color and place them in the list
    pawn_positions = find_figure_occurance(current_gameBoard , pawn_character) 
    #print(pawn_positions)
    
    # Generating a valid move for each piece:
    for iterator in pawn_positions: 
        inc_or_dec_list1=[]
        # Eating logic
        numeric_notation = convert_notation_to_int(iterator)
        numeric_notation_first_int = int(numeric_notation[0])
        numeric_notation_second_int = int(numeric_notation[1])
        if color == "black":
            # Eating on the right side
            if numeric_notation_first_int+1 <= 7 and numeric_notation_second_int+1<=7:
                inc_or_dec_list1.append(1)
            # Eating on the left side
            if numeric_notation_first_int-1 >= 0 and numeric_notation_second_int+1<=7:
                inc_or_dec_list1.append(-1)  
        elif color == "white":
            # Eating on the right side
            if numeric_notation_first_int + 1 <= 7 and numeric_notation_second_int - 1 >= 0:
                inc_or_dec_list1.append(1)
            #Eating on the left side
            if numeric_notation_first_int - 1 >= 0 and numeric_notation_second_int - 1 >= 0:
                inc_or_dec_list1.append(-1)
        # Loop through different directions
        for i in range (0, len(inc_or_dec_list1)):      
            inc_or_dec1 = inc_or_dec_list1[i]
            if current_gameBoard[numeric_notation_second_int+increment_or_decrement_2][numeric_notation_first_int+inc_or_dec1] not in ilegal_capturing_string:
                legal_move = iterator + COLUMNS[numeric_notation_first_int+inc_or_dec1]+ str(numeric_notation_second_int+increment_or_decrement_2)
                #inverting the move again since teh board in the code is inverted
                legal_moves.append(invert_action(legal_move))
        
        # In case of the initial game, pawn has ability to move 2 slots ahead
        if iterator in double_move_enabled and current_gameBoard[int(iterator[1]) + double_inc_or_dec][COLUMNS.find(iterator[0])] == ' ' and current_gameBoard[int(iterator[1])+increment_or_decrement_2][COLUMNS.find(iterator[0])]==' ':
            # Concatinate current move with same column, but next row
            legal_move = iterator + iterator[0] + str(int(iterator[1]) + double_inc_or_dec)
            legal_moves.append(invert_action(legal_move))
            
        # Checking for a 1 slot valid move
        if current_gameBoard[int(iterator[1])+increment_or_decrement_2][COLUMNS.find(iterator[0])] == ' ':
            # Concatinate current move with same column, but next row
            legal_move = iterator + iterator[0] + str(int(iterator[1]) + increment_or_decrement_2)
            legal_moves.append(invert_action(legal_move))
        
    # Gett all the moves without ones that are going to be in check
    legal_moves_no_check = filter_moves(legal_moves, current_gameBoard, color)
    
    return legal_moves_no_check
   
''' 
DESCRIPTION: Checking for valid moves in each direction:
                North --> 0
                South --> 1
                East --> 2
                West --> 3
            This function is a part of the rook valid moves function just for purposes of not repeating the same code.
PRECONDITION: Requires side, iterator, stretch_sign_inverter, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard,legal_moves,legal_capture_list,rook_stretch, figure, and break_out.
POSTCONDITION: Returns updated legal_moves, rook_stretch, and break_out.
PARAMETERS: side --> iterator that is responsible for what side we are checking.
iterator --> iterator from the outside loop.
stretch_sign_inverter --> used to change +1 to -1 and opposite depending on dirrection we are checking.
numeric_notation_first_int --> first character from algebraic notation transformed to numbers. 
numeric_notation_second_int --> second character from algebraic notation transformed to numbers.
current_gameBoard -->Current gameboard that is being played on.
legal_moves --> list of all legal moves that needs to be updated.
legal_capture_list --> list of legal capturing.
rook_stretch --> Distance away from the figure.
figure --> Figure that we are applying this function to.
break_out --> Boolean that checks if outside while loop needs to stop.
'''
def check_side_in_rook(side, iterator, stretch_sign_inverter, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard,legal_moves,legal_capture_list,rook_stretch, figure, break_out):
    # Checking for north and south
    if side == 0 or side == 1:
        legal_move = iterator + iterator[0] + str(numeric_notation_second_int + stretch_sign_inverter * rook_stretch)
        #inverting the move again since the current_gameBoard in the code is inverted
        legal_moves.append(invert_action(legal_move))
        # If a figure is eaten then stop looking
        if current_gameBoard[numeric_notation_second_int + stretch_sign_inverter*rook_stretch][numeric_notation_first_int] in legal_capture_list: 
            break_out= True
        # Since king only moves a rook_stretch of 1, we can stop searching if valid move is for K
        if figure.upper() == 'K':
            break_out= True
        # Checking for further distance
        if break_out == False:rook_stretch += 1
        return legal_moves, rook_stretch, break_out
    # Checking for eas and west
    elif side == 2 or side == 3:
        #loops while it does not go off the board and does not make an invalid capture
        legal_move = iterator + COLUMNS[numeric_notation_first_int + stretch_sign_inverter*rook_stretch] + iterator[1]
        legal_moves.append(invert_action(legal_move))
        if current_gameBoard[numeric_notation_second_int][numeric_notation_first_int + stretch_sign_inverter * rook_stretch] in legal_capture_list :
            break_out= True
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if figure.upper() == 'K':
            break_out= True
        if break_out == False: rook_stretch += 1 #check if the rook can move further now
        return legal_moves, rook_stretch, break_out

'''
DESCRIPTION:This function will generate valid moves for rok. 
            A rook moves any number of vacant squares horizontally or vertically. It also is moved when castling.
PRECONDITION: Requires figures color, fen string and a figure since it will also generate moves for queen and king since queend and king have all the abilities of rook. 
POSTCONDITION: Returns a list of valid moves for the rook, or partially for queen or king depending on what is being passed.
'''    
def  generate_rook_moves(FEN, color, figure):
    # Positions of all rooks on the board
    rook_positions=[]
    # Valid moves for all rooks
    legal_moves=[]
    
    # Getting the initial board
    current_gameBoard = FEN_to_board(FEN)
    
    if color == "black":
        rook_positions=find_figure_occurance(current_gameBoard , figure.lower())
        ilegal_capture_list = ILEGAL_CAPTURING_ROOK_BLACK
        legal_capture_list = LEGAL_CAPTURING_ROOK_BLACK
    elif color == "white":
        rook_positions=find_figure_occurance(current_gameBoard , figure.upper())
        ilegal_capture_list = ILEGAL_CAPTURING_ROOK_WHITE
        legal_capture_list = LEGAL_CAPTURING_ROOK_WHITE
        
    for iterator in rook_positions:
        # Convert the en passant coordinate to integer notation
        numeric_notation = convert_notation_to_int(iterator)
        numeric_notation_first_int = int(numeric_notation[0])
        numeric_notation_second_int = int(numeric_notation[1])
        
        # Recording how many empty spaces in fron of the rook
        rook_stretch = 1
        
        ''' Checking for valid moves in each direction:
            North --> 0
            South --> 1
            East --> 2
            West --> 3
        '''
        for i in range (0, 4):
            # Checking for north
            break_out = False
            rook_stretch = 1
            if i == 0:
                stretch_sign_inverter=-1
                while numeric_notation_second_int - rook_stretch >= 0 and current_gameBoard[numeric_notation_second_int - rook_stretch][numeric_notation_first_int] not in ilegal_capture_list:
                    legal_moves, rook_stretch, break_out = check_side_in_rook(i, iterator, stretch_sign_inverter, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, rook_stretch, figure, break_out)
                    if break_out == True : break
            # Checking south
            elif i == 1:
                stretch_sign_inverter=1
                while numeric_notation_second_int + rook_stretch <= 7 and current_gameBoard[numeric_notation_second_int + rook_stretch][numeric_notation_first_int] not in ilegal_capture_list:
                    legal_moves, rook_stretch, break_out = check_side_in_rook(i, iterator, stretch_sign_inverter, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, rook_stretch, figure, break_out)                    
                    if break_out == True : break
            # Checking east
            elif i == 2:
                stretch_sign_inverter=1
                while numeric_notation_first_int + rook_stretch <= 7 and current_gameBoard[numeric_notation_second_int][numeric_notation_first_int + rook_stretch] not in ilegal_capture_list:
                    legal_moves, rook_stretch, break_out = check_side_in_rook(i, iterator, stretch_sign_inverter, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, rook_stretch, figure, break_out)
                    if break_out == True : break
            # Checking west
            elif i == 3:
                stretch_sign_inverter=-1
                while numeric_notation_first_int - rook_stretch >= 0 and current_gameBoard[numeric_notation_second_int][numeric_notation_first_int - rook_stretch] not in ilegal_capture_list:
                    legal_moves, rook_stretch , break_out= check_side_in_rook(i, iterator, stretch_sign_inverter, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, rook_stretch, figure, break_out)
                    if break_out == True : break
    # Gett all the moves without ones that are going to be in check
    legal_moves_no_check = filter_moves(legal_moves, current_gameBoard, color)
    
    return legal_moves_no_check
 
''' 
DESCRIPTION: Checking for valid moves in each diagonal direction:
                North East --> 0
                South East--> 1
                South West --> 2
                North West --> 3
            This function is a part of the bishop valid moves function just for purposes of not repeating the same code.
PRECONDITION: Requires side, iterator, stretch_sign_inverter,stretch_sign_inverter2, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard,legal_moves,legal_capture_list,bishop_stretch, figure, and break_out.
POSTCONDITION: Returns updated legal_moves, bishop_stretch, and break_out.
PARAMETERS: side --> iterator that is responsible for what side we are checking.
iterator --> iterator from the outside loop.
stretch_sign_inverter --> used to change +1 to -1 and opposite depending on dirrection we are checking.
stretch_sign_inverter2 --> used to change +1 to -1 and opposite depending on dirrection we are checking.
numeric_notation_first_int --> first character from algebraic notation transformed to numbers. 
numeric_notation_second_int --> second character from algebraic notation transformed to numbers.
current_gameBoard -->Current gameboard that is being played on.
legal_moves --> list of all legal moves that needs to be updated.
legal_capture_list --> list of legal capturing.
bishop_stretch --> Distance away from the figure.
figure --> Figure that we are applying this function to.
break_out --> Boolean that checks if outside while loop needs to stop.
'''
def check_side_in_bishop(side, iterator, stretch_sign_inverter, stretch_sign_inverter2, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard,legal_moves,legal_capture_list,bishop_stretch, figure, break_out):
    legal_move = iterator + COLUMNS[numeric_notation_first_int + stretch_sign_inverter* bishop_stretch] + str(numeric_notation_second_int + stretch_sign_inverter2 * bishop_stretch)
    #inverting the move again since the current_gameBoard in the code is inverted
    legal_moves.append(invert_action(legal_move))
    # If a figure is eaten then stop looking
    if current_gameBoard[numeric_notation_second_int + stretch_sign_inverter2*bishop_stretch][numeric_notation_first_int++ stretch_sign_inverter*bishop_stretch] in legal_capture_list: 
        break_out= True
    # Since king only moves a rook_stretch of 1, we can stop searching if valid move is for K
    if figure.upper() == 'K':
        break_out= True
    # Checking for further distance
    if break_out == False: bishop_stretch += 1
    return legal_moves, bishop_stretch, break_out

'''
DESCRIPTION:This function will generate valid moves for bishop. 
            A bishop moves any number of vacant squares diagonaly.
PRECONDITION: Requires figures color, fen string and a figure since it will also generate moves for queen  since queend has all the abilities of bishop. 
POSTCONDITION: Returns a list of valid moves for the bishop, or partialy for queen.
'''                
def generate_bishop_moves(FEN,color, figure):
    # Positions of all bishops on the board
    bishop_positions=[]
    # Valid moves for all rooks
    legal_moves=[]
    
    # Getting the initial board
    current_gameBoard = FEN_to_board(FEN)       
    
    if color == "black":
        bishop_positions=find_figure_occurance(current_gameBoard , figure.lower()) 
        ilegal_capture_list = ILEGAL_CAPTURING_ROOK_BLACK
        legal_capture_list = LEGAL_CAPTURING_ROOK_BLACK
    elif color == "white":
        bishop_positions=find_figure_occurance(current_gameBoard , figure.upper())
        ilegal_capture_list = ILEGAL_CAPTURING_ROOK_WHITE
        legal_capture_list = LEGAL_CAPTURING_ROOK_WHITE
    
    for iterator in bishop_positions:
        # Convert the en passant coordinate to integer notation
        numeric_notation = convert_notation_to_int(iterator)
        numeric_notation_first_int = int(numeric_notation[0])
        numeric_notation_second_int = int(numeric_notation[1])
        
        # Recording how many empty spaces diagonally from bishop
        bishop_stretch = 1
        
        ''' Checking for valid moves in each direction:
            North - East --> 0
            South - East --> 1
            East - West--> 2
            West - West --> 3
        '''
        for i in range (0, 4):
            break_out = False;
            bishop_stretch=1
            if i == 0:
                stretch_sign_inverter = 1
                stretch_sign_inverter2 = -1
                # Checking for north - east
                while numeric_notation_second_int - bishop_stretch >= 0 and numeric_notation_first_int +  bishop_stretch <= 7 and current_gameBoard[numeric_notation_second_int-bishop_stretch][numeric_notation_first_int+bishop_stretch] not in ilegal_capture_list:
                    legal_moves, bishop_stretch , break_out = check_side_in_bishop(i, iterator, stretch_sign_inverter,stretch_sign_inverter2, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, bishop_stretch , figure, break_out)
                    if break_out == True : break
            elif i == 1:
                stretch_sign_inverter = 1
                stretch_sign_inverter2 = 1
                # Checking for south - east
                while numeric_notation_second_int + bishop_stretch <= 7 and numeric_notation_first_int + bishop_stretch <= 7 and current_gameBoard[numeric_notation_second_int+bishop_stretch][numeric_notation_first_int+bishop_stretch]not in ilegal_capture_list:
                    legal_moves, bishop_stretch , break_out = check_side_in_bishop(i, iterator, stretch_sign_inverter,stretch_sign_inverter2, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, bishop_stretch , figure, break_out)
                    if break_out == True : break
            elif i == 2:
                stretch_sign_inverter = -1
                stretch_sign_inverter2 = 1
                # Checking for north - west
                while numeric_notation_second_int + bishop_stretch <= 7 and numeric_notation_first_int - bishop_stretch >= 0 and current_gameBoard[numeric_notation_second_int+bishop_stretch][numeric_notation_first_int-bishop_stretch]not in ilegal_capture_list:
                    legal_moves, bishop_stretch , break_out = check_side_in_bishop(i, iterator, stretch_sign_inverter,stretch_sign_inverter2, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, bishop_stretch , figure, break_out)
                    if break_out == True : break
            elif i == 3:
                stretch_sign_inverter = -1
                stretch_sign_inverter2 = -1
                # Checking for south - west
                while numeric_notation_second_int - bishop_stretch >= 0 and numeric_notation_first_int - bishop_stretch >= 0 and current_gameBoard[numeric_notation_second_int-bishop_stretch][numeric_notation_first_int-bishop_stretch]not in ilegal_capture_list:
                    legal_moves, bishop_stretch , break_out = check_side_in_bishop(i, iterator, stretch_sign_inverter,stretch_sign_inverter2, numeric_notation_first_int, numeric_notation_second_int, current_gameBoard, legal_moves, legal_capture_list, bishop_stretch , figure, break_out)
                    if break_out == True : break
    # Gett all the moves without ones that are going to be in check
    legal_moves_no_check = filter_moves(legal_moves, current_gameBoard, color)
    
    return legal_moves_no_check

       
'''
DESCRIPTION: This function will generate valid moves for queen. 
            The queen moves any number of vacant squares horizontally, vertically, or diagonally.
            Legal moves for queen will be generated by using generate_bishop_moves() for diagonal moves and generate_rook_moves() for adjecent moves.
PRECONDITION: Required are FEN string and color that represents what side we are on.
POSTCONDITION: Returning list of valid moves for a queen.
'''
def generate_queen_moves(FEN, color):
     # Positions of all queens on the board
    queen_positions=[]
    # Valid moves for all queens
    legal_moves=[]
    
    # Getting the initial board
    current_gameBoard = FEN_to_board(FEN)  
    
    if color == "black":
        queen_character = 'q'
    else:
        queen_character = 'Q'
    #Find all queen positions
    queen_positions=find_figure_occurance(current_gameBoard , queen_character) 
    
    #add all the valid moves using generate_bishop_moves() for diagonal moves and generate_rook_moves() for adjecent moves.
    for iterator in queen_positions:
        legal_moves+= generate_bishop_moves(FEN, color, queen_character)
        legal_moves+= generate_rook_moves(FEN, color, queen_character)
    
    # Gett all the moves without ones that are going to be in check
    legal_moves_no_check = filter_moves(legal_moves, current_gameBoard, color)
    
    return legal_moves_no_check

'''
DESCRIPTION: This function will generate valid moves for king. 
            The king moves any number of vacant squares horizontally, vertically, or diagonally.
            Legal moves for king will be generated by using generate_bishop_moves() for diagonal moves and generate_rook_moves() for adjecent moves.
PRECONDITION: Required are FEN string and color that represents what side we are on.
POSTCONDITION: Returning list of valid moves for a king.
'''
def generate_king_moves(FEN, color):
    global CASTLING_K
    global CASTLING_Q
     # Positions of all kings on the board
    king_positions=[]
    # Valid moves for all kings
    legal_moves=[]
    
    # Getting the initial board
    current_gameBoard = FEN_to_board(FEN) 
    
    #select the castling part of the string FEN
    castling_string = FEN.split()[2]

    if color == "black":
        king_character = 'k'
        board_coordinates = [(0,5),(0,6),(0,3),(0,2),(0,1)]
        queen_character = 'q'
        castling_king="e8g8"
        castling_queen="e8c8"
    else:
        king_character = 'K'
        queen_character = 'Q'
        board_coordinates = [(7,5),(7,6),(7,3),(7,2),(7,1)]
        castling_king="e1g1"
        castling_queen="e1c1"
    #find all kings on the board
    king_positions = find_figure_occurance(current_gameBoard , king_character)
    
    for iterator in king_positions:
        # Castling - check if it is possiible
        if not is_in_check(current_gameBoard , color):
            x,y = board_coordinates[0]
            x1,y1 = board_coordinates[1]
            if king_character in castling_string and current_gameBoard[x][y] == ' ' and current_gameBoard[x1][y1] == ' ':
                # There is a possible castle
                CASTLING_K = True
                # Check if we do castle, are we going to be checked? If not, then that is a legal move
                if is_in_check(current_gameBoard, color) == False:
                    legal_moves.append(castling_king) #Castling king side
            x2,y2 = board_coordinates[2]
            x3,y3 = board_coordinates[3]
            x4,y4 = board_coordinates[4]
            if queen_character in castling_string and current_gameBoard[x2][y2] == ' ' and current_gameBoard[x3][y3] == ' ' and current_gameBoard[x4][y4] == ' ':
                # There is a possible castle
                CASTLING_Q = True
                # Check if we do castle, are we going to be checked? If not, then that is a legal move
                if is_in_check(current_gameBoard, color) == False:
                    legal_moves.append(castling_queen) #Castling king side
            
        legal_moves += generate_bishop_moves(FEN, color, king_character) 
        legal_moves += generate_rook_moves(FEN, color, king_character) 
    # Gett all the moves without ones that are going to be in check
    legal_moves_no_check = filter_moves(legal_moves, current_gameBoard, color)
    
    return legal_moves_no_check

'''
DESCRIPTION: This function checks if the coordinates are in bounds of the board.
PRECONDITION: Given coordinates x and y.
POSTCONDITION: Retruns True or False if in bounds or not.
'''
def check_in_bounds(coordinate_x, coordinate_y):
    return coordinate_x >= 0 and coordinate_x <=7 and coordinate_y >= 0 and coordinate_y <=7
'''
DESCRIPTION: This function checks if a single coordinate is in bounds of the board.
PRECONDITION: Given coordinates x.
POSTCONDITION: Retruns True or False if in bounds or not.
'''
def check_in_bounds_single(coordinate):
    return coordinate<=7 and coordinate>=0
'''
DESCRIPTION: This function will generate valid moves for night rider.
            A knight moves to the nearest square not on the same rank, file, or diagonal.
            The knight is not blocked by other pieces: it jumps to the new location.
PRECONDITION: Required are FEN string and color that represents what side we are on.
POSTCONDITION: Returning list of valid moves for a knight A.K.A. night rider.
'''
def generate_night_rider_moves(FEN,color):
    # Positions of gell knights on the board
    knight_positions=[]
    # Valid moves for all knights
    legal_moves=[]
    
    # Getting the initial board
    current_gameBoard = FEN_to_board(FEN) 

    if color == "black":
        knight_character = 'n'
        ilegal_capture_list = ILEGAL_CAPTURING_ROOK_BLACK
    else:
        knight_character = 'N'
        ilegal_capture_list = ILEGAL_CAPTURING_ROOK_WHITE
    
    # Get all knight positions
    knight_positions = find_figure_occurance(current_gameBoard , knight_character)
    for iterator in knight_positions:
        # Convert the en passant coordinate to integer notation
        numeric_notation = convert_notation_to_int(iterator)
        numeric_notation_first_int = int(numeric_notation[0])
        numeric_notation_second_int = int(numeric_notation[1])
        
        # Iterate through the dictionary of all possible knjight moves and check if they are legal
        for x,y in POSSIBLE_POSITIONS_KNIGHT:
            new_x = numeric_notation_first_int + x
            new_y = numeric_notation_second_int + y
            if check_in_bounds(new_x, new_y) == True and  current_gameBoard[new_y][new_x] not in ilegal_capture_list:
                legal_move = iterator + COLUMNS[new_x] + str(new_y)
                legal_moves.append(invert_action(legal_move))
    # Gett all the moves without ones that are going to be in check
    legal_moves_no_check = filter_moves(legal_moves, current_gameBoard, color)
    
    return legal_moves_no_check
  
''' 
DESCRIPTION: Checking for valid moves in each direction:
                North --> 0
                South --> 1
                East --> 2
                West --> 3
            This function is a part of the is_in_check() for purposes of not repeating the same code.
PRECONDITION: Requires iterator, stretch, stretch_sign_inverter, current_gameBoard, numeric_notation_first_int, numeric_notation_second_int,rook_queen, checked, king_to_get_checked_by.
POSTCONDITION: Returns updated checked,stretch,break_out.
PARAMETERS: side --> iterator that is responsible for what side we are checking.
iterator --> iterator from the outside loop.
stretch_sign_inverter --> used to change +1 to -1 and opposite depending on dirrection we are checking.
numeric_notation_first_int --> first character from algebraic notation transformed to numbers. 
numeric_notation_second_int --> second character from algebraic notation transformed to numbers.
current_gameBoard -->Current gameboard that is being played on.
rook_queen --> string that keeps opposite color queen and rook characters.
checked --boolean that keeps if the figure is checked or not.
king_to_get_checked_by --> opposite color king.
break_out --> Boolean that checks if outside while loop needs to stop.
'''
def rook_or_queen (iterator, stretch, stretch_sign_inverter, current_gameBoard, numeric_notation_first_int, numeric_notation_second_int,rook_queen, checked, king_to_get_checked_by,break_out ):
    if iterator<2:
        # Checking if it si being checked by a queen or rook
        if current_gameBoard[numeric_notation_second_int + stretch * stretch_sign_inverter][numeric_notation_first_int] in rook_queen:
            checked = True
            break_out = True
        # Checking if it is being by another king
        if current_gameBoard[numeric_notation_second_int + stretch * stretch_sign_inverter][numeric_notation_first_int] == king_to_get_checked_by and stretch == 1:
            checked = True
            break_out = True
        if break_out==False: stretch+=1
    else:
        # Checking if it si being checked by a queen or rook
        if current_gameBoard[numeric_notation_second_int][numeric_notation_first_int + stretch * stretch_sign_inverter] in rook_queen:
            checked = True
            break_out = True
        # Checking if it is being by another king
        if current_gameBoard[numeric_notation_second_int][numeric_notation_first_int + stretch * stretch_sign_inverter] == king_to_get_checked_by and stretch == 1:
            checked = True
            break_out = True
        if break_out==False: stretch+=1
    return checked,stretch,break_out 

''' 
DESCRIPTION:This function is a part of the is_in_check() for purposes of not repeating the same code.
PRECONDITION: Requires numeric_notation_first_int, numeric_notation_second_int, stretch, stretch_sign_inverter, stretch_sign_inverter2, current_gameBoard,queen_or_bishop_checked, bishop_queen, king_to_get_checked_by.
POSTCONDITION: Returns updated checked,stretch.
PARAMETERS: stretch_sign_inverter --> used to change +1 to -1 and opposite depending on dirrection we are checking.
stretch_sign_inverter2 --> used to change +1 to -1 and opposite depending on dirrection we are checking.
numeric_notation_first_int --> first character from algebraic notation transformed to numbers. 
numeric_notation_second_int --> second character from algebraic notation transformed to numbers.
current_gameBoard -->Current gameboard that is being played on.
queen_or_bishop_checked --> A string that keeps an empty space ' ' bishop,queen, and king of oposite color figures.
bishop_queen --> string that keeps opposite color queen and bishop characters.
checked --boolean that keeps if the figure is checked or not.
king_to_get_checked_by --> opposite color king.
'''
def bishop_or_queen (checked, numeric_notation_first_int, numeric_notation_second_int, stretch, stretch_sign_inverter, stretch_sign_inverter2, current_gameBoard,queen_or_bishop_checked, bishop_queen, king_to_get_checked_by):
    while check_in_bounds(numeric_notation_second_int + stretch * stretch_sign_inverter, numeric_notation_first_int + stretch * stretch_sign_inverter2) and \
        current_gameBoard[numeric_notation_second_int + stretch * stretch_sign_inverter][numeric_notation_first_int + stretch * stretch_sign_inverter2] in queen_or_bishop_checked:
        
        if current_gameBoard[numeric_notation_second_int + stretch * stretch_sign_inverter][numeric_notation_first_int + stretch * stretch_sign_inverter2] in bishop_queen:
             checked = True
             break
        if current_gameBoard[numeric_notation_second_int + stretch * stretch_sign_inverter][numeric_notation_first_int + stretch * stretch_sign_inverter2] in king_to_get_checked_by and stretch == 1:
             checked = True
             break
        stretch += 1
    return checked, stretch
'''
DESCRIPTION: This function will check if king is in check.
PRECONDITION: Requires color and game board as input.
POSTCONDITION: Returns true or false based on if King is in Check or not
'''
def is_in_check( current_gameBoard,color):
    # Variable that keeps if gameboard is in check or not
    checked = False
    # Castling marks that get updated in generate king moves ()
    global CASTLING_K
    global CASTLING_Q
    if color == "white":
        king_character = 'K'
        king_to_get_checked_by = 'k'
        knight_to_get_checked_by = 'n'
        queen_or_rook_ckecked = " rqk"
        queen_or_bishop_checked = " bqk"
        rook_queen = "rq"
        bishop_queen = "bq"
        pawn_to_be_checked_by = "p"
        pawn_check_one = -1
        castling_check_k = "f7"
        castling_check_q = "d7"
    else:
        king_character = 'k'
        king_to_get_checked_by = 'K'
        knight_to_get_checked_by = 'N'
        queen_or_rook_ckecked = " RQK"
        queen_or_bishop_checked = " BQK"
        rook_queen = "RQ"
        bishop_queen = "BQ"
        pawn_to_be_checked_by = "P"
        pawn_check_one = 1
        castling_check_k = "f0"
        castling_check_q = "f7"
    # Finding all kings on the board and their positions
    king_list = find_figure_occurance(current_gameBoard , king_character)
    # Checking to see if there was a possible and valid castling on king and queen side and adding the positions where rook would end up
    # in castling to the king_list in order to see if that position can be checked. If so, then by using recursion in valid king moves () 
    # we will not add that castling to the list of final legal moves
    if CASTLING_K == True:
        king_list.append(castling_check_k)
    if CASTLING_Q == True:
        king_list.append(castling_check_q)
    for iterator in king_list:
        numeric_notation = convert_notation_to_int(iterator)
        numeric_notation_first_int = int(numeric_notation[0])
        numeric_notation_second_int = int(numeric_notation[1])
        
        # Check if checked by a knight. Iterating over a dictionary of knight moves.
        for x,y in POSSIBLE_POSITIONS_KNIGHT:
            new_x = numeric_notation_first_int + x
            new_y = numeric_notation_second_int + y
            if check_in_bounds(new_x, new_y) == True and  current_gameBoard[new_y][new_x] == knight_to_get_checked_by:
                checked = True;
                if checked == True: break
                
        # Check if it is checked by rook or a queen
        for i in range (0, 4):
            stretch = 1
            break_out = False;
            if i == 0:
                # Check for Up direction
                stretch_sign_inverter =-1
                while check_in_bounds_single(numeric_notation_second_int - stretch) and current_gameBoard[numeric_notation_second_int - stretch][numeric_notation_first_int] in queen_or_rook_ckecked:
                    checked,stretch, break_out = rook_or_queen(i, stretch, stretch_sign_inverter, current_gameBoard, numeric_notation_first_int, numeric_notation_second_int, rook_queen, checked, king_to_get_checked_by, break_out)
                    if break_out == True: break
            if i ==1:
                # Check for Down direction
                stretch_sign_inverter = 1
                while check_in_bounds_single(numeric_notation_second_int + stretch) and current_gameBoard[numeric_notation_second_int + stretch][numeric_notation_first_int] in queen_or_rook_ckecked:
                    checked,stretch, break_out = rook_or_queen(i, stretch, stretch_sign_inverter, current_gameBoard, numeric_notation_first_int, numeric_notation_second_int, rook_queen, checked, king_to_get_checked_by, break_out)
                    if break_out == True: break
            if i == 2:
                # Check for Right direction
                stretch_sign_inverter = 1
                while check_in_bounds_single(numeric_notation_first_int + stretch) and current_gameBoard[numeric_notation_second_int][numeric_notation_first_int + stretch] in queen_or_rook_ckecked:
                    checked,stretch, break_out = rook_or_queen(i, stretch, stretch_sign_inverter, current_gameBoard, numeric_notation_first_int, numeric_notation_second_int, rook_queen, checked, king_to_get_checked_by, break_out)
                    if break_out == True: break
            if i == 3:
                # Check for Left direction
                stretch_sign_inverter = -1
                while check_in_bounds_single(numeric_notation_first_int - stretch) and current_gameBoard[numeric_notation_second_int][numeric_notation_first_int - stretch] in queen_or_rook_ckecked:
                    checked,stretch, break_out = rook_or_queen(i, stretch, stretch_sign_inverter, current_gameBoard, numeric_notation_first_int, numeric_notation_second_int, rook_queen, checked, king_to_get_checked_by, break_out)
                    if break_out == True: break
        #Check if it is checked by a bishop or a queen
        for k in range (0,4):
            stretch = 1
            if k == 0:
                # Check for Up-Right direction
                stretch_sign_inverter =-1
                stretch_sign_inverter2 = 1
                checked,stretch=bishop_or_queen(checked, numeric_notation_first_int, numeric_notation_second_int, stretch, stretch_sign_inverter, stretch_sign_inverter2, current_gameBoard, queen_or_bishop_checked, bishop_queen, king_to_get_checked_by)
            if k ==1:
                # Check for Down-Right direction
                stretch_sign_inverter = 1
                stretch_sign_inverter2 = 1
                checked,stretch=bishop_or_queen(checked, numeric_notation_first_int, numeric_notation_second_int, stretch, stretch_sign_inverter, stretch_sign_inverter2, current_gameBoard, queen_or_bishop_checked, bishop_queen, king_to_get_checked_by)
            if k == 2:
                # Check for Down-Left direction
                stretch_sign_inverter = 1
                stretch_sign_inverter2 = -1
                checked,stretch=bishop_or_queen(checked, numeric_notation_first_int, numeric_notation_second_int, stretch, stretch_sign_inverter, stretch_sign_inverter2, current_gameBoard, queen_or_bishop_checked, bishop_queen, king_to_get_checked_by)
            if k == 3:
                # Check for Up-Left direction
                stretch_sign_inverter = -1
                stretch_sign_inverter2 = -1
                checked,stretch=bishop_or_queen(checked, numeric_notation_first_int, numeric_notation_second_int, stretch, stretch_sign_inverter, stretch_sign_inverter2, current_gameBoard, queen_or_bishop_checked, bishop_queen, king_to_get_checked_by)
        
        # Check if checked by a pawn
        if check_in_bounds(numeric_notation_first_int+1, numeric_notation_second_int+pawn_check_one):
            if current_gameBoard[numeric_notation_second_int+pawn_check_one][numeric_notation_first_int+1] == pawn_to_be_checked_by:
                checked = True
        # Check for checking with pawn to the right
        if check_in_bounds(numeric_notation_first_int-1, numeric_notation_second_int+pawn_check_one):
            if current_gameBoard[numeric_notation_second_int+pawn_check_one][numeric_notation_first_int-1] == pawn_to_be_checked_by:
                checked = True
    # Resetting the castling variables
    CASTLING_K = False
    CASTLING_Q = False
    return checked

'''
DESCRIPTION: This function will print the gameBoard in nice manner.
PRECONDITION: GameBoard needs to be passed.
POSTCONDITION: GameBoard is printed to the console.
'''
def print_gameBoard(gameBoard):
  for row in range(0,8):
    if row == 0:
        print("   +----+---+---+---+---+---+---+---+")
    for column in range(0,8):
        if column == 0:
            print(8-row, " |",gameBoard[row][column] + " | ", end="")
        elif column == 7:
            print(gameBoard[row][column] + " | ", end="\n")
        else:
            print(gameBoard[row][column] + " | ", end="")
    print("   +----+---+---+---+---+---+---+---+")
  print("     a    b   c   d   e   f   g   h   ")
  print()

'''
DESCRIPTION: This function will force the game to think faster about making moves.
PRECONDITION: Speed needs to be passed.
POSTCONDITION: Returning the status for the games speed of making moves..
'''
def speed_of_thinking(brzina):
  if brzina == 1:
    return "Normal Speed of Thinking."
  elif brzina == 2:
    return "You need to be making moves a little bit faster."
  elif brzina == 3:
    return "You need to be making quick moves now."
  elif brzina == 4:
    return "No thinking anymore, just make moves."
  else:
    return "Too bad."