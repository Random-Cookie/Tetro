# Tetros
An implementation of the game Blockus designed for use both as a command line game and implementation of bots using both
traditional and machine learning algorithms

## Aim
Provide an interface to simulate games, with some basic example players.
This will allow for testing of different types of bots and investigate the best strategies to win.

## Structure
- Game Resources
   - ObjectFactory.py
    Produces shape sets, and groups of players.
   - SimplePlayers.py
   - Move
     Represents information required to make a move
   - Player
     Abstract Class to represent a player, any implementations must implement self.SelectPiece()
   - HumanPlayer
     Provides an interface for humans to play the game
   - RandomPlayer
     Places pieces randomly
   - ExhaustiveRandomPlayer
     Checks all possible moves before retiring
   - Machine Learning Players.py
   - MachineLearningPlayer
     Abstract class to represent a machine learning player
   - Structure.py
   - Piece
     Represents a game piece
   - GameBoard
     Represents the game board
- Driver.py
  - Tetros
    Drives the game and provides menus

### Dependencies
- colorama
- numpy