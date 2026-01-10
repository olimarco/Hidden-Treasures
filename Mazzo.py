from Carta import Carta
from random import shuffle

class Mazzo:
    """
    Rappresenta il mazzo di carte del gioco. Gestisce la creazione delle istanze Carta standard 
    e speciali, il mescolamento e l'estrazione delle carte da posizionare sulla
    griglia di gioco.
    """
    def __init__(self):
        """
        Inizializza le configurazioni base (lista dei semi, tipi di carte speciali e
        range di valori numerici) e prepara il contenitore vuoto per le carte.
        """
        self._mazzo = []
        self._semi = ["Picche", "Cuori", "Quadri", "Fiori"]
        self._carteSpeciali = ["Moneta", "Pergamena", "Gemma"]
        self._valori = 1, 14

    def creaMazzo(self):
        """
        Riempie il mazzo generando tutte le istanze della classe Carta.
        Crea le carte numeriche per ogni seme e aggiunge le carte speciali uniche.
        Al termine della generazione, mescola automaticamente il mazzo.
        """
        self._mazzo = []
        for i in range(*self._valori):
            for j in self._semi:
                c = Carta(valore=i, seme=j)
                self._mazzo.append(c)
        for i in self._carteSpeciali:
            c = Carta(tipoSpeciale=i)
            self._mazzo.append(c)
        self.mescola()

    def mescola(self):
        """
        Controlla se il mazzo contiene delle carte e le mescola in modo casuale,
        utilizzando l'algoritmo di shuffle.
        """
        if self._mazzo:
            shuffle(self._mazzo)

    def estrai_36(self):
        """
        Preleva e restituisce le prime 36 carte dal mazzo, necessarie per riempire la griglia 
        di gioco 6x6. Le carte estratte vengono rimosse dalla lista principale 
        del mazzo.
        Restituisce una lista vuota se il mazzo contiene meno di 36 carte.
        """
        if len(self._mazzo) < 36:
            return []
        carte_estratte = self._mazzo[:36]
        self._mazzo = self._mazzo[36:]
        return carte_estratte

    def __str__(self):
        """
        Restituisce una stringa informativa che indica quante carte sono 
        attualmente rimaste nel mazzo. Utile principalmente per debug.
        """
        return f"Mazzo con {len(self._mazzo)} carte"