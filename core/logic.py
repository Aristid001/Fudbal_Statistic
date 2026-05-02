"""
FTMS – Football Brain / Business Logic
Handles training load calculation, drill suggestions, and statistics.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from core.database import get_connection


LOAD_WARNING_THRESHOLD = 8.5  # Intensity threshold per drill
SESSION_LOAD_HARD_CAP  = 200  # Duration × Intensity cap for whole session


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Player:
    id: int
    name: str
    position: str
    jersey_number: Optional[int]
    status: str
    date_of_birth: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def status_color(self) -> str:
        return {"Fit": "#00FFCC", "Injured": "#FF4444", "Suspended": "#FFB300"}.get(self.status, "#FFFFFF")

    @property
    def position_full(self) -> str:
        return {"GK": "Goalkeeper", "DEF": "Defender", "MID": "Midfielder", "FWD": "Forward"}.get(self.position, self.position)


@dataclass
class Drill:
    id: int
    title: str
    category: str
    description: str
    duration_mins: int
    intensity: int
    positions: str = "ALL"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def load(self) -> int:
        return self.duration_mins * self.intensity

    @property
    def intensity_label(self) -> str:
        if self.intensity <= 3: return "Low"
        if self.intensity <= 6: return "Medium"
        if self.intensity <= 8: return "High"
        return "Very High"

    @property
    def intensity_color(self) -> str:
        if self.intensity <= 3: return "#00FFCC"
        if self.intensity <= 6: return "#FFB300"
        if self.intensity <= 8: return "#FF8C00"
        return "#FF4444"


@dataclass
class TrainingSession:
    id: int
    session_date: str
    start_time: str
    total_duration: int
    focus_area: Optional[str]
    notes: Optional[str]
    drills: list[Drill] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def total_load(self) -> int:
        return sum(d.load for d in self.drills)

    @property
    def avg_intensity(self) -> float:
        if not self.drills:
            return 0.0
        return sum(d.intensity for d in self.drills) / len(self.drills)

    @property
    def load_warning(self) -> bool:
        return self.avg_intensity > LOAD_WARNING_THRESHOLD or self.total_load > SESSION_LOAD_HARD_CAP


# ─────────────────────────────────────────────────────────────────────────────
# Player CRUD
# ─────────────────────────────────────────────────────────────────────────────

def get_all_players() -> list[Player]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM players ORDER BY position, name").fetchall()
    return [Player(**dict(r)) for r in rows]


def get_player(player_id: int) -> Optional[Player]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM players WHERE id=?", (player_id,)).fetchone()
    return Player(**dict(row)) if row else None


def save_player(name: str, position: str, jersey_number: Optional[int],
                status: str, date_of_birth: str = "", notes: str = "",
                player_id: Optional[int] = None) -> int:
    with get_connection() as conn:
        if player_id:
            conn.execute("""
                UPDATE players SET name=?, position=?, jersey_number=?, status=?,
                date_of_birth=?, notes=? WHERE id=?
            """, (name, position, jersey_number, status, date_of_birth, notes, player_id))
            return player_id
        else:
            cur = conn.execute("""
                INSERT INTO players (name, position, jersey_number, status, date_of_birth, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, position, jersey_number, status, date_of_birth, notes))
            return cur.lastrowid


def delete_player(player_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM players WHERE id=?", (player_id,))


# ─────────────────────────────────────────────────────────────────────────────
# Drill CRUD
# ─────────────────────────────────────────────────────────────────────────────

def get_all_drills(category: str = "", search: str = "") -> list[Drill]:
    sql = "SELECT * FROM drills_library WHERE 1=1"
    params: list = []
    if category:
        sql += " AND category=?"
        params.append(category)
    if search:
        sql += " AND (title LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY category, title"
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [Drill(**dict(r)) for r in rows]


def get_drill(drill_id: int) -> Optional[Drill]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM drills_library WHERE id=?", (drill_id,)).fetchone()
    return Drill(**dict(row)) if row else None


def suggest_drills_for_position(position: str) -> list[Drill]:
    """Football Brain: return drills relevant to a given position."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM drills_library
            WHERE positions='ALL' OR positions LIKE ?
            ORDER BY intensity DESC
        """, (f"%{position}%",)).fetchall()
    return [Drill(**dict(r)) for r in rows]


