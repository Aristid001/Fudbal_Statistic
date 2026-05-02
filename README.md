# ⚽ FTMS — Football Training Management System

A professional desktop application for football coaches to manage training sessions,
track player statistics, and generate PDF reports.

## Tech Stack
- **Python 3.11+**
- **PyQt6** — Modern GUI framework with HiDPI support
- **SQLite** — Embedded relational database
- **ReportLab** — Dark-themed PDF generation
- **PyInstaller** — Compiles to standalone Windows .exe

## Features
- 📊 **Dashboard** — Squad overview: next session, injured count, attendance averages
- 📅 **Calendar** — Interactive session planner with drill builder and attendance register
- 🏋️ **Drill Bank** — 10 pre-loaded industry-standard drills + full CRUD
- 👥 **Squad Hub** — Player profiles with position, status (Fit/Injured/Suspended), jersey numbers
- 📄 **Print Center** — Generate dark-themed A4 PDFs; direct Windows Print Dialog support
- 🧠 **Football Brain** — Training load calculator (Duration × Intensity), high-load warnings

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
cd ftms
python main.py
```

### 3. Compile to Windows .exe
```bash
cd ftms
pyinstaller ftms.spec
```
The executable will appear in `dist/FTMS.exe`.

---

## Project Structure
```
ftms/
├── main.py                  # Entry point
├── requirements.txt
├── ftms.spec                # PyInstaller build config
├── core/
│   ├── database.py          # SQLite schema + seed data
│   ├── logic.py             # Business logic, CRUD, Football Brain
│   └── pdf_engine.py        # ReportLab PDF generation
├── ui/
│   ├── theme.py             # Global QSS stylesheet + shared widgets
│   ├── main_window.py       # Main window + HUD sidebar
│   └── views/
│       ├── dashboard.py     # Dashboard view
│       ├── calendar.py      # Calendar + Session planner
│       ├── drills.py        # Drill Bank view
│       ├── squad.py         # Squad Hub view
│       └── print_center.py  # PDF Print Center
├── data/                    # Auto-created; contains ftms.db
└── exports/                 # Auto-created; PDFs saved here
```

---

## Database Schema

| Table | Key Fields |
|-------|-----------|
| `players` | id, name, position (GK/DEF/MID/FWD), jersey_number, status (Fit/Injured/Suspended) |
| `drills_library` | id, title, category, description, duration_mins, intensity (1–10), positions |
| `training_sessions` | id, session_date, start_time, total_duration, focus_area, notes |
| `session_drills` | session_id ↔ drill_id (many-to-many) |
| `attendance` | session_id, player_id, status (Present/Absent/Excused) |

---

## Pre-loaded Drills
1. 4v4 Small-Sided Game (Tactical, 8/10)
2. Agility Ladder Runs (Physical, 6/10)
3. Positional Possession / Rondo (Tactical, 5/10)
4. Goalkeeper Distribution Drill (Technical, 4/10)
5. Defensive Shape & Pressing Triggers (Tactical, 7/10)
6. Crossing & Finishing Combinations (Technical, 7/10)
7. High-Intensity Interval Sprints (Physical, 9/10)
8. Set Piece – Corner Routines (Set Piece, 5/10)
9. 1v1 Dribbling Challenges (Technical, 6/10)
10. Transition – Counter Attack (Tactical, 8/10)
