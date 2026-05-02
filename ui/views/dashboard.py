"""FTMS – Dashboard View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ui.theme import C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER, C_BG, C_GREEN, C_RED, C_AMBER
from core.logic import get_dashboard_stats, get_all_sessions, get_all_players


class StatCard(QFrame):
    def __init__(self, icon: str, label: str, value: str, sub: str = "", color: str = None, parent=None):
        super().__init__(parent)
        self.color = color or C_ACCENT
        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {self.color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

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

        # Value
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 28px; font-weight: 700;")
        layout.addWidget(self.val_lbl)

        # Sub
        if sub:
            sub_lbl = QLabel(sub)
            sub_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
            layout.addWidget(sub_lbl)

        layout.addStretch()

    def update_value(self, value: str, sub: str = ""):
        self.val_lbl.setText(value)


class ActivityRow(QFrame):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {C_BORDER};
                border-radius: 0;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        date_lbl = QLabel(session.session_date)
        date_lbl.setStyleSheet(f"color: {C_ACCENT}; font-weight: 600; font-size: 12px; min-width: 100px;")

        focus_lbl = QLabel(session.focus_area or "General Training")
        focus_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 12px;")

        drills_lbl = QLabel(f"{len(session.drills)} drills · {session.total_duration} min")
        drills_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
        drills_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(date_lbl)
        layout.addWidget(focus_lbl)
        layout.addStretch()
        layout.addWidget(drills_lbl)


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
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #E6EDF3;")
        sub = QLabel("Your squad overview at a glance")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 13px; margin-top: 4px;")
        title_row.addWidget(title)
        title_row.addStretch()

        v = QVBoxLayout()
        v.addWidget(title)
        v.addWidget(sub)
        root.addLayout(v)

        # ── Stat cards ───────────────────────────────────────────────────────
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

        # ── Recent sessions ──────────────────────────────────────────────────
        section_lbl = QLabel("RECENT SESSIONS")
        section_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
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

        # Recent sessions list
        while self.sessions_layout.count() > 1:
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sessions = get_all_sessions()[:8]
        if not sessions:
            lbl = QLabel("No sessions yet. Create one in the Calendar tab.")
            lbl.setStyleSheet(f"color: {C_TEXT_SUB}; padding: 20px; font-size: 13px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_layout.insertWidget(0, lbl)
        else:
            for s in sessions:
                row = ActivityRow(s)
                self.sessions_layout.insertWidget(self.sessions_layout.count() - 1, row)
