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
        self.label_risultato = self.addLabel(text="Nessun nome", row=0, column=0)
        self.after(100, self.apri_dialog)

    def apri_dialog(self):
        dialog = DialogoNomi(self)
        if dialog.modified:
            n1, n2 = dialog.risultato
            self.label_risultato["text"] = f"Giocatori: {n1} vs {n2}"
            self.inizia_partita(n1, n2)
        else:
            self.label_risultato["text"] = "Annullato"






if __name__ == "__main__":
    app = TesoriNascosti()
    app.mainloop()
    