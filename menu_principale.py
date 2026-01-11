from breezypythongui import EasyFrame
from tkinter import Button
from PIL import Image, ImageTk
import sys
import os

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

if __name__ == "__main__":
    app = MenuPrincipale()
    app.mainloop()


class Classifica(EasyFrame):
    def __init__(self):
        super().__init__("Tesori Nascosti - Classifica")
        self.master.state('zoomed') 
        self.master.update()
        larghezza_schermo = self.master.winfo_width()
        altezza_schermo = self.master.winfo_height() 
        base_dir = os.path.dirname(os.path.abspath(__file__))
        percorso = os.path.join(base_dir, "Immagini_mazzo", "sfondo_classifica.png") 
        try:
            immagine = Image.open(percorso)
            immagine_ridimensionata = immagine.resize((larghezza_schermo, altezza_schermo), Image.Resampling.LANCZOS)
            self.foto = ImageTk.PhotoImage(immagine_ridimensionata)
        except Exception as e:
            self.messageBox("Errore Immagine", f"Errore: {e}")
            sys.exit()
        self.canvas = self.addCanvas(row = 0, column = 0, width = larghezza_schermo, height = altezza_schermo)
        self.canvas.create_image(0, 0, image = self.foto, anchor = "nw")
        centro_x = larghezza_schermo / 2
        centro_y = altezza_schermo / 2 
        self.pulsante_nuova_partita = Button(self.canvas, text = "MENU PRINCIPALE", command = self.torna_al_menu_principale, font=("Verdana", 16, "bold"), background = "#FFC125", foreground = "#8B4513", bd = 3)
        self.canvas.create_window(centro_x, centro_y + 200, window = self.pulsante_nuova_partita, width = 250, height = 60)
    
    def torna_al_menu_principale(self):
        """Chiude la classifica e riapre il menu principale"""
        self.destroy()
        from menu_principale import MenuPrincipale
        app = MenuPrincipale()
        app.mainloop()

if __name__ == "__main__":
    app = Classifica()
    app.mainloop() 