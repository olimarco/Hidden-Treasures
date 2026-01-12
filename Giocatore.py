from Carta import Carta

class Giocatore:
    """
    Rappresenta un partecipante alla partita. Questa classe permette di assegnare un nome,
    gestire la sua mano di carte, i Punti Azione e il tracciamento del punteggio,
    e lo stato, cioè se ha concluso o meno il round.
    """
    def __init__(self, nome):
        """
        Costruttore del giocatore. Inizializza il nome e imposta i valori di default 
        per l'inizio della partita: mano vuota, 15 Punti Azione, punteggi azzerati 
        e stato di turno non concluso.
        """
        self._nome = nome
        self._mano = []
        self._puntiAzione = 15
        self._punteggio = 0
        self._punteggio_totalizzato = 0
        self.concluso = False


    def aggiungi_carta(self, carta):
        """
        Controlla che la mano del giocatore non sia già piena (5 carte), e aggiunge una carta.
        In caso di successo, stabilisce anche il legame di proprietà chiamando 
        il metodo assegna_carta() sull'oggetto carta.
        """
        if len(self._mano) < 5:
            self._mano.append(carta)

    def rimuovi_carta(self, carta):
        """
        Rimuove una specifica carta dalla mano del giocatore.
        Se la carta viene trovata e rimossa, viene invocato il metodo reset() su di essa 
        per cancellarne le proprietà.
        Se la carta non è presente, l'eccezione viene gestita silenziosamente.
        """
        if len(self._mano) > 0:
            try:
                self._mano.remove(carta)
                carta.reset()
            except ValueError:
                return None

    """
    Di seguito tutti metodi getter e setter che permettono di accedere e modificare gli attributi
    della classe Giocatore da altri file in cui viene importata.
    """ 
    @property
    def nome(self):
        return self._nome

    @property
    def mano(self):
        return self._mano

    @property
    def punti_azione(self):
        return self._puntiAzione

    @punti_azione.setter
    def punti_azione(self, valore):
        self._puntiAzione = valore

    @property
    def concluso(self):
        return self._concluso
    
    @concluso.setter
    def concluso(self, valore):
        self._concluso = valore

    @property
    def punti_totali(self):
        return self._punteggio_totalizzato

    @punti_totali.setter
    def punti_totali(self, valore):
        self._punteggio_totalizzato = valore

    def reset_round(self):
        """
        Esegue le operazioni di pulizia necessarie per iniziare un nuovo round.
        Resetta tutte le carte attualmente in mano (rimuovendo assegnazioni e stati),
        svuota la lista della mano, ripristina i 15 Punti Azione iniziali 
        e imposta il giocatore come attivo (non concluso).
        """
        for carta in self._mano:
            carta.reset()
        self._mano = []
        self._puntiAzione = 15
        self.concluso = False
