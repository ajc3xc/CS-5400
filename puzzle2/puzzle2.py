#!/usr/bin/python3
import os, sys
from game_board import game_board
import random
from copy import deepcopy
    
class dungeon_game(game_board):
    def __init__(self):
        input_file_path = sys.argv[1]
        self.output_file_path = sys.argv[2]
        
        #impose max turn limit like morales
        self.MAX_TURN_LIMIT = 7
        
        list_of_lists = []
        with open(input_file_path, 'r') as input_file:
            input_file_list = input_file.read().splitlines()
        
        inputs = input_file_list[0].split()
        rows, cols = int(inputs[0]), int(inputs[1])
            
        #convert input file to list of lists
        input_file_grid = []
        for line in input_file_list:
            input_file_grid.append(list(line))
        
        #get section of map within bounds
        grid = input_file_grid[1:1+rows][:cols]
    
        super().__init__(grid=grid, turn_count=0, points=50)
        #records history of moves made
        self.moves = ''
        
        #variable to store set of moves actman should make,
        #so he either wins or stays alive the longest
        #If a winning moveset is found, then the moves made will be that
        #Otherwise a moveset is found that keeps actman 7 turns, then that will be used
        #Else, bfs will be done each turn until actman dies
        self.moveset = None
    
    #prints current state in game in manner similar to output file
    def _output_final_game_state(self):
        self._update_board()
        with open(self.output_file_path, 'w') as output_file:
            output_file.write(f"{self.moves}\n")
            output_file.write(f"{self.points}\n")
            for line in self.grid:
                output_file.write(f"{''.join(line)}\n")
                   
    def _choose_and_move_actman(self):
        valid_options = self._get_valid_options(self.act_man)

        #data structure to store queue of options
        queue = [{'initial_move': option, 'current_move': option, 'game_board': game_board(grid=self.grid, turn_count=0, points=self.points, moves=self.moves)} for option in valid_options]

        #variable storing which move to make
        selected_option = None
        
        #did we already find a decent or winning moveset with bfs?
        #i.e. win or keep alive 7 turns.
        #this way, actman wins or stays alive as long as he can
        if self.moveset:
            print(f"doing moveset {self.moveset}")
            selected_option = self.moveset[0]
            #if the move is a number, convert the selected option to a digit
            #moveset is stored as a string
            if selected_option.isdigit():
                selected_option = int(selected_option)
            
            #pop first character from moveset string
            if len(self.moveset) > 1:
                self.moveset = self.moveset[1:]
            else:
                self.moveset = None
            
        #good moveset wasn't found
        else:        
            #iterate through the loop until goal condition met or queue becomes empty
            #It takes a LONG time to play the entire game because of this.
            while queue:
                state: dict = queue.pop(0)
                #move act man and move the monsters
                state['game_board']._move_actman(state['current_move'])
                state['game_board']._move_monsters()
                #increment turn count by 1
                state['game_board'].turn_count += 1

                #did act man die from doing this action?
                if state['game_board'].game_state == "defeat":
                    continue
                #did act man kill all the monsters (thereby winning)?
                elif state['game_board'].game_state == "victory":
                    print(f"Found winning moveset {state['game_board'].moves}")
                    #Since we deepcopy our current game state into the array,
                    #we need to filter out the first x moves actman has already made                    
                    #if more than 1 move needed to win, create winning moveset
                    #since we already make a move here, we have to get the moveset len - 1
                    if len(state['game_board'].moves[len(self.moves):]) > 1:
                        self.moveset = state['game_board'].moves[len(self.moves)+1:]
                    selected_option = state['initial_move']
                    break
                #is act man still alive after 7 turns (i.e. 6 turns plus this one)?
                #in case we aren't able to find a series of winning moves within 7 turns,
                #get the last option where he survives 7 moves
                elif state['game_board'].turn_count >= self.MAX_TURN_LIMIT:
                    if not selected_option:
                        #same thing as above
                        #but we want to keep actman alive if there is a moveset > 7
                        if len(state['game_board'].moves[len(self.moves):]) > 1:
                            self.moveset = state['game_board'].moves[len(self.moves)+1:]
                        selected_option = state['initial_move']
                #Turn count for this move wasn't more than 7, and it wasn't victory or defeat
                #keep adding the moves to the queue
                #get valid new options from this position, add to tail end of new options queue
                else:
                    valid_new_options = state['game_board']._get_valid_options(state['game_board'].act_man)
                    new_branch = [{"initial_move": state['initial_move'], "current_move": new_option, 'game_board': deepcopy(state['game_board'])} for new_option in valid_new_options]
                    queue.extend(new_branch)

            #contingency if queue becomes empty and winning moveset not found
            else:
                print("No winning moveset found.")
                #if there is no moveset where he survives 7 moves, make a random move
                if not selected_option:
                    print("No option found where actman survives 7 turns. Moving randomly.")
                    selected_option = random.choice(valid_options)
                else:
                    print(f"doing moveset {self.moveset}")

        self._move_actman(move=selected_option)         
    
    def _play_turn(self):    
        #not sure if sys exiting will cause an error in the program
        #so, I'm being safe and using multiple return checks only
        
        #decrease points by 1, check if points <= 0
        #if <= 0, kill Act-Man and exit game
        #since 'game ends' when score <= 0, I'm default to saying act man dies
        if self.points <= 0:
            self._kill_actman()
        #game end check
        if self.game_state != "playing": return
        
        #increment turn count pre_emptively,
        #in case act man killed by demons or demons get killed
        self.turn_count += 1
        #move act man
        self._choose_and_move_actman()
        if self.game_state != "playing": return
        
        #move the monsters
        self._move_monsters()
        
        #initial state should already be printed
        #prints the game state at the end of each turn
        print()
        print(f"End of Turn {self.turn_count}")
        self._pprint_game_state()
        #exit out of the loop since you won the game
        
    
    #the 'main' function
    def play_game(self):
        print("Initial Board State")
        self._pprint_game_state()
        print()
        
        while self.game_state == "playing":
            self._play_turn()
            #comment / remove break to run full game
            if self.turn_count >= self.MAX_TURN_LIMIT: break
            #break
        
        #print game state for last turn
        print() 
        print(f"Final Board State: End of Turn {self.turn_count}")
        self._pprint_game_state()
        
        
        self._output_final_game_state()
        print("Game Completed!")
    

new_dungeon = dungeon_game()
new_dungeon.play_game()
#new_dungeon._play_turn()