def save_drill(title: str, category: str, description: str,
               duration_mins: int, intensity: int, positions: str,
               drill_id: Optional[int] = None) -> int:
    with get_connection() as conn:
        if drill_id:
            conn.execute("""
                UPDATE drills_library SET title=?, category=?, description=?,
                duration_mins=?, intensity=?, positions=? WHERE id=?
            """, (title, category, description, duration_mins, intensity, positions, drill_id))
            return drill_id
        else:
            cur = conn.execute("""
                INSERT INTO drills_library (title, category, description, duration_mins, intensity, positions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, category, description, duration_mins, intensity, positions))
            return cur.lastrowid


def delete_drill(drill_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM drills_library WHERE id=?", (drill_id,))


# ─────────────────────────────────────────────────────────────────────────────
# Session CRUD
# ─────────────────────────────────────────────────────────────────────────────

def get_all_sessions() -> list[TrainingSession]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM training_sessions ORDER BY session_date DESC").fetchall()
        sessions = []
        for r in rows:
            s = TrainingSession(**dict(r), drills=[])
            s.drills = _load_session_drills(conn, s.id)
            sessions.append(s)
    return sessions


def get_session(session_id: int) -> Optional[TrainingSession]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM training_sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            return None
        s = TrainingSession(**dict(row), drills=[])
        s.drills = _load_session_drills(conn, s.id)
    return s


def _load_session_drills(conn, session_id: int) -> list[Drill]:
    rows = conn.execute("""
        SELECT d.* FROM drills_library d
        JOIN session_drills sd ON sd.drill_id = d.id
        WHERE sd.session_id = ?
        ORDER BY sd.order_index
    """, (session_id,)).fetchall()
    return [Drill(**dict(r)) for r in rows]


def save_session(session_date: str, start_time: str, total_duration: int,
                 focus_area: str, notes: str, drill_ids: list[int],
                 session_id: Optional[int] = None) -> int:
    with get_connection() as conn:
        if session_id:
            conn.execute("""
                UPDATE training_sessions SET session_date=?, start_time=?, total_duration=?,
                focus_area=?, notes=? WHERE id=?
            """, (session_date, start_time, total_duration, focus_area, notes, session_id))
            conn.execute("DELETE FROM session_drills WHERE session_id=?", (session_id,))
        else:
            cur = conn.execute("""
                INSERT INTO training_sessions (session_date, start_time, total_duration, focus_area, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (session_date, start_time, total_duration, focus_area, notes))
            session_id = cur.lastrowid

        for i, did in enumerate(drill_ids):
            conn.execute("INSERT INTO session_drills (session_id, drill_id, order_index) VALUES (?,?,?)",
                         (session_id, did, i))
    return session_id


def delete_session(session_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM training_sessions WHERE id=?", (session_id,))


def get_sessions_for_month(year: int, month: int) -> list[TrainingSession]:
    prefix = f"{year}-{month:02d}"
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM training_sessions WHERE session_date LIKE ? ORDER BY session_date",
            (f"{prefix}%",)
        ).fetchall()
        sessions = []
        for r in rows:
            s = TrainingSession(**dict(r), drills=[])
            s.drills = _load_session_drills(conn, s.id)
            sessions.append(s)
    return sessions


# ─────────────────────────────────────────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────────────────────────────────────────

def save_attendance(session_id: int, records: dict[int, str]):
    """records: {player_id: status}"""
    with get_connection() as conn:
        conn.execute("DELETE FROM attendance WHERE session_id=?", (session_id,))
        conn.executemany(
            "INSERT INTO attendance (session_id, player_id, status) VALUES (?,?,?)",
            [(session_id, pid, status) for pid, status in records.items()]
        )


def get_attendance(session_id: int) -> dict[int, str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT player_id, status FROM attendance WHERE session_id=?", (session_id,)
        ).fetchall()
    return {r["player_id"]: r["status"] for r in rows}


def get_monthly_attendance_report(year: int, month: int):
    """Returns list of {player, sessions_present, sessions_total, pct}."""
    prefix = f"{year}-{month:02d}"
    with get_connection() as conn:
        session_ids = [
            r[0] for r in conn.execute(
                "SELECT id FROM training_sessions WHERE session_date LIKE ?", (f"{prefix}%",)
            ).fetchall()
        ]
        if not session_ids:
            return []

        players = conn.execute("SELECT * FROM players ORDER BY name").fetchall()
        results = []
        for p in players:
            total = len(session_ids)
            present = conn.execute("""
                SELECT COUNT(*) FROM attendance
                WHERE player_id=? AND session_id IN ({}) AND status='Present'
            """.format(",".join("?" * total)), [p["id"]] + session_ids).fetchone()[0]
            pct = round(present / total * 100) if total else 0
            results.append({
                "player": Player(**dict(p)),
                "present": present,
                "total": total,
                "pct": pct
            })
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Stats
# ─────────────────────────────────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    from datetime import date
    today = date.today().isoformat()
    with get_connection() as conn:
        next_session = conn.execute("""
            SELECT session_date, start_time FROM training_sessions
            WHERE session_date >= ? ORDER BY session_date LIMIT 1
        """, (today,)).fetchone()

        injured_count = conn.execute(
            "SELECT COUNT(*) FROM players WHERE status='Injured'"
        ).fetchone()[0]

        recent_avg = conn.execute("""
            SELECT AVG(sub.pct) FROM (
                SELECT
                    ts.id,
                    CAST(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS REAL) /
                    NULLIF(COUNT(a.id),0) * 100 AS pct
                FROM training_sessions ts
                LEFT JOIN attendance a ON a.session_id = ts.id
                WHERE ts.session_date < ?
                GROUP BY ts.id
                ORDER BY ts.session_date DESC
                LIMIT 5
            ) sub
        """, (today,)).fetchone()[0]

        total_sessions = conn.execute("SELECT COUNT(*) FROM training_sessions").fetchone()[0]
        total_players  = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]

    return {
        "next_session":   dict(next_session) if next_session else None,
        "injured_count":  injured_count,
        "recent_avg_pct": round(recent_avg or 0, 1),
        "total_sessions": total_sessions,
        "total_players":  total_players,
    }
