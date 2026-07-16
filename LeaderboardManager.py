# LeaderboardManager.py
"""
LeaderboardManager

This module is responsible for:
1) Saving a match row to a TXT file in append mode at the end of a game.
2) Reading the file and rebuilding the leaderboard.

Row format in the file (separator |):
date_iso|duration_seconds|round_num|name1|points1|ap1|name2|points2|ap2|winner

Example:
2026-01-09T15:30:12|245|3|Marco|120|2|Player2|98|0|Marco
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


SEPARATOR = "|"
VALORE_PAREGGIO = "TIE"


@dataclass
class Match:
    date_iso: str
    duration_seconds: int
    round_num: int
    name1: str
    points1: int
    ap1: int
    name2: str
    points2: int
    ap2: int
    winner: str

    @staticmethod
    def _normalize_winner(winner: Optional[str], name1: str, name2: str) -> str:
        """
        Normalizes the winner field.

        Rules:
        - if it is None or empty string it becomes TIE
        - if it doesn't match name1 or name2 it becomes TIE
        - if it matches name1 or name2 it remains as is
        """
        if winner is None:
            return VALORE_PAREGGIO

        w = str(winner).strip()
        if not w:
            return VALORE_PAREGGIO

        # Support both Italian and English tie labels
        if w.upper() in ("PAREGGIO", "TIE", "PARITÀ", "PARITA", "PAREGGIO"):
            return VALORE_PAREGGIO

        if w != name1 and w != name2:
            return VALORE_PAREGGIO

        return w

    @classmethod
    def from_line(cls, line: str) -> Optional[Match]:
        """
        Converts a line from the file into a Match object.
        Returns None if the line is empty or malformed.
        """
        line = line.strip()
        if not line:
            return None

        parts = line.split(SEPARATOR)

        # Compatibility recovery for older rows saved without a winner
        if len(parts) == 9:
            parts.append(VALORE_PAREGGIO)

        if len(parts) != 10:
            return None

        try:
            name1 = parts[3]
            name2 = parts[6]

            winner_ok = cls._normalize_winner(parts[9], name1, name2)

            return cls(
                date_iso=parts[0],
                duration_seconds=int(parts[1]),
                round_num=int(parts[2]),
                name1=name1,
                points1=int(parts[4]),
                ap1=int(parts[5]),
                name2=name2,
                points2=int(parts[7]),
                ap2=int(parts[8]),
                winner=winner_ok,
            )
        except ValueError:
            return None

    def to_line(self) -> str:
        """
        Converts the Match object into a line ready to be saved in the file.
        """
        winner_ok = self._normalize_winner(self.winner, self.name1, self.name2)

        return SEPARATOR.join(
            [
                self.date_iso,
                str(self.duration_seconds),
                str(self.round_num),
                self.name1,
                str(self.points1),
                str(self.ap1),
                self.name2,
                str(self.points2),
                str(self.ap2),
                winner_ok,
            ]
        )


@dataclass
class LeaderboardRow:
    name: str
    wins: int
    matches: int
    best_score: int
    avg_score: float

    def as_text(self) -> str:
        """
        Readable representation for printing to GUI or terminal.
        """
        return (
            f"{self.name} | wins {self.wins} | matches {self.matches} | "
            f"best {self.best_score} | avg {self.avg_score:.1f}"
        )


class LeaderboardManager:
    def __init__(self, filename: str = "leaderboard.txt"):
        """
        filename is the TXT file where the leaderboard is written and read.
        By default it is created in the project folder.
        """
        self.file_path = Path(filename)

    def register_match(
        self,
        name1: str,
        points1: int,
        ap1: int,
        name2: str,
        points2: int,
        ap2: int,
        winner: str,
        round_num: int,
        duration_seconds: int,
        date_iso: Optional[str] = None,
    ) -> None:
        """
        Saves a match row in append mode to the TXT file.
        If date_iso is not passed, it uses the current date.
        """
        if date_iso is None:
            date_iso = datetime.now().isoformat(timespec="seconds")

        winner_ok = Match._normalize_winner(winner, name1, name2)

        match = Match(
            date_iso=date_iso,
            duration_seconds=duration_seconds,
            round_num=round_num,
            name1=name1,
            points1=points1,
            ap1=ap1,
            name2=name2,
            points2=points2,
            ap2=ap2,
            winner=winner_ok,
        )

        if self.file_path.parent:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(match.to_line() + "\n")

    def read_matches(self) -> List[Match]:
        """
        Reads all matches from the file and returns a list of Match objects.
        If the file does not exist, returns an empty list.
        """
        if not self.file_path.exists():
            return []

        matches: List[Match] = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                p = Match.from_line(line)
                if p is not None:
                    matches.append(p)
        return matches

    def calculate_leaderboard(self) -> List[LeaderboardRow]:
        """
        Calculates the leaderboard by aggregating data from all matches.
        Sorting criteria:
        1) wins descending
        2) best score descending
        3) alphabetical name
        """
        matches = self.read_matches()
        if not matches:
            return []

        stats: Dict[str, Dict[str, float]] = {}

        def ensure_player(name: str) -> None:
            if name not in stats:
                stats[name] = {
                    "wins": 0,
                    "matches": 0,
                    "sum_points": 0.0,
                    "best": 0,
                }

        for p in matches:
            ensure_player(p.name1)
            ensure_player(p.name2)

            stats[p.name1]["matches"] += 1
            stats[p.name2]["matches"] += 1

            stats[p.name1]["sum_points"] += p.points1
            stats[p.name2]["sum_points"] += p.points2

            if p.points1 > stats[p.name1]["best"]:
                stats[p.name1]["best"] = p.points1
            if p.points2 > stats[p.name2]["best"]:
                stats[p.name2]["best"] = p.points2

            # Tie does not increment wins for either player
            if p.winner == p.name1:
                stats[p.name1]["wins"] += 1
            elif p.winner == p.name2:
                stats[p.name2]["wins"] += 1

        rows: List[LeaderboardRow] = []
        for name, s in stats.items():
            matches_played = int(s["matches"])
            sum_p = float(s["sum_points"])
            avg = (sum_p / matches_played) if matches_played > 0 else 0.0
            rows.append(
                LeaderboardRow(
                    name=name,
                    wins=int(s["wins"]),
                    matches=matches_played,
                    best_score=int(s["best"]),
                    avg_score=avg,
                )
            )

        rows.sort(key=lambda r: (-r.wins, -r.best_score, r.name.lower()))
        return rows

    def _format_date_short(self, date_iso: str) -> str:
        try:
            dt = datetime.fromisoformat(date_iso)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return date_iso

    def _best_individual_scores(self) -> List[Tuple[str, int, str]]:
        matches = self.read_matches()
        best: Dict[str, Tuple[int, str]] = {}

        for p in matches:
            d = self._format_date_short(p.date_iso)

            if p.name1 not in best or p.points1 > best[p.name1][0]:
                best[p.name1] = (p.points1, d)

            if p.name2 not in best or p.points2 > best[p.name2][0]:
                best[p.name2] = (p.points2, d)

        rows: List[Tuple[str, int, str]] = [(name, points, date) for name, (points, date) in best.items()]
        rows.sort(key=lambda x: (-x[1], x[0].lower()))
        return rows

    def recent_matches_as_text(self, max_rows: int = 10) -> str:
        matches = self.read_matches()
        if not matches:
            return "No matches recorded."

        matches = matches[-max_rows:]

        headers = ["Date", "Dur", "R", "Player 1", "P1", "AP1", "Player 2", "P2", "AP2", "Winner"]
        rows = []
        for p in matches:
            rows.append(
                [
                    self._format_date_short(p.date_iso),
                    f"{p.duration_seconds}s",
                    str(p.round_num),
                    p.name1,
                    str(p.points1),
                    str(p.ap1),
                    p.name2,
                    str(p.points2),
                    str(p.ap2),
                    p.winner,
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
        out.append("RECENT MATCHES")
        out.append(fmt_row(headers))
        out.append(line)
        for r in rows:
            out.append(fmt_row(r))

        return "\n".join(out)

    def leaderboard_as_text(self, max_rows: int = 20) -> str:
        matches = self.read_matches()
        if not matches:
            return "No matches recorded."

        stats: Dict[str, Dict[str, float]] = {}

        def ensure_player(name: str) -> None:
            if name not in stats:
                stats[name] = {
                    "wins": 0,
                    "matches": 0,
                    "sum_points": 0.0,
                    "best": 0,
                    "sum_duration": 0.0,
                }

        for p in matches:
            ensure_player(p.name1)
            ensure_player(p.name2)

            stats[p.name1]["matches"] += 1
            stats[p.name2]["matches"] += 1

            stats[p.name1]["sum_points"] += p.points1
            stats[p.name2]["sum_points"] += p.points2

            stats[p.name1]["sum_duration"] += p.duration_seconds
            stats[p.name2]["sum_duration"] += p.duration_seconds

            if p.points1 > stats[p.name1]["best"]:
                stats[p.name1]["best"] = p.points1
            if p.points2 > stats[p.name2]["best"]:
                stats[p.name2]["best"] = p.points2

            if p.winner == p.name1:
                stats[p.name1]["wins"] += 1
            elif p.winner == p.name2:
                stats[p.name2]["wins"] += 1

        rows: List[Tuple[str, int, int, int, float, float]] = []
        for name, s in stats.items():
            matches_played = int(s["matches"])
            sum_points = float(s["sum_points"])
            avg = (sum_points / matches_played) if matches_played > 0 else 0.0
            best = int(s["best"])
            wins = int(s["wins"])
            avg_duration = (float(s["sum_duration"]) / matches_played) if matches_played > 0 else 0.0
            rows.append((name, wins, matches_played, best, avg, avg_duration))

        rows.sort(key=lambda x: (-x[1], -x[3], -x[4], x[0].lower()))
        rows = rows[:max_rows]

        headers = ["Pos", "Name", "Wins", "Matches", "Best", "Avg", "Avg Duration"]
        formatted_rows = []
        for i, (name, wins, matches_g, best, avg, avg_duration) in enumerate(rows, start=1):
            formatted_rows.append(
                [
                    str(i),
                    name,
                    str(wins),
                    str(matches_g),
                    str(best),
                    f"{avg:.1f}",
                    f"{int(round(avg_duration))}s",
                ]
            )

        widths = [len(h) for h in headers]
        for r in formatted_rows:
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
        out.append("HIDDEN TREASURES LEADERBOARD")
        out.append(fmt_row(headers))
        out.append(line)
        for r in formatted_rows:
            out.append(fmt_row(r))

        out.append("")
        out.append(f"Total matches: {len(matches)}")
        out.append("")
        out.append(self.recent_matches_as_text(max_rows=5))

        return "\n".join(out)
