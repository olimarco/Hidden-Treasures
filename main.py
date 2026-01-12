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
    """
    Questa classe rappresenta la finestra di avvio dell'applicazione.
    Gestisce l'interfaccia grafica del menu principale, includendo
    l'immagine di copertina, la musica di sottofondo e il pulsante per iniziare.
    """
    def __init__(self):
        super().__init__("Tesori Nascosti - Menu")
        self.master.state('zoomed')                # Imposta la finestra a schermo intero
        
        # Recupera le dimensioni effettive dello schermo dell'utente per adattare la grafica
        larghezza_schermo = self.master.winfo_screenwidth()
        altezza_schermo = self.master.winfo_screenheight() 

        # Restituisce il percorso per l'immagine del menu principale in modo sicuro
        percorso = os.path.join("Immagini_mazzo", "copertina.png")
        try:
            immagine = Image.open(percorso)
            # Ridimensiono l'immagine per adattarla perfettamente alla risoluzione dello schermo
            # Uso LANCZOS per mantenere un'alta qualità durante il ridimensionamento
            immagine_ridimensionata = immagine.resize((larghezza_schermo, altezza_schermo), Image.Resampling.LANCZOS)
            self.foto = ImageTk.PhotoImage(immagine_ridimensionata)
        except Exception as e:
            self.messageBox("Errore Immagine", f"Errore: {e}")
            sys.exit()      # Se manca l'immagine, il programma si chiude

        # Gestione della musica di sottofondo tramite la libreria pygame
        try:
            pygame.mixer.init()

            percorso_musica = os.path.join("Audio", "musica_sottofondo.mp3")
            pygame.mixer.music.load(percorso_musica)
            pygame.mixer.music.set_volume(0.2)      # Impostazione volume
            pygame.mixer.music.play(-1)       # Il parametro -1 indica che la musica andrà in loop infinito
        except Exception as e:
            print(f"Impossibile caricare la musica: {e}")      # Se l'audio fallisce, il gioco parte comunque

        # Canvas per poter sovrapporre il pulsante all'immagine di sfondo
        self.canvas = self.addCanvas(row = 0, column = 0, width = larghezza_schermo, height = altezza_schermo)
        self.canvas.create_image(0, 0, image = self.foto, anchor = "nw")
        
        # Calcolo del centro dello schermo per posizionare il bottone
        centro_x = larghezza_schermo / 2
        centro_y = altezza_schermo / 2 
        
        # Pulsante "GIOCA" con font e colori personalizzati
        self.pulsante_gioca = Button(self.canvas, text = "GIOCA", command = self.avvia_gioco, font=("Verdana", 16, "bold"), background = "#FFC125", foreground = "#8B4513", borderwidth = 3)
        # Aggiunge il pulsante al canvas, spostandolo leggermente verso il basso
        self.canvas.create_window(centro_x, centro_y + 110, window = self.pulsante_gioca, width = 220, height = 60)

    def avvia_gioco(self):
        """
        Metodo collegato al pulsante Gioca.
        Chiude la finestra del menu e apre la finestra della partita.
        """
        if TesoriNascosti:
            self.destroy()
            app = TesoriNascosti()
            app.mainloop()
        else:
            self.messageBox("Errore", "Non trovo il file del gioco!")


class Classifica(EasyFrame):
    """
    Questa classe gestisce la visualizzazione della classifica.
    Legge i dati salvati su file e li mostra all'interno di una listbox.
    """
    def __init__(self):
        super().__init__("Tesori Nascosti - Classifica")
        self.master.state('zoomed')
        self.master.update()       # Aggiorna la finestra per assicurarsi che le dimensioni siano calcolate correttamente
       
        # Recupera le dimensioni della finestra attuale
        larghezza_schermo = self.master.winfo_width()
        altezza_schermo = self.master.winfo_height()
       
        # Ottiene il percorso assoluto della cartella in cui si trova questo script
        base_dir = os.path.dirname(os.path.abspath(__file__))
       
        percorso_sfondo = os.path.join(base_dir, "Immagini_mazzo", "sfondo_classifica.png")

        percorso_dati = os.path.join(base_dir, "classifica.txt")

        # Caricamento e ridimensionamento dello sfondo specifico per la classifica
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
       
        # Creazione della Listbox che conterrà le righe della classifica.
        self.lista_punteggi = tk.Listbox(
            self.canvas,
            font = ("Courier", 13, "bold"),
            background = "#F5DEB3",     
            foreground = "#4B3621",     
            borderwidth = 0,              
            highlightthickness = 0,    # Rimuove il bordo di selezione automatico per non rovinare la grafica della pergamena
            activestyle = "none"       # Rimuove la sottolineatura quando si clicca una riga
        )

        # Usa la classe GestoreClassifica per leggere e formattare i dati dal file di testo
        gestore = GestoreClassifica(percorso_dati)
        testo_completo = gestore.classifica_come_testo()
       
       # Inserisce ogni riga restituita dal gestore all'interno della Listbox
        righe = testo_completo.split("\n")
        for riga in righe:
            if riga.strip():        # Controllo per evitare di inserire righe vuote
                self.lista_punteggi.insert(tk.END, riga)

        # Posiziona la listbox al centro dello schermo
        self.canvas.create_window(centro_x, centro_y, window=self.lista_punteggi, width=700, height=350)
       
        # Pulsante per tornare indietro al menu
        self.pulsante_menu_principale = Button(
            self.canvas,
            text = "MENU PRINCIPALE",
            command = self.torna_al_menu_principale,
            font=("Verdana", 16, "bold"),
            background = "#FFC125",
            foreground = "#8B4513",
            borderwidth = 3
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