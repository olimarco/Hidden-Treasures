from breezypythongui import EasyFrame, EasyDialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
import time
import sys
from Carta import Carta
from Giocatore import Giocatore
from Mazzo import Mazzo
import os 

class DialogoNomi(EasyDialog):
    def __init__(self, parent):
         super().__init__(parent, "Registrazione Giocatotori")
    def body(self, master):
        self.addLabel(master, text = "Giocatore 1, inserisci il tuo nome", row = 0, column = 0)
        self.campo_g1 = self.addTextField(master, text = "", row = 0, column = 1)
        self.addLabel(master, text = "Giocatore 2, inserisci il tuo nome", row = 1, column = 0)
        self.campo_g2 = self.addTextField(master, text = "", row = 1, column = 1)
    def validate(self):
        n1 = self.campo_g1.getText().strip()
        n2 = self.campo_g2.getText().strip()
        if n1 == "" or n2 == "":
            self.messageBox(title = "Errore: Nessun Nome Inserito", message = "Entrambi i giocatori devono registrarsi con un nome.")
            return False
        return True
    def apply(self):
        nome1 = self.campo_g1.getText().strip()
        nome2 = self.campo_g2.getText().strip()
        self.risultato = (nome1, nome2)
        self.setModified()

class DialogoConcludi(EasyDialog):
    def __init__(self, parent):
        self.confermato = False
        super().__init__(parent, "Concludi Round")
    def body(self, master):
        self.addLabel(master, text="L'azione è definitiva.\nPremi OK per confermare. ", row=0, column=0)
    def apply(self):
        self.confermato = True


