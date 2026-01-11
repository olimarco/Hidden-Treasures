class Carta:
    """
    Rappresenta una carta da gioco, che può essere una carta standard (valore e seme)
    oppure una carta speciale (Moneta, Gemma o pergamena). Gestisce anche lo stato della carta
    (coperta/scoperta) e il giocatore che la possiede.
    """
    def __init__(self, valore=None, seme=None, tipoSpeciale=None):
        """
        Prende come argomenti il valore e il seme, o il tipo speciale,
        e crea i rispettivi attributi, e crea gli attributi che serviranno a
        gestire le altre caratteristiche della carta.
        """
        self._valore = valore
        self._seme = seme
        self._tipoSpeciale = tipoSpeciale
        self._coperta = True
        self._assengnataA = None
        self._rivelataPermanente = False

    def __str__(self):
        """
        Restituisce una rappresentazione testuale della carta.
        Gestisce inoltre i valori numerici delle figure (Jack, Regina, Re, Asso)
        e le carte speciali.
        """
        if self._tipoSpeciale:
            return f"{self._tipoSpeciale}"
        elif self._valore and self._seme:
            figure = {11:"Jack", 12:"Regina", 13:"Re", 14:"Asso"}
            if self._valore in figure:
                return f"{figure[self._valore]} di {self._seme}"
            else:
                return f"{self._valore} di {self._seme}"
        return "Carta non valida"
    
    """
    Di seguito tutti i getter e setter che servono ad accedere e modificare facilmente i 
    valori della carta da altri file
    """
    @property
    def valore(self):
        return self._valore

    @property
    def seme(self):
        return self._seme

    @property
    def tipoSpeciale(self):
        return self._tipoSpeciale
    
    @property
    def rivelataPermanente(self):
        return self._rivelataPermanente

    def assegna_carta(self, giocatore):
        """
        Assegna la carta a uno specifico oggetto Giocatore.
        """
        self._assegnataA = giocatore

    def gira_carta(self):
        """
        Inverte lo stato di visibilità della carta (da coperta a scoperta e viceversa).
        L'azione viene bloccata se la carta è stata rivelata permanentemente dalla pergamena.
        """
        if not self._rivelataPermanente:
            self._coperta = not self._coperta

    def rivela_permanente(self):
        """
        Imposta lo stato della carta come rivelata permanentemente e "scopre la carta",
        permettendo alla gui di gestire facilmente il funzionamento della pergamena
        """
        self._rivelataPermanente = True
        self._coperta = False

    def reset(self):
        """
        Resetta le condizioni iniziali della carta.
        """
        self._coperta = True
        self._rivelataPermanente = False
        self._assegnataA = None
