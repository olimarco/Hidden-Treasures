from collections import Counter

class Validator:
    def __init__(self:
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

    def valutaMano(self, carte, puntiAzioneResidui):
        punteggio_combo = self.calcolaPunteggioCombo(carte)
        return punteggio_combo + puntiAzioneResidui

    def calcolaPunteggioCombo(self, carte):
        punteggio_scala_colore ? self.valutaScaleColori(carte) : self.valutaCombo(carte
        punteggio_gruppi = self.valutaGruppi(carte)
        return max(punteggio_scala_colore, punteggio_gruppi)
    
    def valutaScaleColori(self, carte):
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        if len(carte_numeriche) != 5:
            return 0

        if self.checkScalaReale(carte):
            return self.PUNTEGGI['scala_reale']
        if self.checkColore(carte):
            return self.PUNTEGGI['colore']
        if self.checkScala(carte):
            return self.PUNTEGGI['scala']
        
        return 0

    def valutaGruppi(self, carte):
        punteggio_gemma = self.gestisciGemma(carte)
        punteggio_normale = 0
        if self.checkPoker(carte):
            punteggio_normale = self.PUNTEGGI['poker']
        if self.checkFull(carte):
            punteggio_normale = self.PUNTEGGI['full']
        if self.checkTris(carte):
            punteggio_normale = self.PUNTEGGI['tris']
        if self.checkDoppiaCoppia(carte):
            punteggio_normale = self.PUNTEGGI['doppia_coppia']
        if self.checkCoppia(carte):
            punteggio_normale = self.PUNTEGGI['coppia']
        else:
            punteggio_normale = 0
        
        return max(punteggio_gemma, punteggio_normale)

    def gestisciGemma(self, carte):
        gemme = [c for c in carte if c._tipoSpeciale == 'gemma']
        if not gemme:
            return 0
        
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        valori = [c._valore for c in carte_numeriche]
        conteggio = Counter(valori)

        num_gemme = len(gemme)
        miglior_punteggio = 0

        for valore in range (1,11):
        conteggio = conteggio.copy()
        conteggio[valore] += num_gemme

        counts = sorted(conteggio.values(), reverse=True)

        if counts[0] >= 4:
            return self.PUNTEGGI['poker']
        elif counts[0] == 3 and len(counts) >1 and counts[1] >= 2:
            return self.PUNTEGGI['full']
        elif counts[0] == 3:
            return self.PUNTEGGI['tris']
        elif counts[0] == 2 and len(counts) > 1 and counts[1] >= 2:
            return self.PUNTEGGI['doppia_coppia']
        elif counts[0] == 2:
            return self.PUNTEGGI['coppia']
        else:
            punteggio = 0

        if punteggio > miglior_punteggio:
            miglior_punteggio = punteggio
        return miglior_punteggio

    def checkScalaReale(self, carte):
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        if len(carte_numeriche) != 5:
            return False
        
        semi = [c._seme for c in carte_numeriche]
        if len(set(semi)) != 1:
            return False
        
        valori = sorted([c._valore for c in carte_numeriche])
        if len(set(valorii)) != 5:
            return False
        
        if valori[-1] - valori[0] != 4:
            return False
        
        return 10 in valori

    def checkPoker(self, carte):
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        valori = [c._valore for c in carte_numeriche]
        conteggio = Counter(valori)
        return max(conteggio.values()) >= 4 if conteggio else False

    def checkFull(self, carte):
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        valori = [c._valore for c in carte_numeriche]
        conteggio = Counter(valori)
        counts = sorted(conteggio.values(), reverse=True)
        return len(counts) >=2 and counts[0] == 3 and counts[1] >= 2
    
    def checkColore (self,carte):
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        if len(carte_numeriche) != 5:
            return False
        
        semi = [c._seme for c in carte_numeriche]
        return len(set(semi)) == 1

    def checkScala(self, carte):
        carte_numeriche = [c for c in carte if c._tipoSpeciale is None]
        if len(carte_numeriche) != 5:
            return False
        
        valori = sorted([c._valore for c in carte_numeriche])
        if len(set(valori)) != 5:
            return False
        
        if valori[-1] - valori[0] != 4:
            return True
        
        if valori == [1, 2, 3, 4, 5]:
            return True
        
        return False

    
        
        

    
        
        
