from breezypythongui import EasyFrame, EasyDialog

class DialogoNomi(EasyDialog):
    def __init__(self, parent):
         super().__init__(parent, "Registrazione Giocatotori")
    def body(self, master):
        self.addLabel(master, text = "Giocatore 1, inserisci il tuo nome", row = 0, column = 0)
        self.campo_g1 = self.addTextField(master, text = "", row = 0, column = 1)
        self.addLabel(master, text = "Giocatore 2, inserisci il tuo nome", row = 1, column = 0)
        self.campo_g2 = self.addTextField(master, text = "", row = 1, column = 1)
    def apply(self):
        nome1 = self.campo_g1.getText()
        nome2 = self.campo_g2.getText()
        self.risultato = (nome1, nome2)

class TesoriNascosti(EasyFrame):
    def __init__(self, title = "Tesori Nascosti - Team 2", width = 1000, height = 1000, background = "#008000"):
        super().__init__(title, width, height, background)
        self.griglia_carte = []
        self.pulsanti = []
        self.label_info = self.addLabel(text = "In attesa dei giocatori", row = 0, column = 0, columnspan = 4, background = "#FFFF00")
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
        self.pulsante_nuova_partita = self.addButton(text = "Nuova Partita", row = 3, column = 4, command = self.apri_dialog)
        
        
        self.after(100, self.apri_dialog)

    def apri_dialog(self):
        dialog = DialogoNomi(self)
        if dialog.modified:
            n1, n2 = dialog.risultato
            self.label_info["text"] = f"Giocatori: {n1} vs {n2}"
            self.inizia_partita(n1, n2)
        else:
           self.quit()
        
    

     

    


if __name__ == "__main__":
    app = TesoriNascosti()
    app.mainloop()
    