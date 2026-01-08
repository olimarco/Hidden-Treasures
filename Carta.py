class Carta:
    def __init__(self, valore=None, seme=None, tipoSpeciale=None):
        self._valore = valore
        self._seme = seme
        self._tipoSpeciale = tipoSpeciale
        self._coperta = True
        assengnaA = None
        self._rivelataPermanente = False

    def __str__(self):
        if self._tipoSpeciale:
            return f"{self._tipoSpeciale}"
        elif self._valore and self._seme:
            figure = {11:"Jack", 12:"Regina", 13:"Re", 14:"Asso"}
            if self._valore in figure:
                return f"{figure[self._valore]} di {self._seme}"
            else:
                return f"{self._valore} di {self._seme}"
        return "Carta non valida"
    
    @property
    def valore(self):
        return self._valore

    def assegna_carta(self, giocatore):
        self._assegnataA = giocatore

    def gira_carta(self):
        if not self._rivelataPermanente:
            self._coperta = not self._coperta

    def reset(self):
        self._coperta = True
        self._rivelataPermanente = False
        self._assegnataA = None
