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
        
        self.gestore = GestoreClassifica("classifica.txt")

        self.master.state('zoomed') 
        self.master.update() 
        
        w_reale = self.master.winfo_width()
        h_reale = self.master.winfo_height()
        
        h_meta = h_reale // 2 

        base_dir = os.path.dirname(os.path.abspath(__file__))
        percorso = os.path.join(base_dir, "Immagini_mazzo", "sfondo_classifica.png") 
        
        try:
            immagine = Image.open(percorso)
            immagine_ridimensionata = immagine.resize((w_reale, h_meta), Image.Resampling.LANCZOS)
            self.foto = ImageTk.PhotoImage(immagine_ridimensionata)
        except Exception as e:
            self.messageBox("Errore Immagine", f"Errore: {e}")
            self.foto = None

        self.canvas = self.addCanvas(row=0, column=0, width=w_reale, height=h_meta)
        if self.foto:
            self.canvas.create_image(0, 0, image=self.foto, anchor="nw")

        pannello_sotto = self.addPanel(row=1, column=0, background="#FDF5E6")
        
        self.lista_classifica = pannello_sotto.addListbox(row=0, column=0, rowspan=1, width=100, height=15)
        self.lista_classifica["font"] = ("Courier", 14, "bold")
        self.lista_classifica["bg"] = "#FDF5E6"
        self.lista_classifica["fg"] = "#4B3621"
        self.lista_classifica["borderwidth"] = 0
        self.lista_classifica["highlightthickness"] = 0

        try:
            testo_dati = self.gestore.classifica_come_testo()
            righe = testo_dati.split("\n")
            if not righe or righe == ['']:
                 self.lista_classifica.insert(tk.END, "Nessuna partita registrata.")
            else:
                for riga in righe:
                    if riga.strip():
                        self.lista_classifica.insert(tk.END, riga)
        except:
             self.lista_classifica.insert(tk.END, "Errore lettura file.")

        self.pulsante_nuova_partita = pannello_sotto.addButton(text="MENU PRINCIPALE", row=1, column=0, command=self.torna_al_menu_principale)

        self.pulsante_nuova_partita["font"] = ("Verdana", 16, "bold")
        self.pulsante_nuova_partita["bg"] = "#FFC125"
        self.pulsante_nuova_partita["fg"] = "#8B4513"
        self.pulsante_nuova_partita["width"] = 20

    def torna_al_menu_principale(self):
        """Chiude la classifica e riapre il menu principale"""
        self.destroy()
        from menu_principale import MenuPrincipale
        app = MenuPrincipale()
        app.mainloop()

if __name__ == "__main__":
    app = MenuPrincipale()
    app.mainloop()