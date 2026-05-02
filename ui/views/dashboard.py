"""FTMS – Futuristic Dashboard View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QGridLayout, QProgressBar, 
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QBrush, QPainter, QPen, QPalette, QGuiApplication
import math

from ui.theme import C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER, C_BG, C_GREEN, C_RED, C_AMBER
from core.logic import get_dashboard_stats, get_all_sessions, get_all_players, get_monthly_attendance_report
from datetime import date


# ── Futuristic Color Palette ─────────────────────────────────────────────────
COLORS = {
    'primary': '#00F0FF',      # Cyan neon
    'secondary': '#7B2CBF',    # Purple neon
    'success': '#00FF88',      # Green neon
    'warning': '#FFAA00',      # Amber neon
    'danger': '#FF2E63',       # Red neon
    'info': '#00AAFF',         # Blue neon
    'bg_dark': '#0A0E17',      # Deep space
    'bg_card': 'rgba(20, 30, 48, 0.7)',
    'bg_card_hover': 'rgba(30, 50, 80, 0.8)',
    'border_glow': 'rgba(0, 240, 255, 0.3)',
    'text_main': '#E6EDF3',
    'text_sub': '#94A3B8',
}


class GlassCard(QFrame):
    """Futuristic glassmorphism card with neon glow effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._hovered = False
        
        # Apply graphics effect before any painting
        self.glow_effect = QGraphicsDropShadowEffect(self)
        self.glow_effect.setBlurRadius(50)
        self.glow_effect.setXOffset(0)
        self.glow_effect.setYOffset(0)
        glow_color = QColor()
        glow_color.setNamedColor(COLORS['primary'])
        glow_color.setAlpha(60)
        self.glow_effect.setColor(glow_color)
        self.setGraphicsEffect(self.glow_effect)
        
        # Base styling
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
    
    def _update_glow(self):
        """Update glow effect based on hover state"""
        if not self.glow_effect:
            return
        if self._hovered:
            self.glow_effect.setBlurRadius(50)
            hover_color = QColor()
            hover_color.setNamedColor(COLORS['primary'])
            hover_color.setAlpha(120)
            self.glow_effect.setColor(hover_color)
        else:
            self.glow_effect.setBlurRadius(50)
            normal_color = QColor()
            normal_color.setNamedColor(COLORS['primary'])
            normal_color.setAlpha(60)
            self.glow_effect.setColor(normal_color)
    
    def enterEvent(self, event):
        self._hovered = True
        self._update_glow()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._hovered = False
        self._update_glow()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        if self._hovered:
            gradient.setColorAt(0, QColor(30, 50, 80, 180))
            gradient.setColorAt(1, QColor(20, 40, 70, 160))
        else:
            gradient.setColorAt(0, QColor(20, 30, 48, 140))
            gradient.setColorAt(1, QColor(15, 25, 40, 120))
        
        painter.setBrush(QBrush(gradient))
        
        # Draw rounded rectangle with glow border
        pen = QPen()
        if self._hovered:
            pen.setColor(QColor(0, 240, 255, 150))
            pen.setWidth(2)
        else:
            pen.setColor(QColor(255, 255, 255, 40))
            pen.setWidth(1)
        
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)


