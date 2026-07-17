[![Open on Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://vscode.dev/github/olimarco/Hidden-Treasures)

# Hidden Treasures

Hidden Treasures is a game developed in Python with a graphical user interface implemented using breezypythongui.  
The game is for two players and is played on a 6×6 grid of facedown cards. Each player must build a hand of 5 cards by managing their action points and using special cards to gain strategic advantages.

Project Author: Marco Oliveri

## Installation

Clone the repository, navigate to the project directory, and install the dependencies:

```bash
pip install pillow pygame
```

or

```bash
uv add pillow pygame
```

## Repository Contents

Main structure of the project:

- main.py  
  Entry point of the project. Displays the main menu, starts a new game, and contains the leaderboard page class.

- hidden_games_gui.py  
  Interface and game logic. Manages rounds, turns, the 6×6 grid, actions, special cards, scores, and the end of the game.

- Card.py  
  Card model, both numeric and special. Manages face-down and permanently revealed states.

- Deck.py  
  Deck creation, shuffling, and drawing of the 36 cards for the grid.

- Player.py  
  Player model. Manages the hand, action points, scores, and the end-of-round state.

- validator.py  
  Evaluation of hand combinations and calculation of the round score. Also handles the Gem (Gemma) card as a wild card for groups.

- LeaderboardManager.py  
  Saves games to a text file and reconstructs the leaderboard with aggregated statistics.

Support folders and files:

- deck_images
  Contains deck images and backgrounds used by the GUI. The game loads images from this folder for the card back, numeric cards, and special cards.

- audio  
  Contains the mp3 file for the background music played on loop in the main menu.

- ranking.txt  
  Automatically created if it does not exist. Contains the history of games in text format.

## Requirements

Recommended Version:

- Python 3.10 or higher

Libraries used:

- breezypythongui
- tkinter
- pillow
- pygame

Note on pillow and pygame:  
Pillow is used to load and resize images. Pygame is used to play the music in the main menu.


## Dependencies

breezypythongui is included in the project or must be made available in the Python Path depending on the repository configuration.

## How to Run

To start the game, run:

```bash
python main.py
```

Upon startup, the main menu will be shown.

## Game Rules

### Overview

- The game is played on a 6×6 grid consisting of 36 facedown cards.  
- Cards are drawn from a deck and laid face down at the beginning of each round.  
- Each round allocates 15 action points to each player.  
- Players take turns revealing a card and choosing an action: Accept, Reject, or Swap.  
- Each player must build a 5-card hand.  
- Round scores accumulate, and the game ends when a player reaches at least 110 points.  

### Numeric Cards

- **Suits**: Spades, Hearts, Diamonds, Clubs   
- **Numeric values**: from 1 to 10  

In the model, there are also values beyond 10 for text representation, but the scoring logic focus is on numeric cards useful for combinations.

### Special Cards

#### Gem 

Acts as a wild card (jolly) only for combinations based on matching values: Pair, Two Pair, Three of a Kind, Full House, and Four of a Kind.  
It cannot complete a Straight, Flush, or Straight Flush.  
This logic is handled in `validator`.

#### Coin 
When accepted, it immediately awards an extra action point to the player.  
This logic is implemented in `hidden_treasures_gui`.

#### Scroll 

When accepted, it allows revealing one facedown card in the grid permanently.  
The card remains visible for the rest of the round and is not automatically assigned to anyone.  
This logic is implemented in `hidden_treasures_gui`.

## Turn Actions

During their turn, a player selects a facedown card on the grid to reveal it, and then chooses one of the available actions:

### Accept 

- **Cost**: 1 action point  
- **Effect**: adds the card to the hand if the hand is not already full  
- Implementation in `hidden_treasures_gui`

### Reject 

- **Cost**: 1 action point  
- **Effect**: the card is turned face down again and is not assigned to anyone  
- Implementation in `hidden_treasures_gui`

### Swap 

- **Cost**: 2 action points  
- **Effect**: swaps the revealed card with a card already in the hand, choosing which card to replace  
- Implementation in `hidden_treasures_gui`

### End Round 

- Available only when the hand is full (5 cards)  
- Allows the player to end their participation in the round, keeping any remaining action points  
- Implementation in `hidden_treasures_gui`

## End of Round

The round ends when both players have finished (called "End of Round") or when both have run out of action points.  
At the end of the round, hands are evaluated and any remaining action points are added to the combination score.

## Combinations and Scores

Combinations award a fixed score, and the final round score is:

`round score = combination score + remaining action points`

### Combination Values

- **Straight Flush**: 100  
- **Four of a Kind (Poker)**: 50  
- **Full House (Full)**: 30  
- **Flush**: 25  
- **Straight**: 20  
- **Three of a Kind (Tris)**: 15  
- **Two Pair**: 10  
- **Pair**: 5  
- **No combination**: 0  

The evaluation logic is implemented in `validator`.

## End of the Game

The game ends when at least one player reaches 110 points or more.  
If both reach the threshold in the same round, the player with the higher score wins.  
If there is still a tie, the player with more remaining action points wins.  
If it is still a tie, the game ends in a draw.  

The game-end logic is implemented in `hidden_treasures_gui`.

## Game Interface

### 6×6 Grid

- Each card on the grid is represented by a button with an image.  
- A card assigned to a player is highlighted in a different color and cannot be selected by the other player.  

Implementation in `hidden_treasures_gui`.

### Info Panel

Displays in real-time:

- current player's turn  
- remaining action points  
- current score  
- number of cards in hand  
- current round  
- timer  

Implementation in `hidden_treasures_gui`.

### Timer

The timer shows the elapsed seconds and is updated periodically during the game.  
Implementation in `hidden_treasures_gui`.

### Menu

The game includes a top menu with options to:

- start a new game  
- open the leaderboard  

Implementation in `hidden_treasures_gui`.

## Leaderboard

### File Persistence

Games are saved in append mode to a text file.  
Each line contains fields separated by a delimiter, including date, duration, rounds, names, scores, final action points, and winner.

### Visualization

The leaderboard screen reads the file, calculates aggregated statistics, and displays:

- sorted leaderboard  
- total games played  
- recent games  

Implementation in `LeaderboardManager`.

## Relevant Implementation Details

### Card State Management

Each `Card` maintains a face-up/face-down state and a permanent revelation flag used by the Scroll.

### Hand Evaluation and Complexity

- The hand is limited to at most 5 cards, so combination checks have a constant cost with respect to the hand size.  
- Value frequency management uses `Counter` and performs operations on very small sets.  

Implementation in `validator`.

### Leaderboard Saving

- If the leaderboard file does not exist, it is created automatically.  
- Reading reconstructs `Game` objects and aggregates statistics by player name.  

Implementation in `LeaderboardManager`.

## Graphical and Audio Resources

### Images

The game uses images for:

- card back  
- numeric cards named using a value-suit convention  
- special cards with lowercase names  

The GUI loads and resizes images at runtime.  
Implementation in `hidden_treasures_gui`.

### Audio

In the main menu, background music starts playing in a loop at a reduced volume.  
Implementation in `main.py`.

## Single Player Mode (Bot AI)

The game includes a Single-Player mode against an automated bot (Player 2) managed by a heuristic state machine algorithm. When starting the game from the main menu, you can choose between the classic "Two Players" mode or "Single Player" mode.

### Heuristic Algorithm Behavior
The bot's artificial intelligence does not require neural networks or training time, but dynamically reacts to the game state and its resources:

- **Base Rules**: If the hand is empty, the bot prioritizes the "Accept" action to build a playable base. It evaluates Action Point (AP) waste and uses "Reject" only if the AP budget exceeds a safety margin calculated on missing cards.
- **Coin Management**: The bot instantly accepts the Coin, recognizing the mathematical advantage of the free extra AP.
- **Gem Management (Strategic Pivot)**: When the bot reveals the Gem, obtaining it becomes its absolute priority. If the hand is full, it forces a "Change" action by discarding the card with the lowest potential. Once the Gem is obtained, the algorithm performs a "pivot": it abandons any attempt to build Straights or Flushes (not supported by the Gem) and exclusively collects cards with the same value to force a Three of a kind, Full house, or Four of a kind and maximize the score.
- **Scroll Management (Memory)**: If the bot has a high AP budget (e.g. > 8), it will accept the Scroll, permanently revealing a card on the grid. The bot is equipped with "memory": in subsequent turns, before revealing random cards, it will check the card revealed by the Scroll. If useful to close a combo, it will directly target that coordinate.

