from Carta import Carta

class Giocatore:
    def __init__(self, nome):
        self._nome = nome
        self._mano = []
        self._puntiAzione = 15
        self._punteggio = 0
        self._punteggio_totalizzato = 0
        self.concluso = False


    def aggiungi_carta(self, carta):
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

    # def calcola_punteggioMano(self):
        # Usare le funzioni importate da ValidatorePunteggio

    def reset_round(self):
        for carta in self._mano:
            carta.reset()
        self._mano = []
        self._puntiAzione = 15
        self.concluso = False
