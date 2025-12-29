from Carta import Carta
from random import shuffle

class Mazzo:
    def __init__(self):
        self._mazzo = []
        self._semi = ["Picche", "Cuori", "Quadri", "Fiori"]
        self._carteSpeciali = ["Moneta", "Pergamena", "Gemma"]
        self._valori = 1, 14

    def creaMazzo(self):
        self._mazzo = []
        for i in range(*self._valori):
            for j in self._semi:
                c = Carta(valore=i, seme=j)
                self._mazzo.append(c)
        for i in self._carteSpeciali:
            c = Carta(tipoSpeciale=i)
            self._mazzo.append(c)

    def mescola(self):
        if self._mazzo:
            shuffle(self._mazzo)

    def estrai_36(self):
        if len(self._mazzo) < 36:
            return []
        carte_estratte = self._mazzo[:36]
        self._mazzo = self._mazzo[36:]
        return carte_estratte