from breezypythongui import EasyFrame
from tkinter import Button
from PIL import Image, ImageTk
from LeaderboardManager import LeaderboardManager
import sys
import os
import tkinter as tk
import pygame

try:
    from hidden_treasures_gui import HiddenTreasures
except ImportError:
    HiddenTreasures = None 

class MainMenu(EasyFrame):
    """
    This class represents the startup window of the application.
    It manages the graphical interface of the main menu, including
    the cover image, background music, and the play button.
    """
    def __init__(self):
        super().__init__("Hidden Treasures - Menu")
        self.master.state('zoomed')  # Sets window to fullscreen
        
        # Retrieves user's screen dimensions to scale the graphics
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight() 

        # Safe path for cover image
        path = os.path.join("deck_images", "cover.png")
        try:
            image = Image.open(path)
            # Resizes image to fit screen resolution using LANCZOS filter
            resized_image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            self.messageBox("Image Error", f"Error: {e}")
            sys.exit()  # If the cover image is missing, close the application

        # Background music management using pygame mixer
        try:
            pygame.mixer.init()

            music_path = os.path.join("audio", "background_music.mp3")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.2)  # Set volume
            pygame.mixer.music.play(-1)         # -1 means loop infinitely
        except Exception as e:
            print(f"Unable to load music: {e}")  # Play game anyway if audio fails

        # Canvas to overlay button on top of background image
        self.canvas = self.addCanvas(row=0, column=0, width=screen_width, height=screen_height)
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        
        # Calculate screen center to position the play button
        center_x = screen_width / 2
        center_y = screen_height / 2 
        
        # "PLAY" button with custom fonts and colors
        self.play_button = Button(
            self.canvas,
            text="PLAY",
            command=self.start_game,
            font=("Verdana", 16, "bold"),
            background="#FFC125",
            foreground="#8B4513",
            borderwidth=3
        )
        # Position play button slightly below center
        self.canvas.create_window(center_x, center_y + 110, window=self.play_button, width=220, height=60)

    def start_game(self):
        """
        Method linked to the PLAY button.
        Hides the PLAY button and displays mode selection buttons.
        """
        self.play_button.destroy()
        
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = screen_width / 2
        center_y = screen_height / 2 
        
        self.single_player_button = Button(
            self.canvas,
            text="SINGLE PLAYER",
            command=self.start_single_player,
            font=("Verdana", 14, "bold"),
            background="#FFC125",
            foreground="#8B4513",
            borderwidth=3
        )
        self.two_player_button = Button(
            self.canvas,
            text="TWO PLAYERS",
            command=self.start_two_players,
            font=("Verdana", 14, "bold"),
            background="#FFC125",
            foreground="#8B4513",
            borderwidth=3
        )
        
        self.canvas.create_window(center_x - 130, center_y + 110, window=self.single_player_button, width=220, height=60)
        self.canvas.create_window(center_x + 130, center_y + 110, window=self.two_player_button, width=220, height=60)

    def start_single_player(self):
        if HiddenTreasures:
            self.destroy()
            app = HiddenTreasures(game_mode="single")
            app.mainloop()
        else:
            self.messageBox("Error", "Cannot find the game file!")

    def start_two_players(self):
        if HiddenTreasures:
            self.destroy()
            app = HiddenTreasures(game_mode="two")
            app.mainloop()
        else:
            self.messageBox("Error", "Cannot find the game file!")


class Leaderboard(EasyFrame):
    """
    This class manages the display of the leaderboard.
    Reads saved data from a file and shows it in a listbox.
    """
    def __init__(self):
        super().__init__("Hidden Treasures - Leaderboard")
        self.master.state('zoomed')
        self.master.update()  # Refresh window to ensure correct dimensions are calculated
       
        # Retrieve current window size
        screen_width = self.master.winfo_width()
        screen_height = self.master.winfo_height()
       
        # Absolute path of script directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
       
        background_path = os.path.join(base_dir, "deck_images", "leaderboard_background.png")
        data_path = os.path.join(base_dir, "leaderboard.txt")

        # Load and resize background image
        try:
            image = Image.open(background_path)
            resized_image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            self.messageBox("Image Error", f"Error loading background: {e}")
            sys.exit()

        self.canvas = self.addCanvas(row=0, column=0, width=screen_width, height=screen_height)
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
       
        center_x = screen_width / 2
        center_y = screen_height / 2
       
        # Listbox to display leaderboard rows
        self.scores_listbox = tk.Listbox(
            self.canvas,
            font=("Courier", 13, "bold"),
            background="#F5DEB3",     
            foreground="#4B3621",     
            borderwidth=0,              
            highlightthickness=0,  # Remove selection border
            activestyle="none"     # Remove underline on click
        )

        # Uses LeaderboardManager to read and format data from text file
        manager = LeaderboardManager(data_path)
        full_text = manager.leaderboard_as_text()
       
        # Insert each row into Listbox
        rows = full_text.split("\n")
        for row in rows:
            if row.strip():  # Skip empty lines
                self.scores_listbox.insert(tk.END, row)

        # Center Listbox on screen
        self.canvas.create_window(center_x, center_y, window=self.scores_listbox, width=700, height=350)
       
        # Main Menu button
        self.main_menu_button = Button(
            self.canvas,
            text="MAIN MENU",
            command=self.return_to_main_menu,
            font=("Verdana", 16, "bold"),
            background="#FFC125",
            foreground="#8B4513",
            borderwidth=3
        )
        self.canvas.create_window(center_x, center_y + 220, window=self.main_menu_button, width=250, height=60)

    def return_to_main_menu(self):
        """Closes leaderboard and reopens main menu"""
        self.destroy()
        from main import MainMenu
        app = MainMenu()
        app.mainloop()

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()