class NeonStatCard(GlassCard):
    """Futuristic stat card with animated neon accents"""
    
    def __init__(self, icon: str, label: str, value: str, sub: str = "", color: str = None, parent=None):
        super().__init__(parent)
        self.color = color or COLORS['primary']
        self.value = value
        self.sub = sub
        self.label = label
        self.icon = icon
        
        self.setFixedHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # Top row: icon + label with neon accent line
        top = QHBoxLayout()
        top.setSpacing(12)
        
        # Icon with glow
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"""
            font-size: 32px;
            color: {self.color};
            font-weight: bold;
        """)
        icon_shadow = QGraphicsDropShadowEffect(icon_lbl)
        icon_shadow.setBlurRadius(20)
        ic_color = QColor()
        ic_color.setNamedColor(self.color)
        icon_shadow.setColor(ic_color)
        icon_lbl.setGraphicsEffect(icon_shadow)
        
        # Label with futuristic styling
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 3px;
            text-transform: uppercase;
        """)
        
        top.addWidget(icon_lbl)
        top.addWidget(lbl)
        top.addStretch()
        
        # Neon accent line
        accent_line = QFrame()
        accent_line.setFixedHeight(2)
        accent_line.setStyleSheet(f"background-color: {self.color}; border-radius: 1px;")
        accent_shadow = QGraphicsDropShadowEffect(accent_line)
        accent_shadow.setBlurRadius(10)
        acc_color = QColor()
        acc_color.setNamedColor(self.color)
        accent_shadow.setColor(acc_color)
        accent_line.setGraphicsEffect(accent_shadow)
        
        layout.addLayout(top)
        layout.addWidget(accent_line)
        
        # Value with large futuristic font
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"""
            color: {COLORS['text_main']};
            font-size: 42px;
            font-weight: 900;
            letter-spacing: -1px;
        """)
        val_shadow = QGraphicsDropShadowEffect(self.val_lbl)
        val_shadow.setBlurRadius(50)
        val_shadow.setColor(QColor(0, 0, 0, 100))
        self.val_lbl.setGraphicsEffect(val_shadow)
        layout.addWidget(self.val_lbl)
        
        # Subtitle
        if sub:
            self.sub_lbl = QLabel(sub)
            self.sub_lbl.setStyleSheet(f"""
                color: {self.color};
                font-size: 14px;
                font-weight: 600;
            """)
            layout.addWidget(self.sub_lbl)
        
        layout.addStretch()
    
    def update_value(self, value: str, sub: str = ""):
        self.val_lbl.setText(str(value))
        if sub and hasattr(self, 'sub_lbl'):
            self.sub_lbl.setText(str(sub))
        elif sub:
            self.sub_lbl = QLabel(sub)
            self.sub_lbl.setStyleSheet(f"""
                color: {self.color};
                font-size: 14px;
                font-weight: 600;
            """)
            self.layout().addWidget(self.sub_lbl)


class FuturisticProgressCard(GlassCard):
    """Modern progress card with gradient bar and circular indicator"""
    
    def __init__(self, icon: str, label: str, value: int, max_value: int, color: str = None, parent=None):
        super().__init__(parent)
        self.color = color or COLORS['primary']
        self.max_value = max_value
        
        self.setFixedHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        
        # Top row
        top = QHBoxLayout()
        top.setSpacing(12)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 28px; color: {self.color};")
        icon_shadow = QGraphicsDropShadowEffect(icon_lbl)
        icon_shadow.setBlurRadius(50)
        ic2_color = QColor()
        ic2_color.setNamedColor(self.color)
        icon_shadow.setColor(ic2_color)
        icon_lbl.setGraphicsEffect(icon_shadow)
        
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 2.5px;
            text-transform: uppercase;
        """)
        
        top.addWidget(icon_lbl)
        top.addWidget(lbl)
        top.addStretch()
        layout.addLayout(top)
        
        # Percentage display
        pct = min(100, int((value / max_value) * 100) if max_value > 0 else 0)
        self.pct_lbl = QLabel(f"{pct}%")
        self.pct_lbl.setStyleSheet(f"""
            color: {self.color};
            font-size: 32px;
            font-weight: 900;
        """)
        self.pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        pct_shadow = QGraphicsDropShadowEffect(self.pct_lbl)
        pct_shadow.setBlurRadius(12)
        pct_color = QColor()
        pct_color.setNamedColor(self.color)
        pct_color.setAlpha(150)
        pct_shadow.setColor(pct_color)
        self.pct_lbl.setGraphicsEffect(pct_shadow)
        layout.addWidget(self.pct_lbl)
        
        # Futuristic progress bar
        self.progress_container = QFrame()
        self.progress_container.setFixedHeight(12)
        self.progress_container.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
        """)
        
        progress_layout = QHBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(2, 2, 2, 2)
        progress_layout.setSpacing(0)
        
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(8)
        self.update_progress(value, max_value)
        
        # Gradient style for progress
        self.progress_bar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.color},
                stop:1 {COLORS['secondary']});
            border-radius: 4px;
        """)
        
        progress_shadow = QGraphicsDropShadowEffect(self.progress_bar)
        progress_shadow.setBlurRadius(50)
        prog_color = QColor()
        prog_color.setNamedColor(self.color)
        prog_color.setAlpha(180)
        progress_shadow.setColor(prog_color)
        self.progress_bar.setGraphicsEffect(progress_shadow)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        layout.addWidget(self.progress_container)
        
        # Value text
        self.val_lbl = QLabel(f"{value}/{max_value}")
        self.val_lbl.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 13px;
            font-weight: 600;
        """)
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.val_lbl)
    
    def update_progress(self, value: int, max_value: int):
        pct = min(100, int((value / max_value) * 100) if max_value > 0 else 0)
        self.progress_bar.setFixedWidth(max(2, int(pct * (self.progress_container.width() - 4) / 100)))
        self.pct_lbl.setText(f"{pct}%")
        self.val_lbl.setText(f"{value}/{max_value}")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'progress_bar') and hasattr(self, 'progress_container'):
            pct = int(self.pct_lbl.text().replace('%', '')) if self.pct_lbl.text() else 0
            self.progress_bar.setFixedWidth(max(2, int(pct * (self.progress_container.width() - 4) / 100)))


class ActivityRow(GlassCard):
    """Futuristic activity row with hover effects"""
    
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(20)
        
        # Date with neon accent
        date_lbl = QLabel(session.session_date)
        date_lbl.setStyleSheet(f"""
            color: {COLORS['primary']};
            font-weight: 800;
            font-size: 15px;
            letter-spacing: 1px;
        """)
        date_shadow = QGraphicsDropShadowEffect(date_lbl)
        date_shadow.setBlurRadius(50)
        date_color = QColor()
        date_color.setNamedColor(COLORS['primary'])
        date_shadow.setColor(date_color)
        date_lbl.setGraphicsEffect(date_shadow)
        
        # Focus area
        focus_lbl = QLabel(session.focus_area or "General Training")
        focus_lbl.setStyleSheet(f"""
            color: {COLORS['text_main']};
            font-size: 14px;
            font-weight: 700;
        """)
        
        # Load indicator with dynamic color
        load_val = session.total_load
        load_color = COLORS['success'] if load_val < 100 else COLORS['warning'] if load_val < 200 else COLORS['danger']
        load_lbl = QLabel(f"LOAD: {load_val}")
        load_lbl.setStyleSheet(f"""
            color: {load_color};
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 1px;
        """)
        load_shadow = QGraphicsDropShadowEffect(load_lbl)
        load_shadow.setBlurRadius(50)
        load_c = QColor()
        load_c.setNamedColor(load_color)
        load_shadow.setColor(load_c)
        load_lbl.setGraphicsEffect(load_shadow)
        
        # Info label
        drills_lbl = QLabel(f"{len(session.drills)} drills · {session.total_duration} min")
        drills_lbl.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 12px;
            font-weight: 500;
        """)
        drills_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(date_lbl)
        layout.addWidget(focus_lbl)
        layout.addWidget(load_lbl)
        layout.addStretch()
        layout.addWidget(drills_lbl)


