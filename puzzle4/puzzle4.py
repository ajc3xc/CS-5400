#!/usr/bin/python3
import os, sys
from game_board import game_board
import random
from copy import deepcopy
import heapq
    
class dungeon_game(game_board):
    def __init__(self):
        input_file_path = sys.argv[1]
        self.output_file_path = sys.argv[2]
        
        list_of_lists = []
        with open(input_file_path, 'r') as input_file:
            input_file_list = input_file.read().splitlines()
        
        #get how many rows and columns the grid is
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
                   
    def _act_man_astar_search(self):
        valid_options = self._get_valid_options(self.act_man)

        #data structure to store priority queue of options
        #number at the beginning is the current estimated cost
        initial_options = [{'initial_move': option, 'current_move': option, 'game_board': game_board(grid=self.grid, turn_count=0, points=self.points, moves=self.moves)} for option in valid_options]
        
        #simulate each option, calculate each score
        #new cost is total delta in number of points from the start,
        #weighted so that act man movement decrease the points 5x what they normally do
        #positive or negative for the previous turn
        #Since sub-optimal solutions aren't needed for full points,
        #I am using a very simple greedy algorithm to get the job done.
        id = 0
        def calculate_heuristic(option):
            #simulate a turn
            option['game_board']._move_actman(option['current_move'])
            option['game_board']._move_monsters()
            option['game_board'].turn_count += 1
            
            #calculate the estimated score as an inverse cost
            predicted_score = option['game_board'].get_cost()
            
            #generate unique id for this cost, because sometimes the cost may be the same
            nonlocal id
            id += 1
            
            return (-predicted_score, id, option)
        
        #heapq will blow up if your cost is 0, since it will directly compare the dictionary (VERY BAD)
        priority_queue = [calculate_heuristic(option) for option in initial_options]
        heapq.heapify(priority_queue)

        #variable storing which move to make
        selected_option = None
        
        #did we already find a decent or winning moveset with heuristic?
        #i.e. moves to make to win
        #only calculates correct moveset once
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
            #depth limit set at 10 so the heuristic can get done in a reasonable amount of time
            depth_limit = 10
            #don't continue to iterate if we found solution or hit the depth limit
            while priority_queue:
                #since the state has already ran a turn, all I need to do now is check for defeat, victory or neither
                state = heapq.heappop(priority_queue)[-1]
                
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
                    if len(state['game_board'].moves) > 1:
                        self.moveset = state['game_board'].moves[1:]
                    selected_option = state['initial_move']
                    break
                #don't explore options deeper than depth limit
                elif state['game_board'].turn_count < depth_limit:                 
                    #get valid options for this branch, move onto priority queue
                    #since we are using a minheap as the default data structure, the costs must be negated to function as a max heap
                    valid_new_options = state['game_board']._get_valid_options(state['game_board'].act_man)
                    new_branch = [{"initial_move": state['initial_move'], "current_move": new_option, 'game_board': deepcopy(state['game_board'])} for new_option in valid_new_options]
                    
                    #push them one at a time since eventually the heap will get very large
                    #need unique identifier for each item in case costs are the same
                    #also calcualte heuristic while pushing them because I can
                    [heapq.heappush(priority_queue, calculate_heuristic(option)) for option in new_branch]
                                        
            #contingency if queue becomes empty and winning moveset not found
            else:
                print("No winning moveset found. Moving randomly")
                selected_option = random.choice(valid_options)    

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
        self._act_man_astar_search()
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
