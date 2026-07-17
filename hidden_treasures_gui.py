from breezypythongui import EasyFrame, EasyDialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
import time
from Card import Card
from Player import Player
from Deck import Deck
from validator import Validator
from LeaderboardManager import LeaderboardManager
import os

class NameDialog(EasyDialog):
    """
    This class manages a modal dialog window that appears at startup.
    It forces the players to enter their names before starting.
    Supports both Single Player (Human vs Bot) and Two Players modes.
    """
    def __init__(self, parent, game_mode="two"):
         self.game_mode = game_mode
         super().__init__(parent, "Player Registration")
    
    def body(self, master):
        """
        Defines the layout of the dialog box with labels and text fields.
        """
        self.addLabel(master, text="Player 1, enter your name", row=0, column=0)
        self.field_p1 = self.addTextField(master, text="", row=0, column=1)
        if self.game_mode == "two":
            self.addLabel(master, text="Player 2, enter your name", row=1, column=0)
            self.field_p2 = self.addTextField(master, text="", row=1, column=1)
        else:
            self.field_p2 = None
    
    def validate(self):
        """
        Checks that fields are not empty when OK is pressed.
        Returns False if there is an error, preventing the dialog from closing.
        """
        n1 = self.field_p1.getText().strip()
        if n1 == "":
            self.parent.messageBox(title="Error: No Name Entered", message="You must register with a name.")
            return False
        if self.game_mode == "two":
            n2 = self.field_p2.getText().strip()
            if n2 == "":
                self.parent.messageBox(title="Error: No Name Entered", message="Both players must register with a name.")
                return False
        return True
    
    def apply(self):
        """
        Called if validation succeeds.
        Saves the entered names into a variable to be used by the main class.
        """
        name1 = self.field_p1.getText().strip()
        if self.game_mode == "two":
            name2 = self.field_p2.getText().strip()
        else:
            name2 = "Bot"
        self.result = (name1, name2)
        self.setModified()

class ConcludeDialog(EasyDialog):
    """
    Confirmation window that appears when a player decides to end their turn permanently.
    """
    def __init__(self, parent):
        self.confirmed = False
        super().__init__(parent, "Conclude Round")
        
    def body(self, master):
        self.addLabel(master, text="The action is final.\nPress OK to confirm.", row=0, column=0)
        
    def apply(self):
        self.confirmed = True


