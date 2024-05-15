#!/usr/bin/python3
from dataclasses import dataclass, fields

#I'm stupid, so putting this in here for safety reasons
@dataclass
class StrictDataClass:
    def __post_init__(self):
        # This loop sets up an initial check and creation of attributes defined in the dataclass
        for field in fields(self):
            setattr(self, field.name, getattr(self, field.name))
    
    def __setattr__(self, key, value):
        if key not in {field.name for field in fields(self)}:
            raise AttributeError(f"Cannot add new field {key}")
        super().__setattr__(key, value)

@dataclass
class character(StrictDataClass):
    current_position: tuple
    #movement options are ordered clockwise
    movement_options=[8, 9, 6, 3, 2, 1, 4, 7]
    #dictionary for where to move actman based on action
    #ordered clockwise starting from north
    #south: (1, 0), north (-1, 0), east (0, 1), west (0, -1)
    movement_translator = {8: (-1, 0), 9: (-1, 1), 6: (0, 1), 3: (1, 1), 2: (1, 0), 1: (1, -1), 4: (0, -1), 7: (-1, -1)}
    mark_for_death=False

@dataclass 
class monster(character):
    monster_type: chr
    
@dataclass
class act_man(character):
    bullet_options = ['N', 'S', 'E', 'W']
    fired_bullet: bool = False
    is_alive: bool = True