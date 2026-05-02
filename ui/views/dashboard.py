"""FTMS – Dashboard View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QGridLayout, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import math

from ui.theme import C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER, C_BG, C_GREEN, C_RED, C_AMBER
from core.logic import get_dashboard_stats, get_all_sessions, get_all_players, get_monthly_attendance_report
from datetime import date


class StatCard(QFrame):
    def __init__(self, icon: str, label: str, value: str, sub: str = "", color: str = None, parent=None):
        super().__init__(parent)
        self.color = color or C_ACCENT
        self.setFixedHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {self.color};
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Top row: icon + label
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px; color: {self.color};")
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
        top.addWidget(icon_lbl)
        top.addWidget(lbl)
        top.addStretch()
        layout.addLayout(top)

        # Value
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 32px; font-weight: 700;")
        layout.addWidget(self.val_lbl)

        # Sub
        if sub:
            sub_lbl = QLabel(sub)
            sub_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
            layout.addWidget(sub_lbl)

        layout.addStretch()

    def update_value(self, value: str, sub: str = ""):
        self.val_lbl.setText(value)
        if hasattr(self, 'sub_lbl'):
            self.sub_lbl.setText(sub)


class ProgressBarCard(QFrame):
    def __init__(self, icon: str, label: str, value: int, max_value: int, color: str = None, parent=None):
        super().__init__(parent)
        self.color = color or C_ACCENT
        self.setFixedHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Top row: icon + label
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px; color: {self.color};")
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
        top.addWidget(icon_lbl)
        top.addWidget(lbl)
        top.addStretch()
        layout.addLayout(top)

        # Value label
        self.val_lbl = QLabel(f"{value}/{max_value}")
        self.val_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 24px; font-weight: 700;")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.val_lbl)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, max_value)
        self.progress.setValue(value)
        pct = min(100, int((value / max_value) * 100) if max_value > 0 else 0)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {C_BG};
                border: none;
                border-radius: 6px;
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.color};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.progress)

    def update_value(self, value: int, max_value: int):
        self.progress.setRange(0, max_value)
        self.progress.setValue(value)
        self.val_lbl.setText(f"{value}/{max_value}")


class ActivityRow(QFrame):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {C_BORDER};
                border-radius: 0;
            }}
            QFrame:hover {{
                background-color: rgba(255,255,255,0.05);
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        date_lbl = QLabel(session.session_date)
        date_lbl.setStyleSheet(f"color: {C_ACCENT}; font-weight: 600; font-size: 13px; min-width: 110px;")

        focus_lbl = QLabel(session.focus_area or "General Training")
        focus_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 13px; font-weight: 500;")

        # Load indicator
        load_val = session.total_load
        load_color = C_GREEN if load_val < 100 else C_AMBER if load_val < 200 else C_RED
        load_lbl = QLabel(f"Load: {load_val}")
        load_lbl.setStyleSheet(f"color: {load_color}; font-size: 12px; font-weight: 600;")

        drills_lbl = QLabel(f"{len(session.drills)} drills · {session.total_duration} min")
        drills_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
        drills_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(date_lbl)
        layout.addWidget(focus_lbl)
        layout.addWidget(load_lbl)
        layout.addStretch()
        layout.addWidget(drills_lbl)


class MiniStatWidget(QFrame):
    def __init__(self, title: str, value: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; color: {color};")
        
        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 9px; font-weight: 600; letter-spacing: 1px;")
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 18px; font-weight: 700;")
        
        v_layout.addWidget(title_lbl)
        v_layout.addWidget(self.value_lbl)
        
        layout.addWidget(icon_lbl)
        layout.addLayout(v_layout)
        layout.addStretch()
    
    def set_value(self, value: str):
        self.value_lbl.setText(str(value))


class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

        # Auto-refresh every 60s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(60_000)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ── Page title ───────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #E6EDF3;")
        sub = QLabel("Your squad overview at a glance")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 13px; margin-top: 4px;")
        title_row.addWidget(title)
        title_row.addStretch()

        v = QVBoxLayout()
        v.addWidget(title)
        v.addWidget(sub)
        root.addLayout(v)

        # ── Main stat cards ──────────────────────────────────────────────────
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(12)

        self.card_next    = StatCard("📅", "Next Session",     "—",    color=C_ACCENT)
        self.card_injured = StatCard("🏥", "Injured Players",  "0",    color=C_RED)
        self.card_avg_att = StatCard("📊", "Avg Attendance",   "—%",   color=C_GREEN)
        self.card_total   = StatCard("⚽", "Total Sessions",   "0",    color=C_AMBER)
        self.card_squad   = StatCard("👥", "Squad Size",       "0",    color="#00AAFF")

        self.cards_grid.addWidget(self.card_next,    0, 0)
        self.cards_grid.addWidget(self.card_injured, 0, 1)
        self.cards_grid.addWidget(self.card_avg_att, 0, 2)
        self.cards_grid.addWidget(self.card_total,   0, 3)
        self.cards_grid.addWidget(self.card_squad,   0, 4)
        root.addLayout(self.cards_grid)

        # ── Additional stats row ─────────────────────────────────────────────
        self.mini_stats_layout = QHBoxLayout()
        self.mini_stats_layout.setSpacing(12)
        
        self.stat_fit_players = MiniStatWidget("Fit Players", "0", "✅", C_GREEN)
        self.stat_suspended = MiniStatWidget("Suspended", "0", "⚠️", C_AMBER)
        self.stat_avg_load = MiniStatWidget("Avg Session Load", "0", "📈", C_ACCENT)
        self.stat_this_month = MiniStatWidget("Sessions This Month", "0", "🗓️", "#00AAFF")
        
        self.mini_stats_layout.addWidget(self.stat_fit_players)
        self.mini_stats_layout.addWidget(self.stat_suspended)
        self.mini_stats_layout.addWidget(self.stat_avg_load)
        self.mini_stats_layout.addWidget(self.stat_this_month)
        root.addLayout(self.mini_stats_layout)

        # ── Recent sessions ──────────────────────────────────────────────────
        section_lbl = QLabel("RECENT SESSIONS")
        section_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-top: 8px;")
        root.addWidget(section_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.sessions_container = QWidget()
        self.sessions_layout = QVBoxLayout(self.sessions_container)
        self.sessions_layout.setContentsMargins(0, 0, 0, 0)
        self.sessions_layout.setSpacing(0)
        self.sessions_layout.addStretch()

        scroll.setWidget(self.sessions_container)
        scroll.setStyleSheet(f"QScrollArea {{ background: {C_SURFACE}; border: 1px solid {C_BORDER}; border-radius: 12px; }}")
        root.addWidget(scroll, 1)

    def refresh(self):
        stats = get_dashboard_stats()
        all_players = get_all_players()
        all_sessions = get_all_sessions()

        # Next session
        ns = stats["next_session"]
        if ns:
            self.card_next.update_value(ns["session_date"], ns.get("start_time", ""))
        else:
            self.card_next.update_value("None scheduled")

        self.card_injured.update_value(str(stats["injured_count"]))
        self.card_avg_att.update_value(f"{stats['recent_avg_pct']}%")
        self.card_total.update_value(str(stats["total_sessions"]))
        self.card_squad.update_value(str(stats["total_players"]))

        # Additional stats
        fit_count = sum(1 for p in all_players if p.status == "Fit")
        suspended_count = sum(1 for p in all_players if p.status == "Suspended")
        
        self.stat_fit_players.set_value(fit_count)
        self.stat_suspended.set_value(suspended_count)
        
        # Calculate average load
        if all_sessions:
            avg_load = sum(s.total_load for s in all_sessions) / len(all_sessions)
            self.stat_avg_load.set_value(int(avg_load))
        else:
            self.stat_avg_load.set_value(0)
        
        # Sessions this month
        today = date.today()
        sessions_this_month = [s for s in all_sessions if s.session_date.startswith(f"{today.year}-{today.month:02d}")]
        self.stat_this_month.set_value(len(sessions_this_month))

        # Recent sessions list
        while self.sessions_layout.count() > 1:
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recent_sessions = all_sessions[:8]
        if not recent_sessions:
            lbl = QLabel("No sessions yet. Create one in the Calendar tab.")
            lbl.setStyleSheet(f"color: {C_TEXT_SUB}; padding: 30px; font-size: 14px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_layout.insertWidget(0, lbl)
        else:
            for s in recent_sessions:
                row = ActivityRow(s)
                self.sessions_layout.insertWidget(self.sessions_layout.count() - 1, row)
