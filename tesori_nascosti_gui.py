from breezypythongui import EasyFrame, EasyDialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
import time
from Carta import Carta
from Giocatore import Giocatore
from Mazzo import Mazzo
from validator import Validator
from GestoreClassifica import GestoreClassifica
import os

class DialogoNomi(EasyDialog):
    """
    Questa classe gestisce una finestra di dialogo modale che compare all'avvio.
    Serve per obbligare i due giocatori a inserire i loro nomi prima di iniziare.
    """
    def __init__(self, parent):
         super().__init__(parent, "Registrazione Giocatotori")
    
    def body(self, master):
        """
        Definisce il layout della finestra di dialogo con le etichette e i campi di testo.
        """
        self.addLabel(master, text = "Giocatore 1, inserisci il tuo nome", row = 0, column = 0)
        self.campo_g1 = self.addTextField(master, text = "", row = 0, column = 1)
        self.addLabel(master, text = "Giocatore 2, inserisci il tuo nome", row = 1, column = 0)
        self.campo_g2 = self.addTextField(master, text = "", row = 1, column = 1)
    
    def validate(self):
        """
        Controlla che i campi non siano vuoti quando si preme OK.
        Restituisce False se c'è un errore, impedendo la chiusura della finestra.
        """
        n1 = self.campo_g1.getText().strip()
        n2 = self.campo_g2.getText().strip()
        if n1 == "" or n2 == "":
            self.messageBox(title = "Errore: Nessun Nome Inserito", message = "Entrambi i giocatori devono registrarsi con un nome.")
            return False
        return True
    
    def apply(self):
        """
        Viene chiamato se la validazione ha successo.
        Salva i nomi inseriti in una variabile per poterli usare nella classe principale.
        """
        nome1 = self.campo_g1.getText().strip()
        nome2 = self.campo_g2.getText().strip()
        self.risultato = (nome1, nome2)
        self.setModified()

class DialogoConcludi(EasyDialog):
    """
    Finestra di conferma che appare quando un giocatore decide di passare il turno definitivamente.
    """
    def __init__(self, parent):
        self.confermato = False
        super().__init__(parent, "Concludi Round")
    def body(self, master):
        self.addLabel(master, text="L'azione è definitiva.\nPremi OK per confermare. ", row=0, column=0)
    def apply(self):
        # Se l'utente preme OK, questo flag diventa True
        self.confermato = True


