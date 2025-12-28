class Carta:
    def __init__(self, valore=None, seme=None, tipoSpeciale=None):
        self._valore = valore
        self._seme = seme
        self._tipoSpeciale = tipoSpeciale
        self._coperta = True
        self._assegnataA = None
        self._rivelataPermanente = False

    def __str__(self):
        if self._tipoSpeciale:
            return f"{self._tipoSpeciale}"
        elif self._valore and self._seme:
            return f"{self._valore} di {self._seme}"
        return "Carta non valida"

    def assegna_carta(self, giocatore):
        self._assegnataA = giocatore

    def reset(self):
        self._coperta = True
        self._rivelataPermanente = False
        self._assegnataA = None