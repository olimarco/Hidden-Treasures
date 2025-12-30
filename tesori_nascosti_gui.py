from breezypythongui import EasyFrame, EasyDialog
import time
import sys

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

class TesoriNascosti(EasyFrame):
    def __init__(self, title = "Tesori Nascosti - Team 2", width = 1000, height = 1000, background = "#008000"):
        super().__init__(title, width, height, background)
        self.giocatori = [Giocatore("Giocatore 1"), Giocatore("Giocatore 2")]
        self.indice_turno = 0
        self.indice_carta_selezionata = None
        self.griglia_carte = []
        self.pulsanti = []
        self.tempo_inizio = 0
        self.timer_in_corso = False
        self.label_info = self.addLabel(text = "In attesa dei giocatori...", row = 0, column = 0, columnspan = 4)
        self.label_info["anchor"] = "w"      
        self.label_info["justify"] = "left"
        self.label_timer = self.addLabel(text = "Tempo: 0s", row = 0, column = 4, columnspan = 2)
        pannello_griglia = self.addPanel(row = 1, column = 0, columnspan = 6, background = "#008000")
        for r in range(6):
            for c in range(6):
                indice_carta = r * 6 + c
                pulsante = pannello_griglia.addButton(text = "?", row = r, column = c, command = lambda x = indice_carta: self.rivela_carta(x))
                pulsante["width"] = 6
                self.pulsanti.append(pulsante)
        self.pulsante_accetta = self.addButton(text = "Accetta (1 PA)", row = 3, column = 0, command = self.azioneAccetta, state = "disabled") 
        self.pulsante_rifiuta = self.addButton(text = "Rifiuta (1 PA)", row = 3, column = 1, command = self.azioneRifiuta, state = "disabled")
        self.pulsante_cambia = self.addButton(text = "Cambia (2 PA)", row = 3, column = 2, command = self.azioneCambia, state = "disabled")
        self.pulsante_concludi = self.addButton(text = "Concludi", row = 3, column = 3, command = self.azioneConcludi, state = "disabled")
        
        
        
        self.after(100, self.apriDialog)

    def apriDialog(self):
        dialog = DialogoNomi(self)
        if dialog.modified():
            n1, n2 = dialog.risultato
            self.giocatori = [Giocatore(n1), Giocatore(n2)]
            self.indice_turno = 0
            self.tempo_inizio = time.time()
            self.timer_in_corso = True
            self.aggiornaTimer()
            self.iniziaRound()
            self.gestisciTurno()
        else:
            sys.exit()

    def aggiornaTimer(self):
        if self.timer_in_corso:
            tempo_trascorso = int(time.time() - self.tempo_inizio)
            self.label_timer["text"] = f"Tempo: {tempo_trascorso}s"
            self.after(1000, self.aggiornaTimer)

    def iniziaRound(self):
        self.griglia_carte = self.estrai_carte(36)
        for pulsante in self.pulsanti:
            pulsante["text"] = "?"
            pulsante["bg"] = "SystemButtonFace"
            pulsante["state"] = "normal"
        for g in self.giocatori:
            g.reset_round()
        self.gestisciTurno()

    def gestisciTurno(self): 
        giocatore_di_turno = self.giocatori[self.indice_turno]
        if self.indice_turno == 0:
            colore_attuale = "#87CEFA"
        else:
            colore_attuale = "#FC7868"
        self.label_info["text"] = f"Turno di {giocatore_di_turno.nome}\n Punti Azione: {giocatore_di_turno.punti_azione}\n Punti Totali: {giocatore_di_turno.punti_totali}\n Mano: {len(giocatore_di_turno.mano)}/5"
        self.label_info["bg"] = colore_attuale
        self.pulsante_accetta["bg"] = colore_attuale
        self.pulsante_rifiuta["bg"] = colore_attuale
        self.pulsante_cambia["bg"] = colore_attuale
        self.pulsante_concludi["bg"] = colore_attuale
        if self.indice_carta_selezionata == None:  
            self.pulsante_accetta["state"] = "disabled"
            self.pulsante_rifiuta["state"] = "disabled"
            self.pulsante_cambia["state"] = "disabled"
        else: 
            self.pulsante_accetta["state"] = "normal"
            self.pulsante_rifiuta["state"] = "normal"
            self.pulsante_cambia["state"] = "normal"
        if len(giocatore_di_turno.mano) == 5 and not giocatore_di_turno.concluso:
            self.pulsante_concludi["state"] = "normal"
        else:
            self.pulsante_concludi["state"] = "disabled"
            
    def cambiaTurno(self):
        self.indice_carta_selezionata = None
        for pulsante in self.pulsanti:
            pulsante["bg"] = "SystemButtonFace"
        self.indice_turno = 1 - self.indice_turno
        self.gestisciTurno()


    



    
    





if __name__ == "__main__":
    app = TesoriNascosti()
    app.mainloop()
    