# GestoreClassifica.py
"""
GestoreClassifica

Questo modulo si occupa di:
1) Salvare a fine partita una riga in un file TXT in modalità append
2) Rileggere il file e ricostruire una classifica

Formato riga nel file (separatore |):
data_iso|durata_secondi|round|nome1|punti1|pa1|nome2|punti2|pa2|vincitore

Esempio:
2026-01-09T15:30:12|245|3|Mario|120|2|Luigi|98|0|Mario
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


SEPARATORE = "|"


@dataclass
class Partita:
    data_iso: str
    durata_secondi: int
    round_num: int
    nome1: str
    punti1: int
    pa1: int
    nome2: str
    punti2: int
    pa2: int
    vincitore: str

    @staticmethod
    def from_line(line: str) -> Optional["Partita"]:
        """
        Converte una riga del file in un oggetto Partita.
        Ritorna None se la riga è vuota o malformata.
        """
        line = line.strip()
        if not line:
            return None

        parts = line.split(SEPARATORE)
        if len(parts) != 10:
            return None

        try:
            return Partita(
                data_iso=parts[0],
                durata_secondi=int(parts[1]),
                round_num=int(parts[2]),
                nome1=parts[3],
                punti1=int(parts[4]),
                pa1=int(parts[5]),
                nome2=parts[6],
                punti2=int(parts[7]),
                pa2=int(parts[8]),
                vincitore=parts[9],
            )
        except ValueError:
            return None

    def to_line(self) -> str:
        """
        Converte l'oggetto Partita in una riga pronta da salvare nel file.
        """
        return SEPARATORE.join(
            [
                self.data_iso,
                str(self.durata_secondi),
                str(self.round_num),
                self.nome1,
                str(self.punti1),
                str(self.pa1),
                self.nome2,
                str(self.punti2),
                str(self.pa2),
                self.vincitore,
            ]
        )


@dataclass
class RigaClassifica:
    nome: str
    vittorie: int
    partite: int
    miglior_punteggio: int
    media_punteggio: float

    def as_text(self) -> str:
        """
        Rappresentazione leggibile per stampa su GUI o terminale.
        """
        return (
            f"{self.nome} | vittorie {self.vittorie} | partite {self.partite} | "
            f"best {self.miglior_punteggio} | media {self.media_punteggio:.1f}"
        )


class GestoreClassifica:
    def __init__(self, nome_file: str = "classifica.txt"):
        """
        nome_file è il file TXT dove scrivere e leggere la classifica.
        Di default viene creato nella cartella del progetto.
        """
        self.percorso_file = Path(nome_file)

    def registra_partita(
        self,
        nome1: str,
        punti1: int,
        pa1: int,
        nome2: str,
        punti2: int,
        pa2: int,
        vincitore: str,
        round_num: int,
        durata_secondi: int,
        data_iso: Optional[str] = None,
    ) -> None:
        """
        Salva una partita in append sul file TXT.
        Se data_iso non viene passata, usa la data attuale.
        """
        if data_iso is None:
            data_iso = datetime.now().isoformat(timespec="seconds")

        partita = Partita(
            data_iso=data_iso,
            durata_secondi=durata_secondi,
            round_num=round_num,
            nome1=nome1,
            punti1=punti1,
            pa1=pa1,
            nome2=nome2,
            punti2=punti2,
            pa2=pa2,
            vincitore=vincitore,
        )

        self.percorso_file.parent.mkdir(parents=True, exist_ok=True)

        with self.percorso_file.open("a", encoding="utf-8") as f:
            f.write(partita.to_line() + "\n")

    def leggi_partite(self) -> List[Partita]:
        """
        Legge tutte le partite dal file e ritorna una lista di Partita.
        Se il file non esiste, ritorna lista vuota.
        """
        if not self.percorso_file.exists():
            return []

        partite: List[Partita] = []
        with self.percorso_file.open("r", encoding="utf-8") as f:
            for line in f:
                p = Partita.from_line(line)
                if p is not None:
                    partite.append(p)
        return partite

    def calcola_classifica(self) -> List[RigaClassifica]:
        """
        Calcola la classifica aggregando i dati di tutte le partite.
        Criterio di ordinamento:
        1) vittorie decrescente
        2) miglior punteggio decrescente
        3) nome alfabetico
        """
        partite = self.leggi_partite()
        if not partite:
            return []

        stats: Dict[str, Dict[str, float]] = {}

        def assicurati(nome: str) -> None:
            if nome not in stats:
                stats[nome] = {
                    "vittorie": 0,
                    "partite": 0,
                    "somma_punti": 0.0,
                    "best": 0,
                }

        for p in partite:
            assicurati(p.nome1)
            assicurati(p.nome2)

            stats[p.nome1]["partite"] += 1
            stats[p.nome2]["partite"] += 1

            stats[p.nome1]["somma_punti"] += p.punti1
            stats[p.nome2]["somma_punti"] += p.punti2

            if p.punti1 > stats[p.nome1]["best"]:
                stats[p.nome1]["best"] = p.punti1
            if p.punti2 > stats[p.nome2]["best"]:
                stats[p.nome2]["best"] = p.punti2

            if p.vincitore == p.nome1:
                stats[p.nome1]["vittorie"] += 1
            elif p.vincitore == p.nome2:
                stats[p.nome2]["vittorie"] += 1
            else:
                pass

        righe: List[RigaClassifica] = []
        for nome, s in stats.items():
            partite_giocate = int(s["partite"])
            somma = float(s["somma_punti"])
            media = (somma / partite_giocate) if partite_giocate > 0 else 0.0
            righe.append(
                RigaClassifica(
                    nome=nome,
                    vittorie=int(s["vittorie"]),
                    partite=partite_giocate,
                    miglior_punteggio=int(s["best"]),
                    media_punteggio=media,
                )
            )

        righe.sort(key=lambda r: (-r.vittorie, -r.miglior_punteggio, r.nome.lower()))
        return righe

    def _formatta_data_breve(self, data_iso: str) -> str:
        try:
            dt = datetime.fromisoformat(data_iso)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return data_iso

    def _migliori_punteggi_singoli(self) -> List[Tuple[str, int, str]]:
        partite = self.leggi_partite()
        best: Dict[str, Tuple[int, str]] = {}

        for p in partite:
            d = self._formatta_data_breve(p.data_iso)

            if p.nome1 not in best or p.punti1 > best[p.nome1][0]:
                best[p.nome1] = (p.punti1, d)

            if p.nome2 not in best or p.punti2 > best[p.nome2][0]:
                best[p.nome2] = (p.punti2, d)

        righe: List[Tuple[str, int, str]] = [(nome, punti, data) for nome, (punti, data) in best.items()]
        righe.sort(key=lambda x: (-x[1], x[0].lower()))
        return righe

    def ultime_partite_come_testo(self, max_righe: int = 10) -> str:
        partite = self.leggi_partite()
        if not partite:
            return "Nessuna partita registrata."

        partite = partite[-max_righe:]

        headers = ["Data", "Dur", "R", "Giocatore 1", "P1", "PA1", "Giocatore 2", "P2", "PA2", "Vincitore"]
        rows = []
        for p in partite:
            rows.append(
                [
                    self._formatta_data_breve(p.data_iso),
                    f"{p.durata_secondi}s",
                    str(p.round_num),
                    p.nome1,
                    str(p.punti1),
                    str(p.pa1),
                    p.nome2,
                    str(p.punti2),
                    str(p.pa2),
                    p.vincitore,
                ]
            )

        widths = [len(h) for h in headers]
        for r in rows:
            for i, cell in enumerate(r):
                widths[i] = max(widths[i], len(cell))

        def fmt_row(cells):
            out = []
            for i, cell in enumerate(cells):
                if i in (4, 5, 7, 8, 2):
                    out.append(cell.rjust(widths[i]))
                else:
                    out.append(cell.ljust(widths[i]))
            return "  ".join(out)

        line = "  ".join("-" * w for w in widths)

        out = []
        out.append("ULTIME PARTITE")
        out.append(fmt_row(headers))
        out.append(line)
        for r in rows:
            out.append(fmt_row(r))

        return "\n".join(out)

    def classifica_come_testo(self, max_righe: int = 20) -> str:
        partite = self.leggi_partite()
        if not partite:
            return "Nessuna partita registrata."

        stats: Dict[str, Dict[str, float]] = {}

        def assicurati(nome: str) -> None:
            if nome not in stats:
                stats[nome] = {
                    "vittorie": 0,
                    "partite": 0,
                    "somma_punti": 0.0,
                    "best": 0,
                    "somma_durata": 0.0,
                }

        for p in partite:
            assicurati(p.nome1)
            assicurati(p.nome2)

            stats[p.nome1]["partite"] += 1
            stats[p.nome2]["partite"] += 1

            stats[p.nome1]["somma_punti"] += p.punti1
            stats[p.nome2]["somma_punti"] += p.punti2

            stats[p.nome1]["somma_durata"] += p.durata_secondi
            stats[p.nome2]["somma_durata"] += p.durata_secondi

            if p.punti1 > stats[p.nome1]["best"]:
                stats[p.nome1]["best"] = p.punti1
            if p.punti2 > stats[p.nome2]["best"]:
                stats[p.nome2]["best"] = p.punti2

            if p.vincitore == p.nome1:
                stats[p.nome1]["vittorie"] += 1
            elif p.vincitore == p.nome2:
                stats[p.nome2]["vittorie"] += 1

        righe: List[Tuple[str, int, int, int, float, float]] = []
        for nome, s in stats.items():
            partite_giocate = int(s["partite"])
            somma_punti = float(s["somma_punti"])
            media = (somma_punti / partite_giocate) if partite_giocate > 0 else 0.0
            best = int(s["best"])
            vittorie = int(s["vittorie"])
            media_durata = (float(s["somma_durata"]) / partite_giocate) if partite_giocate > 0 else 0.0
            righe.append((nome, vittorie, partite_giocate, best, media, media_durata))

        righe.sort(key=lambda x: (-x[1], -x[3], -x[4], x[0].lower()))
        righe = righe[:max_righe]

        headers = ["Pos", "Nome", "Vittorie", "Partite", "Best", "Media", "Durata media"]
        rows = []
        for i, (nome, vittorie, partite_g, best, media, media_durata) in enumerate(righe, start=1):
            rows.append(
                [
                    str(i),
                    nome,
                    str(vittorie),
                    str(partite_g),
                    str(best),
                    f"{media:.1f}",
                    f"{int(round(media_durata))}s",
                ]
            )

        widths = [len(h) for h in headers]
        for r in rows:
            for i, cell in enumerate(r):
                widths[i] = max(widths[i], len(cell))

        def fmt_row(cells):
            out = []
            for i, cell in enumerate(cells):
                if i in (0, 2, 3, 4, 5, 6):
                    out.append(cell.rjust(widths[i]))
                else:
                    out.append(cell.ljust(widths[i]))
            return "  ".join(out)

        line = "  ".join("-" * w for w in widths)

        out: List[str] = []
        out.append("CLASSIFICA TESORI NASCOSTI")
        out.append(fmt_row(headers))
        out.append(line)
        for r in rows:
            out.append(fmt_row(r))

        out.append("")
        out.append(f"Partite totali: {len(partite)}")
        out.append("")
        out.append(self.ultime_partite_come_testo(max_righe=5))

        return "\n".join(out)
