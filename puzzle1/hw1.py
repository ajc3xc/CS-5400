#!/usr/bin/python3
import os, sys
from character import character, monster, act_man
from typing import Tuple
from math import sqrt
import random


class dungeon_game():
    def __init__(self):
        input_file_path = sys.argv[1]
        self.output_file_path = sys.argv[2]
        
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
        self.grid = input_file_grid[1:1+rows][:cols]
    
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

        #game status variables
        self.playing = True
        self.points = 50
        self.moves = ''
        self.turn_count = 0
    
    #prints current state in game in manner similar to output file
    def _output_final_game_state(self):
        with open(self.output_file_path, 'w') as output_file:
            output_file.write(f"{self.moves}\n")
            output_file.write(f"{self.points}\n")
            for line in self.grid:
                output_file.write(f"{''.join(line)}\n")
            
    def _pprint_game_state(self):
        self._update_board()
        print(self.moves)
        print(self.points)
        for line in self.grid:
            print(''.join(line))
    
    #function to update board state after pieces have been moved
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
    
    #function to kill act man
    def _kill_actman(self):
        self.points = 0
        #the game logic for showing the pieces is probably the most error prone
        #I just don't care now
        self.act_man.is_alive = False
        self._update_board()
        self.playing = False
    
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
        indexes_to_remove = []
        stop = False #variable to exit out of both inner and outer for loop
        
        for row in row_range:
            if stop: break
            for col in col_range:
                #print((row, col))
                if self.grid[row][col] == '#':
                    stop = True
                    break
                #check if monster in cell
                monster_types = ['D', 'G']
                if self.grid[row][col] in monster_types:
                    for index, monster in self.monsters.items():
                        if monster.current_position == (row, col):
                            indexes_to_remove.append(index)
        #can't fire any more bullets
        map(self._kill_monster, indexes_to_remove)
        self.act_man.fired_bullet = True
                   
    def _move_actman(self):
        valid_options = self._get_valid_options(self.act_man)
        
        #select an item from the valid options randomly
        selected_option = random.choice(valid_options)
        
        self.moves += str(selected_option)
        if selected_option in self.act_man.bullet_options:
            self._fire_bullet(selected_option)
        else:
            #update act man's position
            self.act_man.current_position = tuple(sum(values) for values in zip(self.act_man.current_position, self.act_man.movement_translator[selected_option]))
            #check if there's a monster or a corpse there
            #assume that corpses are static and can't move
            if any(monster.current_position == self.act_man.current_position for monster in self.monsters.values()) or self.grid[self.act_man.current_position[0]][self.act_man.current_position[1]] == '@':
                self._kill_actman()
            else:
                self.points -= 1
    
    def _kill_monster(self, monster_index):
        print(".")
        monster_row, monster_col = self.monsters[monster_index].current_position
        self.grid[monster_row][monster_col] = '@'
        del self.monsters[monster_index]
        #five points gained if monster is killed
        self.points += 5
        
    def _move_monsters(self):
        #quick utility function
        def euclidean_distance(coord1: Tuple[int], coord2: Tuple[int]):
            return sqrt((coord2[0] - coord1[0])**2 + (coord2[1] - coord2[1])**2)
        
        #move the monsters one at a time
        monsters_to_remove = []
        for index, monster in self.monsters.items():
            valid_options = self._get_valid_options(monster)
            #print(valid_options)
            #iterate until you get the minimum value(s)
            minimum_distance = float('inf') #set minimum distance to the max value
            minimum_values = []
            for option in valid_options:
                potential_move = tuple(sum(values) for values in zip(monster.current_position, monster.movement_translator[option]))
                act_man_distance = euclidean_distance(potential_move, self.act_man.current_position)
                if act_man_distance < minimum_distance:
                    minimum_values = [option]
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
            #print(selected_move)
            #print(monster.current_position)
            #move monster to new selected position
            monster.current_position = tuple(sum(values) for values in zip(monster.current_position, monster.movement_translator[selected_move]))
            
            #check if any monsters, corpses or actman are in the new position
            #moved into act man
            if self.act_man.current_position == monster.current_position: self._kill_actman()
            #moved into corpse
            #because I can't delete the monster
            elif self.grid[monster.current_position[0]][monster.current_position[1]] == '@': monsters_to_remove.append(index)
            
        #delete all monsters that hit a corpse
        if monsters_to_remove: print(monsters_to_remove)
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
                        
            
            
                
    
    def _play_turn(self):    
        #not sure if sys exiting will cause an error in the program
        #so, I'm being safe and using multiple return checks only
        
        #decrease points by 1, check if points <= 0
        #if <= 0, kill Act-Man and exit game
        if self.points <= 0:
            self._kill_actman()
        #game end check
        if not self.playing: return
        
        #increment turn count pre_emptively,
        #in case act man killed by demons or demons get killed
        self.turn_count += 1
        #move act man
        self._move_actman()
        if not self.playing: return 
        
        #move the monsters
        self._move_monsters()
        
        #initial state should already be printed
        #prints the game state at the end of each turn
        print(f"End of Turn {self.turn_count}")
        self._pprint_game_state()
        #exit out of the loop since you won the game
        if not self.monsters:
            self.playing = False
        
    
    #the 'main' function
    def play_game(self):
        print("Initial Board State")
        self._pprint_game_state()
        
        while self.playing:
            self._play_turn()
            #comment / remove break to run full game
            #break
        
        #print game state for last turn   
        print(f"Final Board State: End of Turn {self.turn_count}")
        self._pprint_game_state()
        
        
        self._output_final_game_state()
        print("Game Completed!")
    

new_dungeon = dungeon_game()
new_dungeon.play_game()
#new_dungeon._play_turn()