class CircularStatWidget(GlassCard):
    """Circular progress widget for futuristic stats"""
    
    def __init__(self, title: str, value: int, max_value: int, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.color = color
        self.value = value
        self.max_value = max_value
        self.icon = icon
        self.title = title
        
        self.setFixedSize(140, 160)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)
        
        # Value
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setStyleSheet(f"""
            color: {COLORS['text_main']};
            font-size: 32px;
            font-weight: 900;
        """)
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_shadow = QGraphicsDropShadowEffect(self.value_lbl)
        value_shadow.setBlurRadius(50)
        val_color = QColor()
        val_color.setNamedColor(color)
        val_color.setAlpha(150)
        value_shadow.setColor(val_color)
        self.value_lbl.setGraphicsEffect(value_shadow)
        layout.addWidget(self.value_lbl)
        
        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; color: {color};")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)
    
    def set_value(self, value: int):
        self.value = value
        self.value_lbl.setText(str(value))


class MiniNeonStat(GlassCard):
    """Compact neon stat widget"""
    
    def __init__(self, title: str, value: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.color = color
        
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)
        
        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2);
            border-radius: 12px;
            border: 1px solid {color};
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; color: {color};")
        icon_shadow = QGraphicsDropShadowEffect(icon_lbl)
        icon_shadow.setBlurRadius(50)
        base_color = QColor()
        base_color.setNamedColor(color)
        icon_shadow.setColor(base_color)
        icon_lbl.setGraphicsEffect(icon_shadow)
        icon_layout.addWidget(icon_lbl)
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        """)
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"""
            color: {COLORS['text_main']};
            font-size: 26px;
            font-weight: 900;
        """)
        # Shadow effect with proper color parsing
        base_color = QColor()
        base_color.setNamedColor(color)
        shadow_color = QColor(base_color)
        shadow_color.setAlpha(120)
        
        value_shadow = QGraphicsDropShadowEffect(self.value_lbl)
        value_shadow.setBlurRadius(50)
        value_shadow.setColor(shadow_color)
        self.value_lbl.setGraphicsEffect(value_shadow)
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(self.value_lbl)
        
        layout.addWidget(icon_container)
        layout.addLayout(text_layout)
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
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(28)

        # Set dark background for the whole view
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_dark']};
            }}
        """)

        # ── Page title ───────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("DASHBOARD")
        title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 900;
            color: {COLORS['primary']};
            letter-spacing: 4px;
            text-transform: uppercase;
        """)
        title_shadow = QGraphicsDropShadowEffect(title)
        title_shadow.setBlurRadius(20)
        title_color = QColor()
        title_color.setNamedColor(COLORS['primary'])
        title_shadow.setColor(title_color)
        title.setGraphicsEffect(title_shadow)
        
        sub = QLabel("Your squad overview at a glance")
        sub.setStyleSheet(f"""
            color: {COLORS['text_sub']};
            font-size: 14px;
            font-weight: 400;
            letter-spacing: 1px;
        """)
        
        v = QVBoxLayout()
        v.setSpacing(6)
        v.addWidget(title)
        v.addWidget(sub)
        root.addLayout(v)

        # ── Main stat cards ──────────────────────────────────────────────────
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(20)

        self.card_next    = NeonStatCard("📅", "Next Session",     "—",    color=COLORS['primary'])
        self.card_injured = NeonStatCard("🏥", "Injured Players",  "0",    color=COLORS['danger'])
        self.card_avg_att = NeonStatCard("📊", "Avg Attendance",   "—%",   color=COLORS['success'])
        self.card_total   = NeonStatCard("⚽", "Total Sessions",   "0",    color=COLORS['warning'])
        self.card_squad   = NeonStatCard("👥", "Squad Size",       "0",    color=COLORS['info'])

        self.cards_grid.addWidget(self.card_next,    0, 0)
        self.cards_grid.addWidget(self.card_injured, 0, 1)
        self.cards_grid.addWidget(self.card_avg_att, 0, 2)
        self.cards_grid.addWidget(self.card_total,   0, 3)
        self.cards_grid.addWidget(self.card_squad,   0, 4)
        root.addLayout(self.cards_grid)

        # ── Additional stats row ─────────────────────────────────────────────
        self.mini_stats_layout = QHBoxLayout()
        self.mini_stats_layout.setSpacing(20)
        
        self.stat_fit_players = MiniNeonStat("Fit Players", "0", "✅", COLORS['success'])
        self.stat_suspended = MiniNeonStat("Suspended", "0", "⚠️", COLORS['warning'])
        self.stat_avg_load = MiniNeonStat("Avg Load", "0", "📈", COLORS['primary'])
        self.stat_this_month = MiniNeonStat("This Month", "0", "🗓️", COLORS['info'])
        
        self.mini_stats_layout.addWidget(self.stat_fit_players)
        self.mini_stats_layout.addWidget(self.stat_suspended)
        self.mini_stats_layout.addWidget(self.stat_avg_load)
        self.mini_stats_layout.addWidget(self.stat_this_month)
        root.addLayout(self.mini_stats_layout)

        # ── Recent sessions ──────────────────────────────────────────────────
        section_lbl = QLabel("RECENT SESSIONS")
        section_lbl.setStyleSheet(f"""
            color: {COLORS['primary']};
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 12px;
        """)
        section_shadow = QGraphicsDropShadowEffect(section_lbl)
        section_shadow.setBlurRadius(50)
        shadow_color = QColor()
        shadow_color.setNamedColor(COLORS['primary'])
        shadow_color.setAlpha(150)
        section_shadow.setColor(shadow_color)
        section_lbl.setGraphicsEffect(section_shadow)
        root.addWidget(section_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ 
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.05);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['primary']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self.sessions_container = QWidget()
        self.sessions_container.setStyleSheet(f"background: transparent;")
        self.sessions_layout = QVBoxLayout(self.sessions_container)
        self.sessions_layout.setContentsMargins(0, 0, 0, 0)
        self.sessions_layout.setSpacing(12)
        self.sessions_layout.addStretch()

        scroll.setWidget(self.sessions_container)
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
            self.stat_avg_load.set_value("0")
        
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
            lbl.setStyleSheet(f"""
                color: {COLORS['text_sub']};
                padding: 40px;
                font-size: 15px;
                font-weight: 500;
            """)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_layout.insertWidget(0, lbl)
        else:
            for s in recent_sessions:
                row = ActivityRow(s)
                self.sessions_layout.insertWidget(self.sessions_layout.count() - 1, row)
