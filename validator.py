from collections import Counter
# Tramite Counter si possono contare le occorrenze di un elemento in una lista

class Validator:
    # definizione attributi
    def __init__(self):
        self.PUNTEGGI = {
            'scala_reale': 100,
            'poker': 50,
            'full': 30,
            'colore': 25,
            'scala': 20,
            'tris': 15,
            'doppia_coppia': 10,
            'coppia': 5,
            'nessuna': 0
        }
# definizione metodi

#valuta la mano del giocatore assegnando il punteggio secondo la consegna

    def valutaMano(self, carte, puntiAzioneResidui):
        punteggio_combo = self.calcolaPunteggioCombo(carte)
        return punteggio_combo + puntiAzioneResidui

#calcola il punteggio della combinazione della mano, ossia quanti punti vale secondo le regole della consegna
    def calcolaPunteggioCombo(self, carte):
        punteggio_scala_colore = self.valutaScaleColori(carte)
        punteggio_gruppi = self.valutaGruppi(carte)
        return max(punteggio_scala_colore, punteggio_gruppi)
    
#Richiama i metodi per controllare se sono presenti le scale, i colori e le scale reali
    def valutaScaleColori(self, carte):
        carte_numeriche = [c for c in carte if c.tipoSpeciale is None]
        if len(carte_numeriche) != 5:
            return 0

        if self.checkScalaReale(carte_numeriche):
            return self.PUNTEGGI['scala_reale']
        if self.checkColore(carte_numeriche):
            return self.PUNTEGGI['colore']
        if self.checkScala(carte_numeriche):
            return self.PUNTEGGI['scala']
        
        return 0

