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
        self.giocatori = [Giocatore("Giocatore 1"), Giocatore("Giocatore 2")]
        self.indice_turno = 0
        self.indice_carta_selezionata = None
        self.griglia_carte = []
        self.pulsanti = []
        self.tempo_inizio = 0
        self.timer_in_corso = False
        self.mappa_possesso = {}
        self.fase_scambio = False 
        self.indice_nuova_carta = None 
        self.label_info = self.addLabel(text = "In attesa dei giocatori...", row = 0, column = 0, columnspan = 4)
        self.label_info["anchor"] = "w"      
        self.label_info["justify"] = "left"
        self.label_timer = self.addLabel(text = "Tempo: 0s", row = 0, column = 4, columnspan = 2)
        pannello_griglia = self.addPanel(row = 1, column = 0, columnspan = 6, background = "#008000")
        for r in range(6):
            for c in range(6):
                indice_carta = r * 6 + c
                pulsante = pannello_griglia.addButton(text = "?", row = r, column = c, command = lambda x = indice_carta: self.rivelaCarta(x))
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
            if len(giocatore_di_turno.mano) >= 1 and giocatore_di_turno.punti_azione >= 1 + (5 - len(giocatore_di_turno.mano)):
                self.pulsante_cambia["state"] = "normal"
            else:
                self.pulsante_cambia["state"] = "disabled"
            self.pulsante_concludi["state"] = "disabled"
            

    def cambiaTurno(self):
        self.indice_carta_selezionata = None
        self.indice_nuova_carta = None
        self.fase_scambio = False
        for i, pulsante in enumerate(self.pulsanti):
            if i in self.mappa_possesso:
                carta_in_mano = self.mappa_possesso[i]
                if carta_in_mano == 0:
                    pulsante["bg"] = "#87CEFA"
                else:
                    pulsante["bg"] = "#FC7868" 
                pulsante["text"] = str(self.griglia_carte[i])
                pulsante["state"] = "disabled"
            else:
                pulsante["bg"] = "SystemButtonFace"
                pulsante["text"] = "?"    
                pulsante["state"] = "normal"
        indice_prossimo_turno = 1 - self.indice_turno
        if self.giocatori[indice_prossimo_turno].concluso:
            pass 
        else:
            self.indice_turno = indice_prossimo_turno
        self.gestisciTurno()

    def rivelaCarta(self, indice_carta):
        if self.fase_scambio:
            indice_giocatore = self.mappa_possesso.get(indice_carta)
            if indice_giocatore == self.indice_turno and indice_carta != self.indice_nuova_carta:
                giocatore_di_turno = self.giocatori[self.indice_turno]
                valore_carta = self.griglia_carte[indice_carta]
                if valore_carta in giocatore_di_turno.mano:
                    giocatore_di_turno.mano.remove(valore_carta)
                del self.mappa_possesso[indice_carta]
                self.pulsanti[indice_carta]["text"] = "?"
                self.pulsanti[indice_carta]["bg"] = "SystemButtonFace"
                self.cambiaTurno()
            return
        giocatore_di_turno = self.giocatori[self.indice_turno]
        if self.indice_carta_selezionata is not None or giocatore_di_turno.punti_azione <= 0:
            return
        self.indice_carta_selezionata = indice_carta
        if self.indice_turno == 0:
            colore_attuale = "#87CEFA" 
        else:
            colore_attuale = "#FC7868"
        self.pulsanti[indice_carta]["bg"] = colore_attuale
        self.pulsanti[indice_carta]["text"] = str(self.griglia_carte[indice_carta])
        self.gestisciTurno()
    
    def azioneAccetta(self):
        giocatore_di_turno = self.giocatori[self.indice_turno]
        giocatore_di_turno.punti_azione -= 1
        carta_presa = self.griglia_carte[self.indice_carta_selezionata]
        if self.indice_carta_selezionata is not None:
            giocatore_di_turno.mano.append(carta_presa)
            self.pulsanti[self.indice_carta_selezionata]["state"] = "disabled"
            self.mappa_possesso[self.indice_carta_selezionata] = self.indice_turno
        self.cambiaTurno()

    def azioneRifiuta(self):
        self.giocatori[self.indice_turno].punti_azione -= 1
        self.pulsanti[self.indice_carta_selezionata]["text"] = "?"
        self.cambiaTurno()
        
    def azioneCambia(self):
        giocatore_di_turno = self.giocatori[self.indice_turno]
        giocatore_di_turno.punti_azione -= 2
        self.fase_scambio = True
        self.indice_nuova_carta = self.indice_carta_selezionata
        nuova_carta = self.griglia_carte[self.indice_carta_selezionata]
        giocatore_di_turno.mano.append(nuova_carta)
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
                self.pulsanti[indice_carta]["text"] = str(self.griglia_carte[indice_carta])
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
        if self.giocatori[0].concluso and self.giocatori[1].concluso:
            self.fineRound()
        else:
            self.cambiaTurno()

    

    










if __name__ == "__main__":
    app = TesoriNascosti()
    app.mainloop()
    