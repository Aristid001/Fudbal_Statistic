"""
FTMS – UI Theme
Centralised QSS stylesheet + shared widget helpers.
"""

from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon, QPixmap, QPainter
import math

# ─── Colour palette ──────────────────────────────────────────────────────────
C_BG         = "#0D1117"
C_SURFACE    = "#161B22"
C_SURFACE2   = "#1C2128"
C_BORDER     = "#21262D"
C_BORDER2    = "#30363D"
C_TEXT       = "#E6EDF3"
C_TEXT_SUB   = "#8B949E"
C_ACCENT     = "#00FFCC"      # Neon Mint
C_ACCENT2    = "#00AAFF"      # Electric Blue
C_RED        = "#FF4444"
C_AMBER      = "#FFB300"
C_GREEN      = "#3FB950"


GLOBAL_QSS = f"""
/* ── Global ───────────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "Inter", "SF Pro Display", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}}

/* ── Scrollbars ───────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {C_SURFACE};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER2};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {C_ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {C_SURFACE};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {C_BORDER2};
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{ background: {C_ACCENT}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── QLineEdit / QTextEdit ────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {C_SURFACE};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {C_ACCENT};
    selection-color: {C_BG};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {C_ACCENT};
}}

/* ── QComboBox ────────────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {C_SURFACE};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 120px;
}}
QComboBox:hover {{ border: 1px solid {C_ACCENT}; }}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {C_SURFACE2};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    selection-background-color: {C_ACCENT};
    selection-color: {C_BG};
    padding: 4px;
}}

/* ── QSpinBox / QDateEdit / QTimeEdit ────────────────────────────────────── */
QSpinBox, QDateEdit, QTimeEdit {{
    background-color: {C_SURFACE};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
}}
QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {{
    border: 1px solid {C_ACCENT};
}}
QSpinBox::up-button, QSpinBox::down-button,
QDateEdit::up-button, QDateEdit::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {{
    background: {C_BORDER};
    border: none;
    width: 18px;
    border-radius: 3px;
}}

/* ── QPushButton – primary ────────────────────────────────────────────────── */
QPushButton {{
    background-color: {C_SURFACE};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {C_SURFACE2};
    border: 1px solid {C_ACCENT};
    color: {C_ACCENT};
}}
QPushButton:pressed {{
    background-color: {C_BORDER};
}}
QPushButton[accent="true"] {{
    background-color: {C_ACCENT};
    color: {C_BG};
    border: none;
    font-weight: 700;
}}
QPushButton[accent="true"]:hover {{
    background-color: #33FFDA;
    color: {C_BG};
}}
QPushButton[danger="true"] {{
    background-color: transparent;
    color: {C_RED};
    border: 1px solid {C_RED};
}}
QPushButton[danger="true"]:hover {{
    background-color: {C_RED};
    color: white;
}}

/* ── QTableWidget ─────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {C_SURFACE};
    alternate-background-color: {C_SURFACE2};
    gridline-color: {C_BORDER};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {C_BORDER};
}}
QTableWidget::item:selected {{
    background-color: rgba(0,255,204,0.15);
    color: {C_ACCENT};
}}
QHeaderView::section {{
    background-color: {C_SURFACE2};
    color: {C_TEXT_SUB};
    border: none;
    border-bottom: 1px solid {C_BORDER};
    padding: 8px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ── QTabWidget ───────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {C_BORDER};
    border-radius: 0 8px 8px 8px;
    background-color: {C_SURFACE};
}}
QTabBar::tab {{
    background: {C_SURFACE2};
    color: {C_TEXT_SUB};
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    border: 1px solid {C_BORDER};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background: {C_ACCENT};
    color: {C_BG};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    background: {C_BORDER};
    color: {C_TEXT};
}}

/* ── QDialog ──────────────────────────────────────────────────────────────── */
QDialog {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 12px;
}}

/* ── QMessageBox ──────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {C_SURFACE};
}}

/* ── QListWidget ──────────────────────────────────────────────────────────── */
QListWidget {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 4px;
}}
QListWidget::item {{
    padding: 6px 10px;
    border-radius: 4px;
    margin-bottom: 2px;
}}
QListWidget::item:selected {{
    background-color: rgba(0,255,204,0.15);
    color: {C_ACCENT};
}}
QListWidget::item:hover:!selected {{
    background-color: {C_SURFACE2};
}}

/* ── QCheckBox ────────────────────────────────────────────────────────────── */
QCheckBox {{
    spacing: 8px;
    color: {C_TEXT};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    background: {C_SURFACE};
}}
QCheckBox::indicator:checked {{
    background: {C_ACCENT};
    border-color: {C_ACCENT};
}}

/* ── QGroupBox ────────────────────────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: 700;
    color: {C_TEXT_SUB};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: {C_ACCENT};
    font-size: 11px;
}}

/* ── QSlider ──────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 4px;
    background: {C_BORDER};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {C_ACCENT};
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {C_ACCENT};
    border-radius: 2px;
}}

/* ── QCalendarWidget ──────────────────────────────────────────────────────── */
QCalendarWidget QWidget {{
    background-color: {C_SURFACE};
    color: {C_TEXT};
    alternate-background-color: {C_SURFACE2};
}}
QCalendarWidget QToolButton {{
    background: {C_SURFACE2};
    color: {C_TEXT};
    border-radius: 6px;
    padding: 4px 8px;
}}
QCalendarWidget QToolButton:hover {{
    background: {C_ACCENT};
    color: {C_BG};
}}
QCalendarWidget QMenu {{
    background-color: {C_SURFACE2};
    color: {C_TEXT};
}}
QCalendarWidget QAbstractItemView:enabled {{
    color: {C_TEXT};
    selection-background-color: {C_ACCENT};
    selection-color: {C_BG};
}}
QCalendarWidget QAbstractItemView:disabled {{
    color: {C_TEXT_SUB};
}}
"""


# ─── Shared Widget Helpers ────────────────────────────────────────────────────

class Card(QFrame):
    """Glassmorphism-style card widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            #Card {{
                background-color: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
                padding: 4px;
            }}
        """)


class SectionLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"""
            color: {C_ACCENT};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 4px;
        """)


class SubLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")


def accent_button(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setProperty("accent", "true")
    btn.style().unpolish(btn)
    btn.style().polish(btn)
    return btn


def danger_button(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setProperty("danger", "true")
    btn.style().unpolish(btn)
    btn.style().polish(btn)
    return btn


def make_svg_icon(svg_content: str, size: int = 20) -> QIcon:
    """Render SVG string to QIcon."""
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    renderer = QSvgRenderer(QByteArray(svg_content.encode()))
    renderer.render(painter)
    painter.end()
    return QIcon(pix)


# ─── SVG icon definitions ─────────────────────────────────────────────────────
ICONS = {
    "dashboard": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
    </svg>""",
    "calendar": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
    </svg>""",
    "drills": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 3"/>
    </svg>""",
    "squad": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>""",
    "print": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
        <rect x="6" y="14" width="12" height="8"/>
    </svg>""",
    "football": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/>
    </svg>""",
}
