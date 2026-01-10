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
        nome_file_sfondo = "copertina.png"
        try:
            image_pil = Image.open(nome_file_sfondo)
            image_ridimensionata = image_pil.resize((larghezza_schermo, altezza_schermo), Image.Resampling.LANCZOS)
            self.immagine_sfondo = ImageTk.PhotoImage(image_ridimensionata)
        except Exception as e:
            self.messageBox("Errore Immagine", f"Errore: {e}")
            sys.exit()
        self.canvas = self.addCanvas(row = 0, column = 0, width = larghezza_schermo, height = altezza_schermo)
        self.canvas.create_image(0, 0, image = self.immagine_sfondo, anchor = "nw")
        centro_x = larghezza_schermo / 2
        centro_y = altezza_schermo / 2 
        self.pulsante_gioca = Button(self.canvas, text = "GIOCA", command = self.avvia_gioco,
                               font=("Verdana", 16, "bold"), background = "#FFC125", foreground = "#8B4513", bd=3)
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