class HiddenTreasures(EasyFrame):
    """
    Main application class.
    Manages the entire game logic, the card grid,
    turns, scores, and user interactions.
    """
    def __init__(self, title="Hidden Treasures", width=1000, height=1000, background="#008000", game_mode="two"):
        super().__init__(title, width, height, background)
       
        # Get system default button background dynamically
        try:
            import tkinter as tk
            temp_btn = tk.Button(self)
            self.default_bg = temp_btn.cget("bg")
            temp_btn.destroy()
        except Exception:
            self.default_bg = "#d9d9d9"
            
        # Object Initialization
        self.game_mode = game_mode
        self.bot_memory = {}
        self.game_deck = Deck()
        self.validator = Validator()
        self.leaderboard_manager = LeaderboardManager("leaderboard.txt")
        self.players = [Player("Player 1"), Player("Player 2")]
        
        # Game State Variables
        self.first_player_round = 0    # Index of who starts the current round
        self.turn_index = 0           # Index of whose turn it is
        self.selected_card_index = None  # Which card was clicked on the grid
        self.drawn_cards_grid = []    # List of 36 cards drawn from the deck
        self.buttons = []             # List of references to grid buttons
        self.start_time = 0
        self.timer_running = False
        self.ownership_map = {}       # Dict mapping grid indexes to player indexes
        
        # Flags for special turn phases
        self.swap_phase = False        # True if player selects "Swap"
        self.scroll_phase = False      # True if Scroll effect is active
        self.new_card_index = None     # Card entering hand after a swap
        self.round_number = 1

        # GUI Creation

        # Top panel with info labels, round number, and menu
        label_grid_panel = self.addPanel(row=0, column=0, columnspan=4, background="#008000")
        self.label_info = label_grid_panel.addLabel(text="Waiting for players...", row=0, column=0, columnspan=2)
        self.label_info["anchor"] = "w"      
        self.label_info["justify"] = "left"
        self.label_round = label_grid_panel.addLabel(text=f"Round {self.round_number}", row=0, column=1, columnspan=2, sticky="NW")
        self.label_timer = label_grid_panel.addLabel(text="Time: 0s", row=0, column=2, columnspan=4, sticky="NW")
        self.menu = label_grid_panel.addMenuBar(row=0, column=3)
        menu = self.menu.addMenu("Menu")
        menu.addMenuItem("New Game", command=self.return_to_main_menu)
        menu.addMenuItem("Leaderboard", command=self.show_leaderboard)

        # Prepare card back image cache
        back_path = self.get_image_path("red_card_back_8bit.png")
        self.back_image_cache = self.load_image(back_path)
        
        # Create panel for the 6x6 grid of card buttons
        card_grid_panel = self.addPanel(row=1, column=0, columnspan=6, background="#008000")
        for r in range(6):
            for c in range(6):
                card_idx = r * 6 + c
                # Lambda function to pass correct index to each button
                button = card_grid_panel.addButton(text="", row=r, column=c, command=lambda x=card_idx: self.reveal_card(x))
                button["height"] = 0
                button["width"] = 0
                button["image"] = self.back_image_cache
                button.image = self.back_image_cache  # Prevent garbage collection
                self.buttons.append(button)
        
        # Action buttons
        self.button_accept = self.addButton(text="Accept (1 AP)", row=3, column=0, command=self.action_accept, state="disabled") 
        self.button_reject = self.addButton(text="Reject (1 AP)", row=3, column=1, command=self.action_reject, state="disabled")
        self.button_swap = self.addButton(text="Swap (2 AP)", row=3, column=2, command=self.action_swap, state="disabled")
        self.button_conclude = self.addButton(text="Conclude", row=3, column=3, command=self.action_conclude, state="disabled")
        self.after(100, self.open_dialog)  # Start name dialog after short delay to ensure GUI is loaded

    def open_dialog(self):
        """
        Opens the name registration dialog. If confirmed, initializes the match.
        """
        dialog = NameDialog(self, game_mode=self.game_mode)
        if dialog.modified():
            self.label_timer["text"] = "Time: 0s"
            n1, n2 = dialog.result
            self.players = [Player(n1), Player(n2)]
            self.first_player_round = 0 
            self.turn_index = 0
            self.round_number = 1
            self.label_round["text"] = "Round 1"
            # Reset button backgrounds
            self.button_accept["bg"] = self.default_bg
            self.button_reject["bg"] = self.default_bg
            self.button_swap["bg"] = self.default_bg
            self.button_conclude["bg"] = self.default_bg
            # Start timer
            self.start_time = time.time()
            self.absolute_game_start = time.time()
            self.timer_running = True
            self.update_timer()
            # Start game logic
            self.start_round()
            self.manage_turn()
        else:
            self.return_to_main_menu()

    def show_leaderboard(self):
        """
        Closes current window and opens the leaderboard window.
        """
        self.destroy()
        from main import Leaderboard 
        app = Leaderboard()
        app.mainloop()

    def update_timer(self):
        """
        Function that updates the timer label every second.
        """
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.label_timer["text"] = f"Time: {elapsed_time}s"
            self.after(1000, self.update_timer)

    def start_round(self):
        """
        Prepares the grid for a new round: shuffles deck and draws 36 cards.
        """
        self.turn_index = self.first_player_round
        self.game_deck.create_deck()
        self.drawn_cards_grid = self.game_deck.draw_36()
        self.ownership_map = {}
        self.selected_card_index = None
        self.swap_phase = False

        # Reset grid buttons visually
        for button in self.buttons:
            button["bg"] = self.default_bg
            button["state"] = "normal"
        
        # Reset players' round states
        for p in self.players:
            p.reset_round()
        self.manage_turn()

    def manage_turn(self): 
        """
        Updates the interface based on the active player's state.
        Enables or disables action buttons depending on Action Points and hand size.
        """
        current_player = self.players[self.turn_index]

        # Calculate provisional score to display it in real time
        if not current_player.concluded:
            current_hand_points = self.validator.evaluate_hand(current_player.hand, current_player.action_points)
            current_player.score = current_player.total_score + current_hand_points
        
        # Set colors to distinguish player turns
        if self.turn_index == 0:
            current_color = "#87CEFA"
        else:
            current_color = "#FC7868"
        self.label_info["text"] = f"Turn of {current_player.name}\n Action Points: {current_player.action_points}\n Score: {current_player.score}\n Hand: {len(current_player.hand)}/5"
        
        # Update colors
        self.label_info["bg"] = current_color
        self.button_accept["bg"] = current_color
        self.button_reject["bg"] = current_color
        self.button_swap["bg"] = current_color
        self.button_conclude["bg"] = current_color

        # Button enabling
        if self.selected_card_index is None: 
            self.button_accept["state"] = "disabled"
            self.button_reject["state"] = "disabled"
            self.button_swap["state"] = "disabled"
            if len(current_player.hand) == 5 and not current_player.concluded:
                self.button_conclude["state"] = "normal"
            else:
                self.button_conclude["state"] = "disabled"
        else: 
            # Accept: only if there's space in hand
            if len(current_player.hand) < 5:
                self.button_accept["state"] = "normal"
            else:
                self.button_accept["state"] = "disabled"

            # Reject: only if player has enough AP to discard (costs 1 AP)
            if current_player.action_points > 5 - len(current_player.hand):
                self.button_reject["state"] = "normal"
            else:
                self.button_reject["state"] = "disabled"

            # Swap: costs 2 AP and requires at least one card in hand to exchange
            if len(current_player.hand) >= 1 and current_player.action_points >= 7 - len(current_player.hand):
                self.button_swap["state"] = "normal"
            else:
                self.button_swap["state"] = "disabled"
            
            self.button_conclude["state"] = "disabled"

    def change_turn(self):
        """
        Handles passing the turn to the other player and updating card visibility.
        """
        self.selected_card_index = None
        self.new_card_index = None
        self.swap_phase = False

        # If both players are done or run out of AP, end the round
        if (self.players[0].concluded or self.players[0].action_points <= 0) and (self.players[1].concluded or self.players[1].action_points <= 0):
            self.end_round()
            return
        
        # Calculate index of the other player
        next_index = 1 - self.turn_index
        next_player = self.players[next_index]

        # If one player is finished, the other continues
        if next_player.concluded or next_player.action_points <= 0:
            pass 
        else:
            self.turn_index = next_index
        active_index = self.turn_index 
        back_path = self.get_image_path("red_card_back_8bit.png")
        back_photo = self.load_image(back_path)

        # Update the grid: hide opponent's cards, show owned cards
        for i, button in enumerate(self.buttons):
            card_obj = self.drawn_cards_grid[i]
            if i in self.ownership_map:
                owner = self.ownership_map[i]
                if owner == 0:
                    button["bg"] = "#87CEFA" 
                else:
                    button["bg"] = "#FC7868" 
                button["state"] = "disabled"

                # Card is only seen face up by its owner (in two-player mode)
                # In single-player, human (owner 0) always sees their cards face up, and bot (owner 1) always keeps theirs face down.
                if self.game_mode == "single":
                    visible_to_viewer = (owner == 0)
                else:
                    visible_to_viewer = (owner == active_index)

                if visible_to_viewer:
                    path = self.get_image_path(card_obj)
                    photo = self.load_image(path)
                    button["image"] = photo
                    button.image = photo
                else:
                    button["image"] = back_photo
                    button.image = back_photo
            else:
                button["bg"] = self.default_bg
                if not card_obj.revealed_permanently:
                    button["image"] = back_photo
                    button.image = back_photo
                else:
                    path = self.get_image_path(card_obj)
                    photo = self.load_image(path)
                    button["image"] = photo
                    button.image = photo
                
                if self.players[active_index].action_points > 0:
                    button["state"] = "normal"
                else:
                    button["state"] = "disabled"     
        self.manage_turn()
        if self.game_mode == "single" and self.turn_index == 1:
            self.disable_human_interaction()
            self.after(1500, self.bot_take_turn)
    
    def reveal_card(self, card_index):
        """
        Handles clicking on a card in the grid.
        Behavior changes depending on the phase (Normal, Swap, Scroll).
        """
        if self.scroll_phase:
            if card_index in self.ownership_map:
                self.messageBox("Error", "You cannot reveal an already assigned card.")
                return

            card_obj = self.drawn_cards_grid[card_index]    
            if card_obj.revealed_permanently:
                 return
            card_obj.reveal_permanently()
            
            path = self.get_image_path(card_obj)
            photo = self.load_image(path)
            self.buttons[card_index]["image"] = photo
            self.buttons[card_index].image = photo
            
            self.scroll_phase = False
            self.change_turn()
            return
        
        current_player = self.players[self.turn_index]
        if self.swap_phase:
            owner_index = self.ownership_map.get(card_index)
            # Player must click one of their own cards to exchange it
            if owner_index == self.turn_index and card_index != self.new_card_index:
                card_obj = self.drawn_cards_grid[card_index]

                if card_obj in current_player.hand:
                    current_player.remove_card(card_obj)
                new_card = self.drawn_cards_grid[self.new_card_index]
                current_player.add_card(new_card)

                # Free up the position of the old card
                del self.ownership_map[card_index]
                self.buttons[card_index]["bg"] = self.default_bg

                # Check effects of the newly acquired card
                if new_card.special_type in ["Scroll", "P"]:
                    self.scroll_phase = True
                    if not (self.game_mode == "single" and self.turn_index == 1):
                        self.messageBox(title="Scroll Effect", message="You swapped for a Scroll!\nClick on a card on the grid to reveal it permanently.")
                    return
                self.change_turn()
            return
        
        if self.selected_card_index is not None or current_player.action_points <= 0:
            return
        self.selected_card_index = card_index

        # Flip the card visually only for the active player
        card_obj = self.drawn_cards_grid[card_index]
        card_obj.flip_card()
        if self.turn_index == 0:
            current_color = "#87CEFA" 
        else:
            current_color = "#FC7868"
        self.buttons[card_index]["bg"] = current_color
        path = self.get_image_path(card_obj)
        try:
            self.buttons[card_index]["width"] = 0
            self.buttons[card_index]["height"] = 0
            photo = self.load_image(path)
            self.buttons[card_index]["image"] = photo
            self.buttons[card_index].image = photo
        except Exception as e:
            print(e)
            self.buttons[card_index]["text"] = str(card_obj)
        self.manage_turn()

    def action_accept(self):
        """
        Player confirms keeping the selected card.
        """
        current_player = self.players[self.turn_index]

        current_player.action_points -= 1  # Action cost
        taken_card = self.drawn_cards_grid[self.selected_card_index]
        if self.selected_card_index is not None:
            current_player.add_card(taken_card)
            self.buttons[self.selected_card_index]["state"] = "disabled"
            self.ownership_map[self.selected_card_index] = self.turn_index

            # Instant effects of special cards
            if taken_card.special_type in ["Coin", "M"]:
                current_player.action_points += 1
                if not (self.game_mode == "single" and self.turn_index == 1):
                    self.messageBox(title="Coin!", message="You collected a Coin!\nYou gain +1 extra Action Point.")
            
            if taken_card.special_type in ["Scroll", "P"]:
                self.scroll_phase = True
                if not (self.game_mode == "single" and self.turn_index == 1):
                    self.messageBox(title="Scroll Effect", message="You found a Scroll!\nClick on a face-down card on the grid to reveal it permanently.")
                return

        self.change_turn()

    def action_reject(self):
        """
        Player discards the selected card, which goes back face down on the grid.
        """
        self.players[self.turn_index].action_points -= 1

        rejected_card = self.drawn_cards_grid[self.selected_card_index]
        rejected_card.flip_card()  # Covers it again

        self.change_turn()

    def action_swap(self):
        """
        Starts swap procedure: player keeps selected card but must discard one from their hand.
        """
        current_player = self.players[self.turn_index]
        current_player.action_points -= 2
        self.swap_phase = True

        self.new_card_index = self.selected_card_index
        self.ownership_map[self.selected_card_index] = self.turn_index
        self.buttons[self.selected_card_index]["state"] = "disabled"

        if self.turn_index == 0:
            current_color = "#87CEFA" 
        else:
            current_color = "#FC7868"

        # Make owned cards clickable on the grid to exchange
        for card_idx, owner_idx in self.ownership_map.items():
            if owner_idx == self.turn_index and card_idx != self.new_card_index:
                self.buttons[card_idx]["state"] = "normal"
                self.buttons[card_idx]["bg"] = current_color 
                card_obj = self.drawn_cards_grid[card_idx]
                path = self.get_image_path(card_obj)
                try:
                    self.buttons[card_idx]["width"] = 0
                    self.buttons[card_idx]["height"] = 0
                    photo = self.load_image(path)
                    self.buttons[card_idx]["image"] = photo
                    self.buttons[card_idx].image = photo 
                except Exception as e:
                    print(f"Error loading swap image: {e}")
                    self.buttons[card_idx]["text"] = str(card_obj)
                

        # Disable other action buttons until swap completes
        self.button_accept["state"] = "disabled"
        self.button_reject["state"] = "disabled"
        self.button_swap["state"] = "disabled"
        self.button_conclude["state"] = "disabled"

    def action_conclude(self):
        """
        Opens confirmation dialog to end the current player's round.
        """
        dialog = ConcludeDialog(self)
        if not dialog.confirmed:
            return
        self.players[self.turn_index].concluded = True
        self.button_conclude["state"] = "disabled"
        self.change_turn()

    def end_round(self):
        """
        Calculates scores at the end of the round and decides whether to continue or finish.
        """
        self.timer_running = False
        timer_pause = time.time()

        # Update total scores
        for player in self.players:
            round_points = self.validator.evaluate_hand(player.hand, player.action_points)
            player.total_score += round_points
            player.score = player.total_score

        # Check win condition
        if self.players[0].score < 110 and self.players[1].score < 110:
            self.label_info["text"] = "Waiting to start a new round..."
            self.label_info["bg"] = self.default_bg

            # Reset grid visual
            path = self.get_image_path("red_card_back_8bit.png")
            photo = self.load_image(path)
            for button in self.buttons:
                button["bg"] = self.default_bg
                button["state"] = "normal"
                button["image"] = photo
                button.image = photo
            self.button_accept["state"] = "disabled"
            self.button_accept["bg"] = self.default_bg
            self.button_reject["state"] = "disabled"
            self.button_reject["bg"] = self.default_bg
            self.button_swap["state"] = "disabled"
            self.button_swap["bg"] = self.default_bg
            self.button_conclude["state"] = "disabled"
            self.button_conclude["bg"] = self.default_bg
            self.messageBox(title=f"Round {self.round_number} Finished", message="No player has reached 110 points. You are about to start a new round.")
            
            # Alternate starting player
            self.first_player_round = 1 - self.first_player_round
            self.round_number += 1
            self.label_round["text"] = f"Round {self.round_number}"
           
            # Adjust start time for pause duration
            timer_resume = time.time()
            pause_duration = timer_resume - timer_pause
            self.start_time += pause_duration
            self.timer_running = True
            self.update_timer()
            self.start_round()
        else:
            self.end_game()

    def end_game(self):
        """
        Declares the winner, handles ties, and saves data to leaderboard.
        """
        p1 = self.players[0]
        p2 = self.players[1]

        # Score Comparison
        if p1.score > p2.score:
            text = f"{p1.name} WINS!"
            current_color = "#87CEFA"
            title = f"Victory goes to {p1.name}"
            message = f"{p1.name} scored {p1.score} points."
            winner_name = p1.name 
            
        elif p2.score > p1.score:
            text = f"{p2.name} WINS!"
            current_color = "#FC7868"
            title = f"Victory goes to {p2.name}"
            message = f"{p2.name} scored {p2.score} points."
            winner_name = p2.name
            
        else:
            # Action Points tiebreaker
            if p1.action_points > p2.action_points:
                text = f"{p1.name} WINS (AP Tiebreaker)!"
                current_color = "#87CEFA"
                title = f"Victory goes to {p1.name}"
                message = f"{p1.name} scored {p1.score} points, and with {p1.action_points} remaining Action Points, claims the victory."
                winner_name = p1.name
                
            elif p2.action_points > p1.action_points:
                text = f"{p2.name} WINS (AP Tiebreaker)!"
                current_color = "#FC7868"
                title = f"Victory goes to {p2.name}"
                message = f"{p2.name} scored {p2.score} points, and with {p2.action_points} remaining Action Points, claims the victory."
                winner_name = p2.name
                
            else:
                text = "TIE!"
                current_color = self.default_bg
                title = "ABSOLUTE TIE"
                message = "The match ends in an absolute tie."
                winner_name = "TIE"

        # GUI Final Update
        self.label_info["text"] = f"GAME OVER\n{text}"
        self.label_info["bg"] = current_color
        self.button_accept["state"] = "disabled"
        self.button_accept["bg"] = self.default_bg
        self.button_reject["state"] = "disabled"
        self.button_reject["bg"] = self.default_bg
        self.button_swap["state"] = "disabled"
        self.button_swap["bg"] = self.default_bg
        self.button_conclude["state"] = "disabled"
        self.button_conclude["bg"] = self.default_bg
        for button in self.buttons:
            button["state"] = "disabled"
            
        self.messageBox(title=title, message=message + "\nYou can view the results of this match in Menu → Leaderboard.")
        
        # Save to file
        try:
            total_duration = int(time.time() - self.absolute_game_start)
            self.leaderboard_manager.register_match(
                name1=p1.name,
                points1=p1.score,
                ap1=p1.action_points,
                name2=p2.name,
                points2=p2.score,
                ap2=p2.action_points,
                winner=winner_name,
                round_num=self.round_number,
                duration_seconds=total_duration
            )
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def get_image_path(self, card):
        """
        Builds the image file path based on the card type (special or numeric).
        """
        if isinstance(card, str):
            file_name = f"red_card_back_8bit.png"
        elif card.special_type:
            file_name = f"{card.special_type.lower()}.png"
        elif card.value:
            file_name = f"{card.value}_of_{card.suit.lower()}.png"
        return os.path.join("deck_images", file_name)

    def load_image(self, path):
        """
        Loads an image and resizes it to fit the buttons (55x70).
        """
        pil_image = Image.open(path)
        resized_image = pil_image.resize((55, 70), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized_image)

    def disable_human_interaction(self):
        """
        Disables human interaction buttons and card grid buttons during bot turns.
        """
        self.button_accept["state"] = "disabled"
        self.button_reject["state"] = "disabled"
        self.button_swap["state"] = "disabled"
        self.button_conclude["state"] = "disabled"
        for button in self.buttons:
            button["state"] = "disabled"

    def get_hand_potential_score(self, hand, strategy):
        """
        Calculates a heuristic score representing the potential value of the hand.
        """
        if not hand:
            return 0
        from collections import Counter
        
        # Base combination score using the existing validator
        combo_score = self.validator.calculate_combo_score(hand)
        
        potential = 0
        
        # Get numeric values of the standard cards
        values = [c.value for c in hand if c.value is not None]
        val_counts = Counter(values)
        
        # Get suits of the standard cards
        suits = [c.suit for c in hand if c.suit is not None]
        suit_counts = Counter(suits)
        
        if strategy == "value":
            # Value-based strategy (Gem acquired): focus exclusively on Pairs, Tris, Full, Poker
            for val, count in val_counts.items():
                if count == 2:
                    potential += 15
                elif count == 3:
                    potential += 40
                elif count >= 4:
                    potential += 70
        else:
            # Default strategy: both value and suit/straights
            for val, count in val_counts.items():
                if count == 2:
                    potential += 10
                elif count == 3:
                    potential += 30
                elif count >= 4:
                    potential += 60
            
            # Flush potential
            for suit, count in suit_counts.items():
                if count >= 2:
                    potential += count * 6
                    
            # Straight potential
            sorted_vals = sorted(list(set(values)))
            if len(sorted_vals) >= 2:
                for i in range(len(sorted_vals) - 1):
                    if sorted_vals[i+1] - sorted_vals[i] < 5:
                        potential += 4
                        
        return combo_score * 100 + potential

    def get_weakest_card_index(self, hand, strategy):
        """
        Finds the index of the weakest card in hand by checking which card's removal
        leaves the hand with the highest remaining potential score.
        """
        best_score = -1
        weakest_idx = 0
        for i in range(len(hand)):
            temp_hand = hand[:i] + hand[i+1:]
            score = self.get_hand_potential_score(temp_hand, strategy)
            if score > best_score:
                best_score = score
                weakest_idx = i
        return weakest_idx

    def bot_take_turn(self):
        """
        Executes the bot's turn using the heuristic algorithm.
        """
        if self.turn_index != 1 or self.players[1].concluded or self.players[1].action_points <= 0:
            return

        bot_player = self.players[1]
        hand = bot_player.hand
        ap = bot_player.action_points
        
        # Strategy detection: pivot if Gem is in hand
        has_gem = any(c.special_type in ["Gem", "G"] for c in hand)
        strategy = "value" if has_gem else "any"

        # Conclude check:
        # Automatically use 'Conclude' when hand is full and no further improvements are viable without wasting too many AP.
        if len(hand) == 5:
            current_score = self.validator.calculate_combo_score(hand)
            # If hand is excellent or AP is low, conclude
            if current_score >= 25 or ap <= 6:
                self.bot_conclude()
                return

        # Ensure bot_memory exists
        if not hasattr(self, "bot_memory"):
            self.bot_memory = {}

        # 1. Evaluate memory first
        best_memorized_idx = -1
        best_memorized_score = -1
        
        # Only consider memorized cards that are still available on the grid
        available_memorized = {idx: card for idx, card in self.bot_memory.items() if idx not in self.ownership_map}
        
        for idx, card in available_memorized.items():
            if len(hand) < 5:
                curr_pot = self.get_hand_potential_score(hand, strategy)
                new_pot = self.get_hand_potential_score(hand + [card], strategy)
                if new_pot > curr_pot and new_pot > best_memorized_score:
                    best_memorized_score = new_pot
                    best_memorized_idx = idx
            else:
                curr_pot = self.get_hand_potential_score(hand, strategy)
                for h_idx in range(len(hand)):
                    temp_hand = hand[:h_idx] + hand[h_idx+1:] + [card]
                    new_pot = self.get_hand_potential_score(temp_hand, strategy)
                    if new_pot > curr_pot and new_pot > best_memorized_score:
                        best_memorized_score = new_pot
                        best_memorized_idx = idx

        # Target memorized card if it improves the hand
        if best_memorized_idx != -1:
            self.selected_card_index = best_memorized_idx
            card_obj = self.drawn_cards_grid[best_memorized_idx]
            card_obj.flip_card()
            self.buttons[best_memorized_idx]["bg"] = "#FC7868"
            path = self.get_image_path(card_obj)
            photo = self.load_image(path)
            self.buttons[best_memorized_idx]["image"] = photo
            self.buttons[best_memorized_idx].image = photo
            
            self.after(1500, lambda: self.bot_decide_action(card_obj))
            return

        # 2. Pick a random face-down card
        available_idxs = [i for i, c in enumerate(self.drawn_cards_grid) if i not in self.ownership_map and not c.revealed_permanently]
        if not available_idxs:
            self.bot_conclude()
            return
            
        import random
        chosen_idx = random.choice(available_idxs)
        self.selected_card_index = chosen_idx
        
        card_obj = self.drawn_cards_grid[chosen_idx]
        card_obj.flip_card()
        self.buttons[chosen_idx]["bg"] = "#FC7868"
        path = self.get_image_path(card_obj)
        photo = self.load_image(path)
        self.buttons[chosen_idx]["image"] = photo
        self.buttons[chosen_idx].image = photo
        
        self.after(1500, lambda: self.bot_decide_action(card_obj))

    def bot_decide_action(self, card_obj):
        """
        Decides and executes the bot's action after a card is revealed.
        """
        bot_player = self.players[1]
        hand = bot_player.hand
        ap = bot_player.action_points
        has_gem = any(c.special_type in ["Gem", "G"] for c in hand)
        strategy = "value" if has_gem else "any"

        # The Coin: Always Accept
        if card_obj.special_type in ["Coin", "M"]:
            self.bot_accept_action()
            return

        # The Gem: Top Priority
        if card_obj.special_type in ["Gem", "G"]:
            if len(hand) < 5:
                self.bot_accept_action()
            else:
                weakest_idx = self.get_weakest_card_index(hand, strategy)
                self.bot_swap_action(weakest_idx)
            return

        # The Scroll: Accept if AP > 8, otherwise reject
        if card_obj.special_type in ["Scroll", "P"]:
            if ap > 8:
                self.bot_accept_scroll_action()
            else:
                self.bot_reject_action()
            return

        # Standard card logic
        if len(hand) == 0:
            self.bot_accept_action()
            return

        curr_pot = self.get_hand_potential_score(hand, strategy)
        if len(hand) < 5:
            new_pot = self.get_hand_potential_score(hand + [card_obj], strategy)
            if new_pot > curr_pot:
                self.bot_accept_action()
            else:
                # Reject useless card only if AP budget safely exceeds missing cards count
                missing_cards = 5 - len(hand)
                if ap - 1 > missing_cards:
                    self.bot_reject_action()
                else:
                    self.bot_accept_action()
        else:
            # Hand is full, evaluate swap
            best_swap_idx = -1
            best_pot = curr_pot
            for idx, h_card in enumerate(hand):
                temp_hand = hand[:idx] + hand[idx+1:] + [card_obj]
                pot = self.get_hand_potential_score(temp_hand, strategy)
                if pot > best_pot:
                    best_pot = pot
                    best_swap_idx = idx
            
            if best_swap_idx != -1:
                self.bot_swap_action(best_swap_idx)
            else:
                self.bot_reject_action()

    def bot_accept_action(self):
        """
        Bot executes the accept action for the currently selected card.
        """
        bot_player = self.players[1]
        bot_player.action_points -= 1
        taken_card = self.drawn_cards_grid[self.selected_card_index]
        bot_player.add_card(taken_card)
        self.buttons[self.selected_card_index]["state"] = "disabled"
        self.ownership_map[self.selected_card_index] = 1
        
        if taken_card.special_type in ["Coin", "M"]:
            bot_player.action_points += 1
            
        # Pacing: Wait 1.5 seconds before passing the turn so the user sees the card accepted
        self.after(1500, self.change_turn)

    def bot_reject_action(self):
        """
        Bot executes the reject action, turning the card back face-down.
        """
        bot_player = self.players[1]
        bot_player.action_points -= 1
        rejected_card = self.drawn_cards_grid[self.selected_card_index]
        
        # Pacing: Let the user see the rejected card state for 1.5 seconds before passing turn
        def perform_reject():
            rejected_card.flip_card()
            self.change_turn()
        self.after(1500, perform_reject)

    def bot_swap_action(self, hand_card_idx):
        """
        Bot swaps the currently selected card with the card at hand_card_idx.
        """
        bot_player = self.players[1]
        bot_player.action_points -= 2
        
        old_card = bot_player.hand[hand_card_idx]
        old_grid_idx = -1
        for idx, owner in self.ownership_map.items():
            if owner == 1 and self.drawn_cards_grid[idx] == old_card:
                old_grid_idx = idx
                break
                
        # Highlight both buttons temporarily (keep them face-down)
        if old_grid_idx != -1:
            self.buttons[old_grid_idx]["bg"] = "#FFFF00" # Yellow highlight
            self.buttons[self.selected_card_index]["bg"] = "#FFFF00" # Yellow highlight
            
        def perform_swap():
            bot_player.remove_card(old_card)
            new_card = self.drawn_cards_grid[self.selected_card_index]
            bot_player.add_card(new_card)
            
            if old_grid_idx != -1:
                del self.ownership_map[old_grid_idx]
                self.buttons[old_grid_idx]["bg"] = self.default_bg
                
            self.ownership_map[self.selected_card_index] = 1
            self.buttons[self.selected_card_index]["state"] = "disabled"
            
            if new_card.special_type in ["Scroll", "P"]:
                self.bot_trigger_scroll_effect()
                return
                
            self.change_turn()
            
        self.after(1500, perform_swap)

    def bot_accept_scroll_action(self):
        """
        Bot accepts a Scroll and triggers its effect.
        """
        bot_player = self.players[1]
        bot_player.action_points -= 1
        taken_card = self.drawn_cards_grid[self.selected_card_index]
        bot_player.add_card(taken_card)
        self.buttons[self.selected_card_index]["state"] = "disabled"
        self.ownership_map[self.selected_card_index] = 1
        
        # Pacing: Let the user see the scroll card action for 1.5 seconds before triggering its effect
        self.after(1500, self.bot_trigger_scroll_effect)

    def bot_trigger_scroll_effect(self):
        """
        Selects a random face-down card to reveal permanently and memorizes it.
        """
        face_down_idxs = [i for i, c in enumerate(self.drawn_cards_grid) if i not in self.ownership_map and not c.revealed_permanently]
        if face_down_idxs:
            import random
            reveal_idx = random.choice(face_down_idxs)
            card_obj = self.drawn_cards_grid[reveal_idx]
            card_obj.reveal_permanently()
            
            if not hasattr(self, "bot_memory"):
                self.bot_memory = {}
            self.bot_memory[reveal_idx] = card_obj
            
            path = self.get_image_path(card_obj)
            photo = self.load_image(path)
            self.buttons[reveal_idx]["image"] = photo
            self.buttons[reveal_idx].image = photo
            
            # Pacing: Let the user see the Scroll-revealed card for 2.0 seconds before passing turn
            self.after(2000, self.change_turn)
        else:
            self.change_turn()

    def bot_conclude(self):
        """
        Bot concludes its round.
        """
        self.players[1].concluded = True
        self.change_turn()

    def return_to_main_menu(self):
        """
        Closes current game and returns to the main menu.
        """
        self.destroy()
        from main import MainMenu
        app = MainMenu()
        app.mainloop()

if __name__ == "__main__":
    app = HiddenTreasures()
    app.mainloop()
