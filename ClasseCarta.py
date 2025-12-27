class Carta:
    def __init__(self, valore, seme, tipoSpeciale):
        self._valore = valore
        self._seme = seme
        self._tipoSpeciale = tipoSpeciale
        self._coperta = True
        self._assegnataA = Giocatore()
        self._rivelataPermanente = False