"""
FTMS - Football Training Management System
Database Layer: SQLite schema + seed data
"""

import sqlite3
import os
from pathlib import Path


def get_db_path() -> str:
    """Resolve DB path relative to executable or script location."""
    if getattr(__import__('sys'), 'frozen', False):
        base = Path(__import__('sys').executable).parent
    else:
        base = Path(__file__).parent.parent
    db_dir = base / "data"
    db_dir.mkdir(exist_ok=True)
    return str(db_dir / "ftms.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Create all tables and seed initial data."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Players ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL,
            position        TEXT    NOT NULL CHECK(position IN ('GK','DEF','MID','FWD')),
            jersey_number   INTEGER,
            status          TEXT    NOT NULL DEFAULT 'Fit' CHECK(status IN ('Fit','Injured','Suspended')),
            date_of_birth   TEXT,
            notes           TEXT,
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Drills Library ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS drills_library (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT    NOT NULL,
            category        TEXT    NOT NULL CHECK(category IN ('Technical','Tactical','Physical','Set Piece')),
            description     TEXT,
            duration_mins   INTEGER NOT NULL DEFAULT 15,
            intensity       INTEGER NOT NULL DEFAULT 5 CHECK(intensity BETWEEN 1 AND 10),
            positions       TEXT    DEFAULT 'ALL',
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Training Sessions ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS training_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date    TEXT    NOT NULL,
            start_time      TEXT    DEFAULT '09:00',
            total_duration  INTEGER DEFAULT 90,
            focus_area      TEXT,
            notes           TEXT,
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Session ↔ Drills (Many-to-Many) ──────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS session_drills (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
            drill_id    INTEGER NOT NULL REFERENCES drills_library(id),
            order_index INTEGER DEFAULT 0
        )
    """)

    # ── Attendance ───────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
            player_id   INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            status      TEXT    NOT NULL DEFAULT 'Present' CHECK(status IN ('Present','Absent','Excused')),
            UNIQUE(session_id, player_id)
        )
    """)

    conn.commit()
    _seed_drills(cur, conn)
    _seed_players(cur, conn)
    conn.close()


def _seed_drills(cur, conn):
    """Insert 10 industry-standard football drills if library is empty."""
    cur.execute("SELECT COUNT(*) FROM drills_library")
    if cur.fetchone()[0] > 0:
        return

    drills = [
        (
            "4v4 Small-Sided Game",
            "Tactical",
            "Fast-paced small-sided match on a compact pitch. Encourages quick decision-making, "
            "pressing, and transition play. Both teams aim to score on small goals. No goalkeeper required.",
            20, 8, "ALL"
        ),
        (
            "Agility Ladder Runs",
            "Physical",
            "Players perform high-knees, lateral shuffles, and in-out steps through agility ladders. "
            "Develops foot speed, coordination, and neuromuscular control. 3 sets per player.",
            12, 6, "ALL"
        ),
        (
            "Positional Possession (Rondo)",
            "Tactical",
            "8v2 or 6v2 keep-away circle. Outer players maintain possession while two defenders press. "
            "Switch defenders every 90 seconds. Trains one-touch play and spatial awareness.",
            15, 5, "MID,FWD"
        ),
        (
            "Goalkeeper Distribution Drill",
            "Technical",
            "GK practices short distribution to defenders under pressure, long kicks to strikers, "
            "and rolling to wide players. Focus on accuracy and consistency over 20 reps.",
            20, 4, "GK"
        ),
        (
            "Defensive Shape & Pressing Triggers",
            "Tactical",
            "Backline holds a compact defensive shape. Coach signals specific triggers (pass to winger, "
            "back pass) and defenders collectively press. Develops unit cohesion and communication.",
            25, 7, "DEF,MID"
        ),
        (
            "Crossing & Finishing Combinations",
            "Technical",
            "Wide players (wingers/fullbacks) deliver crosses from both sides while strikers make "
            "near-post, far-post, and penalty-spot runs. 3 crossers × 10 balls each.",
            20, 7, "FWD,MID"
        ),
        (
            "High-Intensity Interval Sprints",
            "Physical",
            "Players sprint 40m at maximum effort, jog back, repeat. 8 reps with 90-second rest "
            "between sets. Targets anaerobic capacity and match-speed endurance.",
            18, 9, "ALL"
        ),
        (
            "Set Piece – Corner Routines",
            "Set Piece",
            "Practice 4 pre-designed corner kick routines: near-post flick, far-post attack, "
            "short corner combo, and pull-back finish. Defenders work zonal/man marking simultaneously.",
            20, 5, "ALL"
        ),
        (
            "1v1 Dribbling Challenges",
            "Technical",
            "Attackers take on a single defender in a 10×10 metre box to beat them and reach the "
            "end line. Switch attacker/defender every 2 minutes. Builds confidence and dribbling skill.",
            15, 6, "FWD,MID"
        ),
        (
            "Transition – Counter Attack",
            "Tactical",
            "Team A defends and wins the ball, immediately launching a counter-attack with a "
            "numbers-up advantage (3v2, 4v3). Trains speed of transition and forward passing lanes.",
            25, 8, "ALL"
        ),
    ]

    cur.executemany("""
        INSERT INTO drills_library (title, category, description, duration_mins, intensity, positions)
        VALUES (?, ?, ?, ?, ?, ?)
    """, drills)
    conn.commit()


def _seed_players(cur, conn):
    """Insert sample squad if players table is empty."""
    cur.execute("SELECT COUNT(*) FROM players")
    if cur.fetchone()[0] > 0:
        return

    players = [
        ("Marcus Hendry",   "GK",  1, "Fit"),
        ("Jordan Silva",    "DEF", 5, "Fit"),
        ("Tom Breckenridge","DEF", 4, "Fit"),
        ("Leo Vasquez",     "DEF", 3, "Injured"),
        ("Kai Oduya",       "MID", 8, "Fit"),
        ("Soren Larssen",   "MID", 6, "Fit"),
        ("Emre Yilmaz",     "MID",10, "Fit"),
        ("Dante Ferreira",  "FWD", 9, "Fit"),
        ("Nicky Walsh",     "FWD",11, "Fit"),
        ("Cris Montoya",    "FWD", 7, "Suspended"),
    ]

    cur.executemany("""
        INSERT INTO players (name, position, jersey_number, status)
        VALUES (?, ?, ?, ?)
    """, players)
    conn.commit()