#Richiama i metodi per controllare se è presente un poker, full, tris, doppia coppia, coppia. Se tutti sono false ritorna 0 (nessuna)
    def valutaGruppi(self, carte):
        punteggio_gemma = self.gestisciGemma(carte)

        carte_numeriche = [c for c in carte if c.tipoSpeciale is None]
        if not carte_numeriche:
            return punteggio_gemma

        punteggio_normale = 0
        if self.checkPoker(carte_numeriche):
            punteggio_normale = self.PUNTEGGI['poker']
        elif self.checkFull(carte_numeriche):
            punteggio_normale = self.PUNTEGGI['full']
        elif self.checkTris(carte_numeriche):
            punteggio_normale = self.PUNTEGGI['tris']
        elif self.checkDoppiaCoppia(carte_numeriche):
            punteggio_normale = self.PUNTEGGI['doppia_coppia']
        elif self.checkCoppia(carte_numeriche):
            punteggio_normale = self.PUNTEGGI['coppia']
        else:
            punteggio_normale = 0
        
        return max(punteggio_gemma, punteggio_normale)

    """
    metodo per gestire la carta speciale gemma. La gemma viene trattata come un jolly 
    che assume un valore da 1 a 10 (nessun seme) per creare o migliorare
    una combinazione tra quelle elencate in ValutaGruppi. Tuttavia non può completare scala, colore o scala reale.
    """
    def gestisciGemma(self, carte):
        gemme = [c for c in carte if c.tipoSpeciale in ['G', 'Gemma']]
        if not gemme:
            return 0

        carte_numeriche = [c for c in carte if c.tipoSpeciale is None]
        valori = [c.valore for c in carte_numeriche if c.valore is not None]
        conteggio = Counter(valori)

        if not conteggio:
            return 0

        num_gemme = len(gemme)

        if max(conteggio.values()) < 2:
            return 0

        miglior_punteggio = 0

        for valore_test in conteggio.keys():
            test_conteggio = conteggio.copy()
            test_conteggio[valore_test] += num_gemme

            counts = sorted(test_conteggio.values(), reverse=True)

            if counts[0] >= 4:
                punteggio = self.PUNTEGGI['poker']
            elif counts[0] == 3 and len(counts) > 1 and counts[1] >= 2:
                punteggio = self.PUNTEGGI['full']
            elif counts[0] == 3:
                punteggio = self.PUNTEGGI['tris']
            elif counts[0] == 2 and len(counts) > 1 and counts[1] == 2:
                punteggio = self.PUNTEGGI['doppia_coppia']
            elif counts[0] == 2:
                punteggio = self.PUNTEGGI['coppia']
            else:
                punteggio = 0

            if punteggio > miglior_punteggio:
                miglior_punteggio = punteggio

        return miglior_punteggio

    """
    metodo per controllare se la mano contiene una scala reale.
    Se sono 5 carte, dello stesso seme e valori consecutivi
    (come 6,7,8,9,10) ritorna True.
    """    
    def checkScalaReale(self, carte_numeriche):
        if len(carte_numeriche) != 5:
            return False
        
        semi = [c.seme for c in carte_numeriche]
        if len(set(semi)) != 1:
            return False
        
        valori = sorted([c.valore for c in carte_numeriche])
        if len(set(valori)) != 5:
            return False
        
        if valori[-1] - valori[0] != 4:
            return False
        
        return 10 in valori

    """
    metodo per controllare se la mano contiene un poker.
    Se sono almeno 4 carte di valore uguale ritorna [True]
    """
    def checkPoker(self, carte_numeriche):
        valori = [c.valore for c in carte_numeriche]
        conteggio = Counter(valori)
        return max(conteggio.values()) >= 4 if conteggio else False

    """
    metodo per controllare se la mano contiene un full.
    Attraverso Counter si verifica quante volte appare ogni valore.
    Un full ha frequenze 3 e 2, quindi controlla che la frequenza
    più alta sia 3 e che la seconda più alta sia 2.
    Ritorna True se le condizioni sono soddisfatte,
    False altrimenti.
    """
    def checkFull(self, carte_numeriche):
        valori = [c.valore for c in carte_numeriche]
        conteggio = Counter(valori)
        counts = sorted(conteggio.values(), reverse=True)
        return len(counts) >= 2 and counts[0] == 3 and counts[1] >= 2
    
    """
    metodo per controllare se la mano contiene un colore.
    Se sono 5 carte dello stesso seme indipendamente dal valore ritorna True
    """
    def checkColore (self, carte_numeriche):
        if len(carte_numeriche) != 5:
            return False
        
        semi = [c.seme for c in carte_numeriche]
        return len(set(semi)) == 1

    """
    metodo per controllare se la mano contiene una scala.
    Se sono 5 carte in sequenza indipendamente dal seme ritorna True.
    Vengono inoltre gestiti due casi:
    - uno evita i duplicati, una scala non può avere valori ripetuti
    - uno gestisce la scala bassa (1,2,3,4,5) come caso speciale
    """
    def checkScala(self, carte_numeriche):
        if len(carte_numeriche) != 5:
            return False
        
        valori = sorted([c.valore for c in carte_numeriche])
        if len(set(valori)) != 5:
            return False
        
        if valori[-1] - valori[0] == 4:
            return True
        
        if valori == [1, 2, 3, 4, 5]:
            return True
        
        return False

    """
    metodo per controllare se la mano contiene un tris.
    Se sono 3 carte dello stesso valore
    ma di seme diverso ritorna True
    """
    def checkTris(self, carte_numeriche):
        valori = [c.valore for c in carte_numeriche]
        conteggio = Counter(valori)
        counts = sorted(conteggio.values(), reverse=True)
        return counts[0] == 3 if conteggio else False

    """
    metodo per controllare se la mano contiene una doppia coppia.
    Se sono 2 coppie distinte (tramite counter frequenze: 2, 2, 1)
    e la quinta carta è diversa dalle altre 4 ritorna True
    """
    def checkDoppiaCoppia(self, carte_numeriche):
        valori = [c.valore for c in carte_numeriche]
        conteggio = Counter(valori)
        counts = sorted(conteggio.values(), reverse=True)
        return len(counts) >= 2 and counts[0] == 2 and counts[1] == 2

    """
    metodo per controllare se la mano contiene una coppia.
    Se sono 2 carte dello stesso valore ritorna True
    """
    def checkCoppia (self, carte_numeriche):
        valori = [c.valore for c in carte_numeriche]
        conteggio = Counter(valori)
        return max(conteggio.values()) >= 2 if conteggio else False
