from breezypythongui import EasyFrame
from tkinter import Button
from PIL import Image, ImageTk
from GestoreClassifica import GestoreClassifica
import sys
import os
import tkinter as tk
import pygame

try:
    from tesori_nascosti_gui import TesoriNascosti
except ImportError:
    TesoriNascosti = None 

class MenuPrincipale(EasyFrame):
    def __init__(self):
        super().__init__("Tesori Nascosti - Menu")
        self.master.state('zoomed') 
        larghezza_schermo = self.master.winfo_screenwidth()
        altezza_schermo = self.master.winfo_screenheight() 
        percorso = os.path.join("Immagini_mazzo", "copertina.png")
        try:
            immagine = Image.open(percorso)
            immagine_ridimensionata = immagine.resize((larghezza_schermo, altezza_schermo), Image.Resampling.LANCZOS)
            self.foto = ImageTk.PhotoImage(immagine_ridimensionata)
        except Exception as e:
            self.messageBox("Errore Immagine", f"Errore: {e}")
            sys.exit()

        try:
            pygame.mixer.init()

            percorso_musica = os.path.join("Audio", "musica_sottofondo.mp3")
            pygame.mixer.music.load(percorso_musica)
            pygame.mixer.music.set_volume(0.2) 
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Impossibile caricare la musica: {e}")

        self.canvas = self.addCanvas(row = 0, column = 0, width = larghezza_schermo, height = altezza_schermo)
        self.canvas.create_image(0, 0, image = self.foto, anchor = "nw")
        centro_x = larghezza_schermo / 2
        centro_y = altezza_schermo / 2 
        self.pulsante_gioca = Button(self.canvas, text = "GIOCA", command = self.avvia_gioco, font=("Verdana", 16, "bold"), background = "#FFC125", foreground = "#8B4513", bd=3)
        self.canvas.create_window(centro_x, centro_y + 110, window = self.pulsante_gioca, width = 220, height = 60)

    def avvia_gioco(self):
        if TesoriNascosti:
            self.destroy()
            app = TesoriNascosti()
            app.mainloop()
        else:
            self.messageBox("Errore", "Non trovo il file del gioco!")

    def chiudi_tutto(self):
        sys.exit()



class Classifica(EasyFrame):
    def __init__(self):
        super().__init__("Tesori Nascosti - Classifica")
        self.master.state('zoomed')
        self.master.update()
       
        larghezza_schermo = self.master.winfo_width()
        altezza_schermo = self.master.winfo_height()
       
        base_dir = os.path.dirname(os.path.abspath(__file__))
       
        percorso_sfondo = os.path.join(base_dir, "Immagini_mazzo", "sfondo_classifica.png")

        percorso_dati = os.path.join(base_dir, "classifica.txt")

        try:
            immagine = Image.open(percorso_sfondo)
            immagine_ridimensionata = immagine.resize((larghezza_schermo, altezza_schermo), Image.Resampling.LANCZOS)
            self.foto = ImageTk.PhotoImage(immagine_ridimensionata)
        except Exception as e:
            self.messageBox("Errore Immagine", f"Errore caricamento sfondo: {e}")
            sys.exit()

        self.canvas = self.addCanvas(row = 0, column = 0, width = larghezza_schermo, height = altezza_schermo)
        self.canvas.create_image(0, 0, image = self.foto, anchor = "nw")
       
        centro_x = larghezza_schermo / 2
        centro_y = altezza_schermo / 2
       
        self.lista_punteggi = tk.Listbox(
            self.canvas,
            font=("Courier", 13, "bold"),
            bg="#F5DEB3",     
            fg="#4B3621",     
            bd=0,              
            highlightthickness=0,
            activestyle="none"
        )

        gestore = GestoreClassifica(percorso_dati)
        testo_completo = gestore.classifica_come_testo()
       
        righe = testo_completo.split("\n")
        for riga in righe:
            if riga.strip():
                self.lista_punteggi.insert(tk.END, riga)

        self.canvas.create_window(centro_x, centro_y, window=self.lista_punteggi, width=700, height=350)
       
        self.pulsante_nuova_partita = Button(
            self.canvas,
            text = "MENU PRINCIPALE",
            command = self.torna_al_menu_principale,
            font=("Verdana", 16, "bold"),
            background = "#FFC125",
            foreground = "#8B4513",
            bd = 3
        )
        self.canvas.create_window(centro_x, centro_y + 220, window = self.pulsante_nuova_partita, width = 250, height = 60)

    def torna_al_menu_principale(self):
        """Chiude la classifica e riapre il menu principale"""
        self.destroy()
        from main import MenuPrincipale
        app = MenuPrincipale()
        app.mainloop()

if __name__ == "__main__":
    app = MenuPrincipale()
    app.mainloop()