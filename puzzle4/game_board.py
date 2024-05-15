#!/usr/bin/python3
from character import character, monster, act_man
from typing import Tuple, List
from math import sqrt
from copy import deepcopy

#game state class to store temporary boards for bfs
#need to have everything to move the board independently of act man making a decision to move
class game_board():
    def __init__(self, grid: List[List]=None, turn_count: int=0, points: int=50, moves: str=''):    
        self.grid = deepcopy(grid)
        self.turn_count = turn_count
        #keep track of current game state
        #victory, defeat or playing. Used for BFS
        self.game_state = "playing"
        self.points = points
        self.monsters_killed = 0
        self.corpse_count = 0
        self.moves = moves
        self.act_man = None
        self.monsters = {}
        monsters_index = 0
        #iterate through matrix, determine monsters and actman positions     
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] == 'A':  self.act_man = act_man((i, j), fired_bullet=False, is_alive=True)
                elif self.grid[i][j] == 'G':
                    self.monsters[monsters_index] = monster((i, j), 'G')
                    monsters_index += 1
                elif self.grid[i][j] == 'D':
                    self.monsters[monsters_index] = monster((i, j), 'D')
                    monsters_index += 1
                elif self.grid[i][j] == '@':
                    self.corpse_count += 1
    
                
    #debugging function for seeing current board state
    def _pprint_game_state(self):
        self._update_board()
        print(f"Moves: {self.moves}")
        print(f"Points: {self.points}")
        for line in self.grid:
            print(''.join(line))
    
    #function to update board state after pieces have been moved
    #only update the board when it is being looked it
    #i.e. printed or outputted to a file
    def _update_board(self):
        # Replace 'A', 'G', 'D' with '  ' using a nested list comprehension
        self.grid = [[' ' if element in ['A', 'G', 'D'] else element for element in line] for line in self.grid]
        
        #show all living demons' positions on the board (will be alive if in list)
        for monster in self.monsters.values(): self.grid[monster.current_position[0]][monster.current_position[1]] = monster.monster_type
        
        #show act man's current position on board if he's alive
        #if a demon is in the same position as act man, then act man's dead X should show over the demon
        if self.act_man.is_alive: self.grid[self.act_man.current_position[0]][self.act_man.current_position[1]] = 'A'
        else: self.grid[self.act_man.current_position[0]][self.act_man.current_position[1]] = 'X'
        return
    
    #For the heuristic, you're greedily choosing the action that gets the most amount of points
    #heuristic for how many points in total you will gain / lose by doing this action
    def get_cost(self):
        #approximately how much has your points increased / decreased since the start?
        #since actman loses 20 points when he fires a bullet, he also doesn't lose a point by moving, thus total cost ~= this formula
        #I'm also heavily biasing the points calculation to go for shorter games, that way the max amount of points gets increased
        points_delta = (5 * self.monsters_killed) - 5 * len(self.moves) - (19 * self.act_man.fired_bullet)
        return points_delta
    
    #'waste management' function
    def _kill_monster(self, monster_index):
        initial_length = len(self.monsters)
        #replace the monster in the grid with a corpse, delete from list of monsters
        monster_row, monster_col = self.monsters[monster_index].current_position
        self.grid[monster_row][monster_col] = '@'
        del self.monsters[monster_index]
        #print(f"{self.moves} {initial_length} {len(self.monsters)}")
        #five points gained if monster is killed
        self.points += 5
        self.monsters_killed += 1
        self.corpse_count = 1

        #check if there are any monsters left after you killed a monster
        #also make sure that you didn't kill act man first
        if not self.monsters and self.act_man.is_alive:
            self.game_state = "victory"
        
    def _move_monsters(self):
        #quick utility function
        def euclidean_distance(coord1: Tuple[int], coord2: Tuple[int]):
            return sqrt((coord2[0] - coord1[0])**2 + (coord2[1] - coord1[1])**2)
        
        #move the monsters one at a time
        monsters_to_remove = []
        for index, monster in self.monsters.items():
            valid_options = self._get_valid_options(monster)
            #iterate until you get the minimum value(s)
            minimum_distance = float('inf') #set minimum distance to the max value
            minimum_values = []
            for option in valid_options:
                potential_move = tuple(sum(values) for values in zip(monster.current_position, monster.movement_translator[option]))
                act_man_distance = euclidean_distance(potential_move, self.act_man.current_position)
                if act_man_distance < minimum_distance:
                    minimum_values = [option]
                    minimum_distance = act_man_distance
                elif act_man_distance == minimum_distance:
                    minimum_values.append(option)
            
            selected_move = None
            #if there is a tie, then get the minimum values

            #basic assertion protection (check that value(s) were selected, monster type is ogre or demon)
            assert minimum_values, f"No valid moves for monster {monster}"
            assert monster.monster_type in ['G', 'D'], f"{monster} isn't a demon or ogre"
            if 8 in minimum_values: selected_move = 8
            #since the minimum values should be ordered clockwise (with no 8s)
            #all we have to do is the first (ogre), or the last (demon)
            elif monster.monster_type == 'G':
                selected_move = minimum_values[0]
            elif monster.monster_type == 'D':
                selected_move = minimum_values[-1]
            #move monster to new selected position
            monster.current_position = tuple(sum(values) for values in zip(monster.current_position, monster.movement_translator[selected_move]))
            #check if any monsters, corpses or actman are in the new position
            #moved into act man
            if self.act_man.current_position == monster.current_position:
                self._kill_actman()
                return
            #moved into corpse
            #because I can't delete the monster
            elif self.grid[monster.current_position[0]][monster.current_position[1]] == '@': monsters_to_remove.append(index)
            
        #delete all monsters that hit a corpse
        [self._kill_monster(index) for index in monsters_to_remove]
        monsters_to_remove = []
        
        
        #once you finished moving the monsters, check if they've finished in the same place
        #moved into another monster
        #sinces self.monsters is a dictionary, each item in the dictionary has a constant index
        for index, monster in self.monsters.items():
            for check_index, check_monster in self.monsters.items():
                if monster.current_position == check_monster.current_position and check_index != index:
                    if index not in monsters_to_remove:
                        monsters_to_remove.append(index)
                    if check_index not in monsters_to_remove:
                        monsters_to_remove.append(check_index)
        
        #delete all monsters that are in the same collision space
        [self._kill_monster(index) for index in monsters_to_remove]

        #check that actman's score is >= 0 at the end of a turn
        #this is built into monsters function because of bfs
        #since 'game ends' when score <= 0, I'm default to saying act man dies
        if self.points <= 0:
            self._kill_actman()

    
    #function to kill act man
    def _kill_actman(self):
        self.points = 0
        #the game logic for showing the pieces is probably the most error prone
        #I just don't care now
        self.act_man.is_alive = False
        self.grid[self.act_man.current_position[0]][self.act_man.current_position[1]] = 'X'
        #if act man dies, the game is lost
        self.game_state = "defeat"
    
    #function to pick a valid move at random 
    def _get_valid_options(self, character: character):
        valid_movements = []
        #start coordinate[0] is row, start_coordinate[1] is column
        #have safety to ensure that you can't go out of bounds
        #I'm going to be cheap and check that you aren't along the edge of the game
        #(i.e. 0 or n -1 for row or column). Also assume list of lists is rectangular    
        assert character.current_position[0] > 0 and character.current_position[0] < len(self.grid) - 1 and character.current_position[1] > 0 and character.current_position[1] < len(self.grid[0]) - 1,\
            f"{character.current_position} is out of bounds!"
            
        valid_options = []
        #add valid movements to list
        #i.e. ones that are not a wall
        for key, movement in character.movement_translator.items():
            if self.grid[character.current_position[0] + movement[0]][character.current_position[1] + movement[1]] != '#':
                valid_options.append(key)
        
        #safety check (ensure there is at least 1 valid movement)
        assert valid_options, "No valid movements found"
        
        #actman only
        #can only fire bullet once
        if isinstance(character, act_man) and not character.fired_bullet:
            valid_options += character.bullet_options
        
        return valid_options
    
    #assume direction is N, S, E or W
    def _fire_bullet(self, direction):
        act_man_row, act_man_col = self.act_man.current_position[0], self.act_man.current_position[1]
        if direction == 'N':
            row_range = list(range(act_man_row - 1, -1, -1))
            col_range = [act_man_col]
        elif direction == 'S':
            row_range = range(act_man_row + 1, len(self.grid))
            col_range = [act_man_col]
        elif direction == 'W':
            row_range = [act_man_row]
            col_range = range(act_man_col - 1, -1, -1)
        elif direction == 'E':
            row_range = [act_man_row]
            col_range = range(act_man_col + 1, len(self.grid[0]))
        
        #20 points lost when bullet is fired
        self.points -= 20
        #since break only gets out of one loop, returning immediately will be necessary   
        indeces_to_remove = []
        stop = False #variable to exit out of both inner and outer for loop
        
        #move the death beam until it hits a wall, kill any monsters in the way
        for row in row_range:
            if stop: break
            for col in col_range:
                if self.grid[row][col] == '#':
                    stop = True
                    break
                #check if monster in cell
                #at most there should only be 1 monster in a cell
                for index, monster in self.monsters.items():
                        if monster.current_position == (row, col):
                            indeces_to_remove.append(index)
                            break
        
        #kill all the monsters hit by a bullet
        #initial_length = len(self.monsters)
        [self._kill_monster(index) for index in indeces_to_remove]

        #can only fire bullet once
        self.act_man.fired_bullet = True
    
    def _move_actman(self, move: str=None):
        #ensure the move selected is valid
        valid_options = self._get_valid_options(self.act_man)
        assert move in valid_options,   f"{move} not in valid options {valid_options}"
        
        #add moves to string of all moves made
        self.moves += str(move)
        #fire a bullet if a selection to fire the bullet was made. Otherwise, move act man
        if move in self.act_man.bullet_options:
            self._fire_bullet(move)
        else:
            #update act man's position
            self.act_man.current_position = tuple(sum(values) for values in zip(self.act_man.current_position, self.act_man.movement_translator[move]))
            #check if there's a monster or a corpse there
            #assume that corpses are static and can't move
            #since act man's points will be set to 0 if he dies, subtracting points will make the result negative
            if any(monster.current_position == self.act_man.current_position for monster in self.monsters.values()) or self.grid[self.act_man.current_position[0]][self.act_man.current_position[1]] == '@':
                self._kill_actman()
            else:
                self.points -= 1
