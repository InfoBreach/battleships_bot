# Battleships Game

A Python-based Battleships implementation featuring an bot opponent and an interface.


## Overview
This project is an interactive implementation of the Battleships game, developed in Python using CustomTkinter for the interface and NumPy for grid management.

The application includes a player-versus-bot system in which the bot uses probability-based analysis and targeted search strategies to make informed decisions rather than relying on random selection.

## Extra Features
- Automatic ship placement
- Auto-attack, auto replay mode
- Real-time heatmap visualization of the bot's decisions
- Turn tracking and win/loss detection

## Requirements
Ensure Python 3.10 or later is installed.

### Dependencies:
 - numpy 
 - customtkinter

## Gameplay Instructions
### Ship Placement Phase
Select grid cells to position ships. Use the orientation button to switch between horizontal and vertical placement. Confirm placement before proceeding.

* Alternatively, use the automatic placement feature.

<img width="583" height="465" alt="image" src="https://github.com/user-attachments/assets/250cfd5d-9245-42f6-85f3-995ffc6deefb" />


## Attack Phase
Select a target cell.
Confirm the attack to execute the move.
The bot will respond immediately.

<img width="950" height="469" alt="image" src="https://github.com/user-attachments/assets/2eb144fe-0e95-4d3d-8951-06475c09e003" />


## Objective
Sink all enemy ships to win.

The game ends when either the player or the AI loses all ships.

## Bot's algorithm
The bot operates using two complementary strategies:

### Scan Mode
Generates a probability heatmap based on all valid ship placements.

Then Selects cells with the highest probability of containing a ship.

<img width="331" height="343" alt="image" src="https://github.com/user-attachments/assets/50ee3765-f016-45dd-9c3c-faf6616b2ea8" />
<img width="334" height="334" alt="image" src="https://github.com/user-attachments/assets/d56a0c56-3697-4497-b826-dde1b3f0ecda" />


### Hunt Mode
Will be switch over after a successful hit. Targets adjacent cells to locate the rest of the ship. Will focus the next attack with a direction when multiple hits are aligned. This will switch off if a ship is sunk.

<img width="326" height="325" alt="image" src="https://github.com/user-attachments/assets/e62f9ba5-7283-4887-ae79-24a9f93a1de6" />
<img width="333" height="328" alt="image" src="https://github.com/user-attachments/assets/f2a1eb05-659e-40e2-b2b7-6d024b9918f7" />
<img width="334" height="328" alt="image" src="https://github.com/user-attachments/assets/1f24bead-368b-4684-8e22-88dba391d082" />


#### For more info, look inside the Flowchart folder.
![Flowchart](flowchart/)

### Changes:
- Can now find all ships in a cluster, no more adjacent ship problems.
- auto replay for display

## Contributers:
Tran Thien Khanh - 11525082 , Nguyen Cong Gia Tri - 11525064

## Inspiration:
http://www.datagenetics.com/blog/december32011/
