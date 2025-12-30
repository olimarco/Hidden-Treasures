from Carta import Carta

class Giocatore:
    def __init__(self, nome):
        self._nome = nome
        self._mano = []
        self._puntiAzione = 15
        self._punteggio = 0


    def aggiungi_carta(self, carta):
        # Non dimenticare di disabilitare il pulsante, anche se gli errori
        # principali vengono gestiti
        if len(self._mano) < 5:
            self._mano.append(carta)
            carta.assegna_carta(self)

    def rimuovi_carta(self, carta):
        if len(self._mano) > 0:
            try:
                self._mano.remove(carta)
                carta.reset()
            except ValueError:
                return None