class TesoriNascosti(EasyFrame):
    def __init__(self, title = "Tesori Nascosti - Team 2", width = 1000, height = 1000, background = "#008000"):
        super().__init__(title, width, height, background)
        self.mazzo_gioco = Mazzo()
        self.giocatori = [Giocatore("Giocatore 1"), Giocatore("Giocatore 2")]
        self.indice_turno = 0
        self.indice_carta_selezionata = None
        self.griglia_carte_estratte = []
        self.pulsanti = []
        self.tempo_inizio = 0
        self.timer_in_corso = False
        self.mappa_possesso = {}
        self.fase_scambio = False 
        self.indice_nuova_carta = None 
        self.numero_round = 1
        pannello_griglia_label = self.addPanel(row = 0, column = 0, columnspan = 4, background = "#008000")
        self.label_info = pannello_griglia_label.addLabel(text = "In attesa dei giocatori...", row = 0, column = 0, columnspan = 2)
        self.label_info["anchor"] = "w"      
        self.label_info["justify"] = "left"
        self.label_round = pannello_griglia_label.addLabel(text = f"Round {self.numero_round}", row = 0, column = 1, columnspan = 2, sticky = "NW")
        self.label_timer = pannello_griglia_label.addLabel(text = "Tempo: 0s", row = 0, column = 2, columnspan = 4, sticky = "NW")
        self.menu = pannello_griglia_label.addMenuBar(row = 0, column = 3)
        menu = self.menu.addMenu("Menu")
        menu.addMenuItem("Nuova Partita", command = self.apriDialog)
        # menu.addMenuItem("Classifica", command = self.mostraClassifica)

        pannello_griglia_carte = self.addPanel(row = 1, column = 0, columnspan = 6, background = "#008000")
        for r in range(6):
            for c in range(6):
                indice_carta = r * 6 + c
                pulsante = pannello_griglia_carte.addButton(text = "", row = r, column = c, command = lambda x = indice_carta: self.rivelaCarta(x))
                pulsante["height"] = 0
                pulsante["width"] = 0
                percorso = self.ottieni_percorso_immagini("retro_carta_rossa_8bit.png")
                foto = self.carica_immagine(percorso)
                pulsante["image"] = foto
                pulsante.image = foto

                self.pulsanti.append(pulsante)
        self.pulsante_accetta = self.addButton(text = "Accetta (1 PA)", row = 3, column = 0, command = self.azioneAccetta, state = "disabled") 
        self.pulsante_rifiuta = self.addButton(text = "Rifiuta (1 PA)", row = 3, column = 1, command = self.azioneRifiuta, state = "disabled")
        self.pulsante_cambia = self.addButton(text = "Cambia (2 PA)", row = 3, column = 2, command = self.azioneCambia, state = "disabled")
        self.pulsante_concludi = self.addButton(text = "Concludi", row = 3, column = 3, command = self.azioneConcludi, state = "disabled")
        self.after(100, self.apriDialog)

    def apriDialog(self):
        partita_in_corso = self.timer_in_corso
        if partita_in_corso:
            self.timer_in_corso = False
            pausa_timer = time.time()
        dialog = DialogoNomi(self)
        if dialog.modified():
            self.timer_in_corso = False
            self.label_timer["text"] = "Tempo: 0s"
            n1, n2 = dialog.risultato
            self.giocatori = [Giocatore(n1), Giocatore(n2)]
            self.numero_round = 1
            self.label_round["text"] = "Round 1"
            self.pulsante_accetta["bg"] = "SystemButtonFace"
            self.pulsante_rifiuta["bg"] = "SystemButtonFace"
            self.pulsante_cambia["bg"] = "SystemButtonFace"
            self.pulsante_concludi["bg"] = "SystemButtonFace"
            self.indice_turno = 0
            self.tempo_inizio = time.time()
            self.timer_in_corso = True
            self.aggiornaTimer()
            self.iniziaRound()
            self.gestisciTurno()
        else:
            if partita_in_corso:
                ripresa_timer = time.time()
                durata_pausa = ripresa_timer - pausa_timer
                self.tempo_inizio += durata_pausa
                self.timer_in_corso = True
                self.aggiornaTimer()
            else:
                sys.exit()

    def aggiornaTimer(self):
        if self.timer_in_corso:
            tempo_trascorso = int(time.time() - self.tempo_inizio)
            self.label_timer["text"] = f"Tempo: {tempo_trascorso}s"
            self.after(1000, self.aggiornaTimer)

    def iniziaRound(self):
        self.mazzo = self.mazzo_gioco.creaMazzo()
        self.griglia_carte_estratte = self.mazzo_gioco.estrai_36()
        self.mappa_possesso = {}
        self.indice_carta_selezionata = None
        self.fase_scambio = False
        for pulsante in self.pulsanti:
            pulsante["text"] = "?"
            pulsante["bg"] = "SystemButtonFace"
            pulsante["state"] = "normal"
        for g in self.giocatori:
            g.reset_round()
        self.gestisciTurno()

    def gestisciTurno(self): 
        giocatore_di_turno = self.giocatori[self.indice_turno]
        if not giocatore_di_turno.concluso:
            giocatore_di_turno.punteggio = giocatore_di_turno.punti_totali + sum(c.valore for c in giocatore_di_turno.mano if c.valore is not None)
        if self.indice_turno == 0:
            colore_attuale = "#87CEFA"
        else:
            colore_attuale = "#FC7868"
        self.label_info["text"] = f"Turno di {giocatore_di_turno.nome}\n Punti Azione: {giocatore_di_turno.punti_azione}\n Punteggio: {giocatore_di_turno.punteggio}\n Mano: {len(giocatore_di_turno.mano)}/5"
        self.label_info["bg"] = colore_attuale
        self.pulsante_accetta["bg"] = colore_attuale
        self.pulsante_rifiuta["bg"] = colore_attuale
        self.pulsante_cambia["bg"] = colore_attuale
        self.pulsante_concludi["bg"] = colore_attuale
        if self.indice_carta_selezionata == None:  
            self.pulsante_accetta["state"] = "disabled"
            self.pulsante_rifiuta["state"] = "disabled"
            self.pulsante_cambia["state"] = "disabled"
            if len(giocatore_di_turno.mano) == 5 and not giocatore_di_turno.concluso:
                self.pulsante_concludi["state"] = "normal"
            else:
                self.pulsante_concludi["state"] = "disabled"
        else: 
            if len(giocatore_di_turno.mano) < 5:
                self.pulsante_accetta["state"] = "normal"
            else:
                self.pulsante_accetta["state"] = "disabled"
            if giocatore_di_turno.punti_azione > 5 - len(giocatore_di_turno.mano):
                self.pulsante_rifiuta["state"] = "normal"
            else:
                self.pulsante_rifiuta["state"] = "disabled"
            if len(giocatore_di_turno.mano) >= 1 and giocatore_di_turno.punti_azione >= 7 - len(giocatore_di_turno.mano):
                self.pulsante_cambia["state"] = "normal"
            else:
                self.pulsante_cambia["state"] = "disabled"
            self.pulsante_concludi["state"] = "disabled"


    def cambiaTurno(self):
        self.indice_carta_selezionata = None
        self.indice_nuova_carta = None
        self.fase_scambio = False
        if (self.giocatori[0].concluso or self.giocatori[0].punti_azione <= 0) and (self.giocatori[1].concluso or self.giocatori[1].punti_azione <= 0):
            self.fineRound()
            return
        indice_prossimo = 1 - self.indice_turno
        prossimo_giocatore = self.giocatori[indice_prossimo]
        if prossimo_giocatore.concluso or prossimo_giocatore.punti_azione <= 0:
            pass 
        else:
            self.indice_turno = indice_prossimo
        indice_attivo = self.indice_turno 
        for i, pulsante in enumerate(self.pulsanti):
            if i in self.mappa_possesso:
                proprietario = self.mappa_possesso[i]
                carta_obj = self.griglia_carte_estratte[i]
                if proprietario == 0:
                    pulsante["bg"] = "#87CEFA" 
                else:
                    pulsante["bg"] = "#FC7868"
                pulsante["state"] = "disabled"
                if proprietario == indice_attivo:
                    pulsante["text"] = str(carta_obj)
                else:
                    percorso = self.ottieni_percorso_immagini("retro_carta_rossa_8bit.png")
                    foto = self.carica_immagine(percorso)
                    pulsante["image"] = foto
                    pulsante.image = foto
            else:
                percorso = self.ottieni_percorso_immagini("retro_carta_rossa_8bit.png")
                foto = self.carica_immagine(percorso)
                pulsante["image"] = foto
                pulsante.image = foto
                if self.giocatori[indice_attivo].punti_azione > 0:
                    pulsante["state"] = "normal"
                else:
                    pulsante["state"] = "disabled"     
        self.gestisciTurno()

    def rivelaCarta(self, indice_carta):
        giocatore_di_turno = self.giocatori[self.indice_turno]
        if self.fase_scambio:
            indice_giocatore = self.mappa_possesso.get(indice_carta)
            if indice_giocatore == self.indice_turno and indice_carta != self.indice_nuova_carta:
                valore_carta = self.griglia_carte_estratte[indice_carta]

                if valore_carta in giocatore_di_turno.mano:
                    giocatore_di_turno.rimuovi_carta(valore_carta)
                nuova_carta = self.griglia_carte_estratte[self.indice_nuova_carta]
                giocatore_di_turno.aggiungi_carta(nuova_carta)

                del self.mappa_possesso[indice_carta]
                self.pulsanti[indice_carta]["text"] = "?"
                self.pulsanti[indice_carta]["bg"] = "SystemButtonFace"
                self.cambiaTurno()
            return
        if self.indice_carta_selezionata is not None or giocatore_di_turno.punti_azione <= 0:
            return
        self.indice_carta_selezionata = indice_carta

        carta_obj = self.griglia_carte_estratte[indice_carta]
        carta_obj.gira_carta()
        if self.indice_turno == 0:
            colore_attuale = "#87CEFA" 
        else:
            colore_attuale = "#FC7868"
        self.pulsanti[indice_carta]["bg"] = colore_attuale
        percorso = self.ottieni_percorso_immagini(carta_obj)
        try:
            self.pulsanti[indice_carta]["width"] = 0
            self.pulsanti[indice_carta]["height"] = 0
            foto = self.carica_immagine(percorso)
            self.pulsanti[indice_carta]["image"] = foto
            self.pulsanti[indice_carta].image = foto
        except Exception as e:
            print({e})
            self.pulsanti[indice_carta]["text"] = str(carta_obj)
        self.gestisciTurno()

    def azioneAccetta(self):
        giocatore_di_turno = self.giocatori[self.indice_turno]

        giocatore_di_turno.punti_azione -= 1
        carta_presa = self.griglia_carte_estratte[self.indice_carta_selezionata]
        if self.indice_carta_selezionata is not None:
            giocatore_di_turno.aggiungi_carta(carta_presa)
            self.pulsanti[self.indice_carta_selezionata]["state"] = "disabled"
            self.mappa_possesso[self.indice_carta_selezionata] = self.indice_turno
        self.cambiaTurno()

    def azioneRifiuta(self):
        self.giocatori[self.indice_turno].punti_azione -= 1

        carta_rifiutata = self.griglia_carte_estratte[self.indice_carta_selezionata]
        carta_rifiutata.gira_carta()

        self.pulsanti[self.indice_carta_selezionata]["text"] = "?"
        self.cambiaTurno()

    def azioneCambia(self):
        giocatore_di_turno = self.giocatori[self.indice_turno]
        giocatore_di_turno.punti_azione -= 2
        self.fase_scambio = True
        self.indice_nuova_carta = self.indice_carta_selezionata
        self.mappa_possesso[self.indice_carta_selezionata] = self.indice_turno
        self.pulsanti[self.indice_carta_selezionata]["state"] = "disabled"
        contatore = 0
        for indice_carta, indice_giocatore in self.mappa_possesso.items():
            if self.indice_turno == 0:
                colore_attuale = "#87CEFA" 
            else:
                colore_attuale = "#FC7868"
            if indice_giocatore == self.indice_turno and indice_carta != self.indice_nuova_carta:
                self.pulsanti[indice_carta]["state"] = "normal"
                self.pulsanti[indice_carta]["bg"] = colore_attuale 
                self.pulsanti[indice_carta]["text"] = str(self.griglia_carte_estratte[indice_carta])
                contatore += 1
        self.pulsante_accetta["state"] = "disabled"
        self.pulsante_rifiuta["state"] = "disabled"
        self.pulsante_cambia["state"] = "disabled"
        self.pulsante_concludi["state"] = "disabled"

    def azioneConcludi(self):
        dialogo = DialogoConcludi(self)
        if not dialogo.confermato:
            return
        self.giocatori[self.indice_turno].concluso = True
        self.pulsante_concludi["state"] = "disabled"
        self.cambiaTurno()

    def fineRound(self):
        self.timer_in_corso = False
        pausa_timer = time.time()
        for giocatore in self.giocatori:
            giocatore.punteggio += giocatore.punti_azione + giocatore.punti_totali
            giocatore.punti_totali = giocatore.punteggio
        if self.giocatori[0].punteggio < 110 and self.giocatori[1].punteggio < 110:
            self.messageBox(title = f"Round {self.numero_round} Terminato", message = "La partita non è ancora terminata, state per inziare un nuovo round.")
            self.numero_round += 1
            self.label_round["text"] = f"Round {self.numero_round}"
            ripresa_timer = time.time()
            durata_pausa = ripresa_timer - pausa_timer
            self.tempo_inizio += durata_pausa
            self.timer_in_corso = True
            self.aggiornaTimer()
            self.iniziaRound()
        else:
            self.finePartita()

    def finePartita(self):
        g1 = self.giocatori[0]
        g2 = self.giocatori[1]
        if g1.punteggio > g2.punteggio:
            testo = f"VINCE {g1.nome}!"
            colore_attuale = "#87CEFA"
        elif g2.punteggio > g1.punteggio:
            testo = f"VINCE {g2.nome}!"
            colore_attuale = "#FC7868"
        else:
            if g1.punti_azione > g2.punti_azione:
                testo = f"VINCE {g1.nome} (Spareggio PA)!"
                colore_attuale = "#87CEFA"
            elif g2.punti_azione > g1.punti_azione:
                testo = f"VINCE {g2.nome} (Spareggio PA)!"
                colore_attuale = "#FC7868"
            else:
                testo = "PAREGGIO!"
        self.label_info["text"] = f"PARTITA TERMINATA\n{testo}"
        self.label_info["bg"] = colore_attuale
        self.pulsante_accetta["state"] = "disabled"
        self.pulsante_accetta["bg"] = "SystemButtonFace"
        self.pulsante_rifiuta["state"] = "disabled"
        self.pulsante_rifiuta["bg"] = "SystemButtonFace"
        self.pulsante_cambia["state"] = "disabled"
        self.pulsante_cambia["bg"] = "SystemButtonFace"
        self.pulsante_concludi["state"] = "disabled"
        self.pulsante_concludi["bg"] = "SystemButtonFace"
        for pulsante in self.pulsanti:
            pulsante["state"] = "disabled"

    def ottieni_percorso_immagini(self, carta):
        if isinstance(carta, str):
            nome_file = f"retro_carta_rossa_8bit.png"
        elif carta.tipoSpeciale:
            nome_file = f"{carta.tipoSpeciale.lower()}.png"
        elif carta.valore:
            nome_file = f"{carta.valore}_di_{carta.seme.lower()}.png"
        return os.path.join("Immagini_mazzo", nome_file)
    
    def carica_immagine(self, percorso):
        immagine_pil = Image.open(percorso)
        immagine_ridimensionata = immagine_pil.resize((55, 70), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(immagine_ridimensionata)










if __name__ == "__main__":
    app = TesoriNascosti()
    app.mainloop()

