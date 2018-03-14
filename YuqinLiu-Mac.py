#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 23:12:22 2018

@author: liuyuqin
"""

from collections import defaultdict

rows='ABCDEFGHI'
cols='123456789'

def cross(a, b):
    return[s+t for s in a for t in b]

def diagonal(a, b):
    for s in a:
        for t in b:
            if (a.find(s))==(b.find(t)):
                return[s+t]
            if ((a.find(s)+b.find(t))==10):
                return[s+t]

boxes=[r+c for r in rows for c in cols]
history={}
row_units=[cross(r,cols) for r in rows]
column_units=[cross(rows,c) for c in cols]
square_units=[cross(rs,cs) for rs in ('ABC','DEF','GHI') for cs in ('123'
              ,'456''789')]
diagonal_units=[cross(a,b) for a,b in zip(rows,cols) for a,b in zip(rows,cols[::-1])]
unitlist=row_units+column_units+square_units+diagonal_units


def extract_units(unitlist, boxes):
    units=defaultdict(list)
    for current_box in boxes:
        for unit in unitlist:
            if current_box in unit:
                # defaultdict avoids this raising a KeyError when new keys are added
                units[current_box].append(unit)
    return units

units=extract_units(unitlist, boxes)

def extract_peers(units, boxes):
    """Initialize a mapping from box names to a list of peer boxes (i.e., a flat list
    of boxes that are in a unit together with the key box)

    Parameters
    ----------
    units(dict)
        a dictionary with a key for each box (string) whose value is a list
        containing the units that the box belongs to (i.e., the "member units")

    boxes(list)
        a list of strings identifying each box on a sudoku board (e.g., "A1", "C7", etc.)

    Returns
    -------
    dict
        a dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)
    """
    # the value for keys that aren't in the dictionary are initialized as an empty list
    peers = defaultdict(set)  # set avoids duplicates
    for key_box in boxes:
        for unit in units[key_box]:
            for peer_box in unit:
                if peer_box != key_box:
                    # defaultdict avoids this raising a KeyError when new keys are added
                    peers[key_box].add(peer_box)
    return peers

peers=extract_peers(units, boxes)

def assign_value(values, box, value):
    """You must use this function to update your values dictionary if you want to
    try using the provided visualization tool. This function records each assignment
    (in order) for later reconstruction.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    prev = values2grid(values)
    values[box] = value
    if len(value) == 1:
        history[values2grid(values)] = (prev, (box, value))
    return values

def values2grid(values):
    """Convert the dictionary board representation to as string

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    """
    res = []
    for r in rows:
        for c in cols:
            v = values[r + c]
            res.append(v if len(v) == 1 else '.')
    return ''.join(res)

def grid2values(grid):
    """Convert grid into a dict of {square: char} with '123456789' for empties.

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    
    Returns
    -------
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    sudoku_grid = {}
    for val, key in zip(grid, boxes):
        if val == '.':
            sudoku_grid[key] = '123456789'
        else:
            sudoku_grid[key] = val
    return sudoku_grid
    

def display(values):
    """Display the values as a 2-D grid.

    Parameters
    ----------
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print()
    
def reconstruct(values,history):
    path=[]
    prev=values2grid(values)
    while prev in history:
        prev,step=history[prev]
        path.append(step)
    return path[::-1]


def grid_value(grid):
    chars=[]
    digits='123456789'
    for c in grid:
        if c=='.':
            chars.append(digits)
        if c in digits:
            chars.append(c)
    assert len(chars)==81
    return dict(zip(boxes, chars))

def eliminate(values):
    solved_values=[box for box in values.keys() if len(values[box])==1]
    for box in solved_values:
        digit=values[box]
        for peer in peers[box]:
            values[peer]=values[peer].replace(digit,'')
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces=[box for box in unit if digit in values[box]]
            if len(dplaces)==1:
                values[dplaces[0]]=digit
    return values

def reduce_puzzle(values):
    stalled=False
    while not stalled:
        #Check how many boxes have a determined value
        solved_values_before=len([box for box in values.keys() if len(values[box])==1])
        values=eliminate(values)
        values=only_choice(values)
        solved_values_after=len([box for box in values.keys() if len(values[box])==1])
        #if no new values added, stop the loop
        stalled=solved_values_after==solved_values_before
        #Sanity check, return false if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box])==0]):
            return False
    return values

def search(values):
    #Using depth-first search and propagation, create a search tree and solve the soduku.
    #First, reduce the puzzle using the previous function
    values=reduce_puzzle(values)
    if values==False:
        return False
    if all(len(values[s])==1 for s in boxes):
        return values
    
    #Choose one of the unfilled squares with the fewesr possibilities
    n,s=min((len(values[s]),s) for s in boxes if len(values[s])>1)
    #Now use recursion to solve each one of the resulting sodukus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_soduku=values.copy()
        new_soduku[s]=value
        attempt=search(new_soduku)
        if attempt:
            return attempt
        
def naked_twins(values):
    twin_solved=False
    while not twin_solved:
        solved_values_before=[box for box in values.keys() if len(values[box])==2]
        for box in solved_values_before:
            digit=values[box]
            for s in peers[box]:
                if (len(s)==2 and values[s]==digit):
                    peer=[rest for rest in peers[box] for rest in peers[s]]
                    values[peer]=values.peer.replace(digit,'')
        solved_values_after=len([box for box in values.keys() if len(values[box])==2])
        twin_solved=len(solved_values_before)==solved_values_after
        if len([box for box in values.keys() if len(values[box])==0]):
            return False
    return values
                    

def solve(grid):
    values=grid2values(grid)
    values=search(values)
    return values

if __name__=="__main__":
    diag_sodoku_grid='2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sodoku_grid))
    result=solve(diag_sodoku_grid)
    display(result)
    
    try: 
        import PySudoku
        PySudoku.play(grid2values(diag_sodoku_grid), result, history)
    
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to pygame issue. Not a problem! It is not a requirement!')
    
    