class TesoriNascosti(EasyFrame):
    """
    Classe principale dell'applicazione.
    Gestisce l'intera logica di gioco, la griglia delle carte,
    i turni, i punteggi e le interazioni con l'utente.
    """
    def __init__(self, title = "Tesori Nascosti - Team 2", width = 1000, height = 1000, background = "#008000"):
        super().__init__(title, width, height, background)
       
        # Inizializzazione degli oggetti 
        self.mazzo_gioco = Mazzo()
        self.validator = Validator()
        self.gestore_classifica = GestoreClassifica("classifica.txt")
        self.giocatori = [Giocatore("Giocatore 1"), Giocatore("Giocatore 2")]
        
        # Variabili di stato del gioco
        self.primo_giocatore_round = 0    # Indice di chi inizia il round corrente
        self.indice_turno = 0           # Indice di chi sta effettuando il turno
        self.indice_carta_selezionata = None      # Quale carta è stata cliccata sulla griglia
        self.griglia_carte_estratte = []    # Lista delle 36 carte estratte dal mazzo
        self.pulsanti = []              # Lista dei riferimenti ai pulsanti della griglia
        self.tempo_inizio = 0
        self.timer_in_corso = False
        self.mappa_possesso = {}       # Dizionario che assegna le carte alle mani dei rispettivi giocatori
        
        # Flag per gestire fasi speciali del turno
        self.fase_scambio = False        # True se il giocatore seleziona l'azione "Cambia"
        self.fase_pergamena = False      # True se è attivo l'effetto della Pergamena
        self.indice_nuova_carta = None   # Carta che entra nella mano di gioco dopo lo scambio
        self.numero_round = 1

        # Creazione dell'Interfaccia Grafica

        # Pannello superiore con le etichette di info e di numero round, e il menu
        pannello_griglia_label = self.addPanel(row = 0, column = 0, columnspan = 4, background = "#008000")
        self.label_info = pannello_griglia_label.addLabel(text = "In attesa dei giocatori...", row = 0, column = 0, columnspan = 2)
        self.label_info["anchor"] = "w"      
        self.label_info["justify"] = "left"
        self.label_round = pannello_griglia_label.addLabel(text = f"Round {self.numero_round}", row = 0, column = 1, columnspan = 2, sticky = "NW")
        self.label_timer = pannello_griglia_label.addLabel(text = "Tempo: 0s", row = 0, column = 2, columnspan = 4, sticky = "NW")
        self.menu = pannello_griglia_label.addMenuBar(row = 0, column = 3)
        menu = self.menu.addMenu("Menu")
        menu.addMenuItem("Nuova Partita", command = self.torna_al_menu_principale)
        menu.addMenuItem("Classifica", command = self.mostraClassifica)

        # Preparazione dell'immagine del retro delle carte
        percorso_retro = self.ottieni_percorso_immagini("retro_carta_rossa_8bit.png")
        self.immagine_retro_cache = self.carica_immagine(percorso_retro)
        
        # Creazione del pannello per la griglia 6x6 di pulsanti per le carte
        pannello_griglia_carte = self.addPanel(row = 1, column = 0, columnspan = 6, background = "#008000")
        for r in range(6):
            for c in range(6):
                indice_carta = r * 6 + c
                # Funzione lambda per passare l'indice corretto a ogni pulsante
                pulsante = pannello_griglia_carte.addButton(text = "", row = r, column = c, command = lambda x = indice_carta: self.rivelaCarta(x))
                pulsante["height"] = 0
                pulsante["width"] = 0
                pulsante["image"] = self.immagine_retro_cache
                pulsante.image = self.immagine_retro_cache    # Evita che il garbage collector rimuova l'immagine
                self.pulsanti.append(pulsante)
        
        # Pulsanti di azione
        self.pulsante_accetta = self.addButton(text = "Accetta (1 PA)", row = 3, column = 0, command = self.azioneAccetta, state = "disabled") 
        self.pulsante_rifiuta = self.addButton(text = "Rifiuta (1 PA)", row = 3, column = 1, command = self.azioneRifiuta, state = "disabled")
        self.pulsante_cambia = self.addButton(text = "Cambia (2 PA)", row = 3, column = 2, command = self.azioneCambia, state = "disabled")
        self.pulsante_concludi = self.addButton(text = "Concludi", row = 3, column = 3, command = self.azioneConcludi, state = "disabled")
        self.after(100, self.apriDialog)       # Avvia la richiesta dei nomi dopo breve ritardo per assicurare che la GUI si sia prima caricata

    def apriDialog(self):
        """
        Apre la finestra per l'inserimento nomi. Se confermata, inizializza la partita.
        """
        dialog = DialogoNomi(self)
        if dialog.modified():
            # Reset e setup iniziale post-login
            self.label_timer["text"] = "Tempo: 0s"
            n1, n2 = dialog.risultato
            self.giocatori = [Giocatore(n1), Giocatore(n2)]
            self.primo_giocatore_round = 0 
            self.indice_turno = 0
            self.numero_round = 1
            self.label_round["text"] = "Round 1"
            # Reset colori pulsanti nello stile standard di Windows
            self.pulsante_accetta["bg"] = "SystemButtonFace"
            self.pulsante_rifiuta["bg"] = "SystemButtonFace"
            self.pulsante_cambia["bg"] = "SystemButtonFace"
            self.pulsante_concludi["bg"] = "SystemButtonFace"
            # Avvio timer
            self.tempo_inizio = time.time()
            self.inizio_partita_assoluto = time.time()
            self.timer_in_corso = True
            self.aggiornaTimer()
            # Avvio logica di gioco
            self.iniziaRound()
            self.gestisciTurno()
        else:
            # Se l'utente chiude la finestra nomi senza inserire nulla, torna al menu
            self.torna_al_menu_principale()

    def mostraClassifica(self):
        """
        Chiude la finestra attuale e apre quella della classifica.
        """
        self.destroy()
        from main import Classifica 
        app = Classifica()
        app.mainloop()

    def aggiornaTimer(self):
        """
        Funzione che aggiorna l'etichetta del tempo ogni secondo.
        """
        if self.timer_in_corso:
            tempo_trascorso = int(time.time() - self.tempo_inizio)
            self.label_timer["text"] = f"Tempo: {tempo_trascorso}s"
            # Richiama se stessa dopo 1000ms 
            self.after(1000, self.aggiornaTimer)

    def iniziaRound(self):
        """
        Prepara la griglia per un nuovo round: mescola il mazzo e distribuisce le 36 carte.
        """
        self.indice_turno = self.primo_giocatore_round
        self.mazzo = self.mazzo_gioco.creaMazzo()      # Import da Mazzo.py
        self.griglia_carte_estratte = self.mazzo_gioco.estrai_36()
        self.mappa_possesso = {}      # Resetta i possessori delle carte sulla griglia
        self.indice_carta_selezionata = None
        self.fase_scambio = False

        # Resetta graficamente i pulsanti della griglia
        for pulsante in self.pulsanti:
            pulsante["bg"] = "SystemButtonFace"
            pulsante["state"] = "normal"
        
        # Resetta lo stato dei giocatori
        for g in self.giocatori:
            g.reset_round()             # Import da Giocatore.py
        self.gestisciTurno()

    def gestisciTurno(self): 
        """
        Aggiorna l'interfaccia in base allo stato del giocatore di turno.
        Abilita o disabilita i pulsanti per le azioni in base ai Punti Azione
        e al numero di carte in mano.
        """
        giocatore_di_turno = self.giocatori[self.indice_turno]

        # Calcolo punti provvisorio per mostrare il punteggio in tempo reale
        if not giocatore_di_turno.concluso:
            punti_mano_corrente = self.validator.valutaMano(giocatore_di_turno.mano, giocatore_di_turno.punti_azione)     # Import da validator.py
            giocatore_di_turno.punteggio = giocatore_di_turno.punti_totali + punti_mano_corrente
        
        # Imposta colori diversi per distinguere visivamente i turni
        if self.indice_turno == 0:
            colore_attuale = "#87CEFA"
        else:
            colore_attuale = "#FC7868"
        self.label_info["text"] = f"Turno di {giocatore_di_turno.nome}\n Punti Azione: {giocatore_di_turno.punti_azione}\n Punteggio: {giocatore_di_turno.punteggio}\n Mano: {len(giocatore_di_turno.mano)}/5"
        
        # Aggiorna il colore 
        self.label_info["bg"] = colore_attuale
        self.pulsante_accetta["bg"] = colore_attuale
        self.pulsante_rifiuta["bg"] = colore_attuale
        self.pulsante_cambia["bg"] = colore_attuale
        self.pulsante_concludi["bg"] = colore_attuale

        # Abilitazione pulsanti
        if self.indice_carta_selezionata == None: 
             # Se nessuna carta è selezionata, non è possibile effettuare azioni sulle carte
            self.pulsante_accetta["state"] = "disabled"
            self.pulsante_rifiuta["state"] = "disabled"
            self.pulsante_cambia["state"] = "disabled"
            # Si può concludere solo se si hanno 5 carte nella propria mano
            if len(giocatore_di_turno.mano) == 5 and not giocatore_di_turno.concluso:
                self.pulsante_concludi["state"] = "normal"
            else:
                self.pulsante_concludi["state"] = "disabled"
        else: 
            # Se si seleziona una carta, i pulsanti si attivano in base alle condizioni di gioco
            
            # Accetta: solo se si ha spazio in mano
            if len(giocatore_di_turno.mano) < 5:
                self.pulsante_accetta["state"] = "normal"
            else:
                self.pulsante_accetta["state"] = "disabled"

            # Rifiuta: solo se si hanno abbastanza PA per scartare (costa 1 PA)
            # Nota: il controllo 5 - len(...) serve a garantire che rimangano PA per finire la mano    
            if giocatore_di_turno.punti_azione > 5 - len(giocatore_di_turno.mano):
                self.pulsante_rifiuta["state"] = "normal"
            else:
                self.pulsante_rifiuta["state"] = "disabled"

            # Cambia: costa 2 PA e richiede almeno una carta in mano da scambiare
            # Nota: il controllo 7 - len(...) serve a garantire che rimangano PA per finire la mano    
            if len(giocatore_di_turno.mano) >= 1 and giocatore_di_turno.punti_azione >= 7 - len(giocatore_di_turno.mano):
                self.pulsante_cambia["state"] = "normal"
            else:
                self.pulsante_cambia["state"] = "disabled"
            
            # Non è possibile concludere mentre si ha una carta "in sospeso" selezionata
            self.pulsante_concludi["state"] = "disabled"

    def cambiaTurno(self):
        """
        Gestisce il passaggio del turno all'altro giocatore e aggiorna la visibilità delle carte.
        """
        self.indice_carta_selezionata = None
        self.indice_nuova_carta = None
        self.fase_scambio = False

        # Se entrambi hanno finito, termina il round
        if (self.giocatori[0].concluso or self.giocatori[0].punti_azione <= 0) and (self.giocatori[1].concluso or self.giocatori[1].punti_azione <= 0):
            self.fineRound()
            return
        
        # Calcola indice dell'altro giocatore (0->1, 1->0)
        indice_prossimo = 1 - self.indice_turno
        prossimo_giocatore = self.giocatori[indice_prossimo]

        # Se uno ha finito, tocca ancora all'altro
        if prossimo_giocatore.concluso or prossimo_giocatore.punti_azione <= 0:
            pass 
        else:
            self.indice_turno = indice_prossimo
        indice_attivo = self.indice_turno 
        percorso_retro = self.ottieni_percorso_immagini("retro_carta_rossa_8bit.png")
        foto_retro = self.carica_immagine(percorso_retro)

        # Aggiorna la griglia: nasconde le carte dell'avversario, mostra le proprie
        for i, pulsante in enumerate(self.pulsanti):
            carta_obj = self.griglia_carte_estratte[i]
            if i in self.mappa_possesso:
                # La carta è già stata presa da qualcuno
                proprietario = self.mappa_possesso[i]
                # Applica il colore del proprietario
                if proprietario == 0:
                    pulsante["bg"] = "#87CEFA" 
                else:
                    pulsante["bg"] = "#FC7868" 
                pulsante["state"] = "disabled"

                # La carta viene vista scoperta soltanto da chi ne è il proprietario
                if proprietario == indice_attivo:
                    percorso = self.ottieni_percorso_immagini(carta_obj)
                    foto = self.carica_immagine(percorso)
                    pulsante["image"] = foto
                    pulsante.image = foto
                else:
                    pulsante["image"] = foto_retro
                    pulsante.image = foto_retro
            else:
                # Carta libera sulla griglia
                pulsante["bg"] = "SystemButtonFace"
                # Se non è rivelata permanentemente, mostra il retro
                if not carta_obj.rivelataPermanente:       # Import da Carta.py
                    pulsante["image"] = foto_retro
                    pulsante.image = foto_retro
                else:
                    percorso = self.ottieni_percorso_immagini(carta_obj)
                    foto = self.carica_immagine(percorso)
                    pulsante["image"] = foto
                    pulsante.image = foto
                
                # Se il giocatore ha PA la può cliccare
                if self.giocatori[indice_attivo].punti_azione > 0:
                    pulsante["state"] = "normal"
                else:
                    pulsante["state"] = "disabled"     
        self.gestisciTurno()
    
    def rivelaCarta(self, indice_carta):
        """
        Gestisce il click su una carta della griglia.
        Il comportamento cambia in base alla fase (Normale, Scambio, Pergamena).
        """
        if self.fase_pergamena:
            if indice_carta in self.mappa_possesso:
                self.messageBox("Errore", "Non puoi rivelare una carta già assegnata.")
                return

            carta_obj = self.griglia_carte_estratte[indice_carta]    
            if carta_obj.rivelataPermanente:
                 return
            carta_obj.rivela_permanente()     # Rivela la carta per sempre a tutti
            
            percorso = self.ottieni_percorso_immagini(carta_obj)
            foto = self.carica_immagine(percorso)
            self.pulsanti[indice_carta]["image"] = foto
            self.pulsanti[indice_carta].image = foto
            
            self.fase_pergamena = False
            self.cambiaTurno()
            return
        
        giocatore_di_turno = self.giocatori[self.indice_turno]
        if self.fase_scambio:
            indice_giocatore = self.mappa_possesso.get(indice_carta)
            # Il giocatore deve cliccare una delle carte già possedute per scambiarla
            if indice_giocatore == self.indice_turno and indice_carta != self.indice_nuova_carta:
                valore_carta = self.griglia_carte_estratte[indice_carta]

                # Rimuove la vecchia carta dalla mano e aggiunge quella nuova
                if valore_carta in giocatore_di_turno.mano:
                    giocatore_di_turno.rimuovi_carta(valore_carta)
                nuova_carta = self.griglia_carte_estratte[self.indice_nuova_carta]
                giocatore_di_turno.aggiungi_carta(nuova_carta)

                # Libera la posizione sulla griglia della vecchia carta
                del self.mappa_possesso[indice_carta]
                self.pulsanti[indice_carta]["bg"] = "SystemButtonFace"

                # Controllo immediato effetti speciali della carta appena acquisita
                if nuova_carta.tipoSpeciale in ["Pergamena", "P"]:
                    self.fase_pergamena = True
                    self.messageBox(title = "Effetto Pergamena", message = "Hai scambiato per una Pergamena!\nClicca su una carta della griglia per rivelarla permanentemente.")
                    return
                self.cambiaTurno()
            return
        
        if self.indice_carta_selezionata is not None or giocatore_di_turno.punti_azione <= 0:
            return     # Se il giocatore ha già selezionato una carta o non ha PA, ignora il click
        self.indice_carta_selezionata = indice_carta

        # Gira visivamente la carta solo per il giocatore di turno
        carta_obj = self.griglia_carte_estratte[indice_carta]
        carta_obj.gira_carta()        # Import da Carta.py
        if self.indice_turno == 0:
            colore_attuale = "#87CEFA" 
        else:
            colore_attuale = "#FC7868"
        self.pulsanti[indice_carta]["bg"] = colore_attuale
        percorso = self.ottieni_percorso_immagini(carta_obj)
        try:
            # Reset delle dimensioni per adattare l'immagine
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
        """
        Il giocatore conferma di voler tenere la carta selezionata.
        """
        giocatore_di_turno = self.giocatori[self.indice_turno]

        giocatore_di_turno.punti_azione -= 1  # Costo azione
        carta_presa = self.griglia_carte_estratte[self.indice_carta_selezionata]
        if self.indice_carta_selezionata is not None:
            giocatore_di_turno.aggiungi_carta(carta_presa)         # Import da Giocatore.py
            self.pulsanti[self.indice_carta_selezionata]["state"] = "disabled"
            # Segna la carta come posseduta
            self.mappa_possesso[self.indice_carta_selezionata] = self.indice_turno

            # Effetti istantanei delle carte speciali
            if carta_presa.tipoSpeciale in ["Moneta", "M"]:
                giocatore_di_turno.punti_azione += 1
                self.messageBox(title = "Moneta!", message = "Hai raccolto una Moneta!\nGuadagni +1 Punto Azione extra.")
            
            if carta_presa.tipoSpeciale in ["Pergamena", "P"]:
                self.fase_pergamena = True
                self.messageBox(title = "Effetto Pergamena", message = "Hai trovato una Pergamena!\nClicca su una carta coperta della griglia per rivelarla permanentemente.")
                return

        self.cambiaTurno()

    def azioneRifiuta(self):
        """
        Il giocatore scarta la carta selezionata, la quale torna coperta sulla griglia.
        """
        self.giocatori[self.indice_turno].punti_azione -= 1      # Costo azione

        carta_rifiutata = self.griglia_carte_estratte[self.indice_carta_selezionata]
        carta_rifiutata.gira_carta()   # La copre nuovamente

        self.cambiaTurno()

    def azioneCambia(self):
        """
        Inizia la procedura di scambio: tiene la carta selezionata ma deve esserne scartata una dalla propria mano.
        """
        giocatore_di_turno = self.giocatori[self.indice_turno]
        giocatore_di_turno.punti_azione -= 2     # Costo maggiore per lo scambio
        self.fase_scambio = True

        # Mette in serbo la nuova carta
        self.indice_nuova_carta = self.indice_carta_selezionata
        self.mappa_possesso[self.indice_carta_selezionata] = self.indice_turno
        self.pulsanti[self.indice_carta_selezionata]["state"] = "disabled"

        if self.indice_turno == 0:
            colore_attuale = "#87CEFA" 
        else:
            colore_attuale = "#FC7868"

        # Rende cliccabili le carte che il giocatore possiede già sulla griglia
        for indice_carta, indice_giocatore in self.mappa_possesso.items():
            if indice_giocatore == self.indice_turno and indice_carta != self.indice_nuova_carta:
                self.pulsanti[indice_carta]["state"] = "normal"
                self.pulsanti[indice_carta]["bg"] = colore_attuale 
                carta_obj = self.griglia_carte_estratte[indice_carta]
                percorso = self.ottieni_percorso_immagini(carta_obj)
                try:
                    self.pulsanti[indice_carta]["width"] = 0
                    self.pulsanti[indice_carta]["height"] = 0
                    foto = self.carica_immagine(percorso)
                    self.pulsanti[indice_carta]["image"] = foto
                    self.pulsanti[indice_carta].image = foto 
                except Exception as e:
                    print(f"Errore caricamento immagine scambio: {e}")
                    self.pulsanti[indice_carta]["text"] = str(carta_obj)
                

        # Disabilita gli altri pulsanti finché lo scambio non è finito
        self.pulsante_accetta["state"] = "disabled"
        self.pulsante_rifiuta["state"] = "disabled"
        self.pulsante_cambia["state"] = "disabled"
        self.pulsante_concludi["state"] = "disabled"

    def azioneConcludi(self):
        """
        Apre il dialogo di conferma per terminare il round del giocatore corrente.
        """
        dialogo = DialogoConcludi(self)
        if not dialogo.confermato:
            return
        self.giocatori[self.indice_turno].concluso = True
        self.pulsante_concludi["state"] = "disabled"
        self.cambiaTurno()

    def fineRound(self):
        """
        Calcola i punteggi alla fine del round e stabilisce se continuare o finire la partita.
        """
        self.timer_in_corso = False
        pausa_timer = time.time()

        # Aggiornamento punteggi totali
        for giocatore in self.giocatori:
            punti_round = self.validator.valutaMano(giocatore.mano, giocatore.punti_azione)
            giocatore.punti_totali += punti_round
            giocatore.punteggio = giocatore.punti_totali

        # Controllo condizione di vittoria
        if self.giocatori[0].punteggio < 110 and self.giocatori[1].punteggio < 110:
            # Se nessuno ha vinto, si prepara il prossimo round
            self.label_info["text"] = f"In attesa di iniziare un nuovo round..."
            self.label_info["bg"] = "SystemButtonFace"

            # Reset visuale griglia
            percorso = self.ottieni_percorso_immagini("retro_carta_rossa_8bit.png")
            foto = self.carica_immagine(percorso)
            for pulsante in self.pulsanti:
                pulsante["bg"] = "SystemButtonFace"
                pulsante["state"] = "normal"
                pulsante["image"] = foto
                pulsante.image = foto
            self.pulsante_accetta["state"] = "disabled"
            self.pulsante_accetta["bg"] = "SystemButtonFace"
            self.pulsante_rifiuta["state"] = "disabled"
            self.pulsante_rifiuta["bg"] = "SystemButtonFace"
            self.pulsante_cambia["state"] = "disabled"
            self.pulsante_cambia["bg"] = "SystemButtonFace"
            self.pulsante_concludi["state"] = "disabled"
            self.pulsante_concludi["bg"] = "SystemButtonFace"
            self.messageBox(title = f"Round {self.numero_round} Terminato", message = "Nessun giocatore ha raggiunto la soglia di 110 punti per vincere. State per inziare un nuovo round.")
            
            # Alterna chi inizia per primo nei vari round
            self.primo_giocatore_round = 1 - self.primo_giocatore_round
            self.numero_round += 1
            self.label_round["text"] = f"Round {self.numero_round}"
           
            # Gestione del tempo trascorso durante il messaggio
            ripresa_timer = time.time()
            durata_pausa = ripresa_timer - pausa_timer
            self.tempo_inizio += durata_pausa         # Aggiusta il tempo di inizio per non contare la pausa
            self.timer_in_corso = True
            self.aggiornaTimer()
            self.iniziaRound()
        else:
            self.finePartita()

    def finePartita(self):
        """
        Decreta il vincitore, gestisce pareggi e salva i dati in classifica.
        """
        g1 = self.giocatori[0]
        g2 = self.giocatori[1]

        # Confronto Punteggi
        if g1.punteggio > g2.punteggio:
            testo = f"VINCE {g1.nome}!"
            colore_attuale = "#87CEFA"
            titolo = f"La Vittoria va a {g1.nome}"
            messaggio = f"{g1.nome} ha totalizzato {g1.punteggio} punti."
            vincitore_nome = g1.nome 
            
        elif g2.punteggio > g1.punteggio:
            testo = f"VINCE {g2.nome}!"
            colore_attuale = "#FC7868"
            titolo = f"La Vittoria va a {g2.nome}"
            messaggio = f"{g2.nome} ha totalizzato {g2.punteggio} punti."
            vincitore_nome = g2.nome
            
        else:
            # Spareggio basato sui Punti Azione residui
            if g1.punti_azione > g2.punti_azione:
                testo = f"VINCE {g1.nome} (Spareggio PA)!"
                colore_attuale = "#87CEFA"
                titolo = f"La Vittoria va a {g1.nome}"
                messaggio = f"{g1.nome} ha totalizzato {g1.punteggio} punti, e con {g1.punti_azione} punti azione residui si aggiudica la vittoria."
                vincitore_nome = g1.nome
                
            elif g2.punti_azione > g1.punti_azione:
                testo = f"VINCE {g2.nome} (Spareggio PA)!"
                colore_attuale = "#FC7868"
                titolo = f"La Vittoria va a {g2.nome}"
                messaggio = f"{g2.nome} ha totalizzato {g2.punteggio} punti, e con {g2.punti_azione} punti azione residui si aggiudica la vittoria."
                vincitore_nome = g2.nome
                
            else:
                testo = "PAREGGIO!"
                colore_attuale = "SystemButtonFace"
                testo = "PARITÀ"
                messaggio = "La partita si conclude in pareggio"
                vincitore_nome = "Pareggio"

        # Aggiornamento finale GUI
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
            
        self.messageBox(title = titolo, message = messaggio + "\nPotete consultare i risultati di questa partita in Menu → Classifica.")
        
        # Salvataggio su file tramite GestoreClassifica
        try:
            durata_totale = int(time.time() - self.inizio_partita_assoluto)
            self.gestore_classifica.registra_partita(
                nome1=g1.nome,
                punti1=g1.punteggio,
                pa1=g1.punti_azione,
                nome2=g2.nome,
                punti2=g2.punteggio,
                pa2=g2.punti_azione,
                vincitore=vincitore_nome,
                round_num=self.numero_round,
                durata_secondi=durata_totale
            )
        except Exception as e:
            print(f"Errore salvataggio classifica: {e}")
    
    def ottieni_percorso_immagini(self, carta):
        """
        Costruisce il percorso del file immagine in base al tipo di carta (speciale o numerica).
        """
        if isinstance(carta, str):
            nome_file = f"retro_carta_rossa_8bit.png"
        elif carta.tipoSpeciale:
            nome_file = f"{carta.tipoSpeciale.lower()}.png"
        elif carta.valore:
            nome_file = f"{carta.valore}_di_{carta.seme.lower()}.png"
        return os.path.join("Immagini_mazzo", nome_file)

    def carica_immagine(self, percorso):
        """
        Carica un'immagine e la ridimensiona per adattarla ai pulsanti (55x70).
        Usa il filtro LANCZOS per una migliore qualità.
        """
        immagine_pil = Image.open(percorso)
        immagine_ridimensionata = (immagine_pil.resize((55, 70), Image.Resampling.LANCZOS))
        return ImageTk.PhotoImage(immagine_ridimensionata)

    def torna_al_menu_principale(self):
        """
        Chiude la partita corrente e torna al menu principale.
        """
        self.destroy()
        from main import MenuPrincipale
        app = MenuPrincipale()
        app.mainloop()

if __name__ == "__main__":
    app = TesoriNascosti()
    app.mainloop()