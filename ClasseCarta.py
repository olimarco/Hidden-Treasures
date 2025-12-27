class Carta:
    def __init__(self, valore, seme, tipoSpeciale):
        self._valore = valore
        self._seme = seme
        self._tipoSpeciale = tipoSpeciale
        self._coperta = True
        self._assegnataA = None
        self._rivelataPermanente = False

    def __str__(self):
        if self._tipoSpeciale == None:
            return f"{self._valore} di {self._seme}"
        else:
            return f"{self._tipoSpeciale}"
        
    def AssegnaCarta(self, giocatore):
        self._assegnataA = giocatore