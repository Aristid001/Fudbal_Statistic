"""FTMS – Main Window with HUD Sidebar"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray

from ui.theme import (GLOBAL_QSS, C_ACCENT, C_BG, C_SURFACE, C_BORDER,
                      C_TEXT, C_TEXT_SUB, C_SURFACE2, ICONS)
from ui.views.dashboard   import DashboardView
from ui.views.calendar    import CalendarView
from ui.views.drills      import DrillBankView
from ui.views.squad       import SquadHubView
from ui.views.print_center import PrintCenterView


def _svg_icon(svg: str, size: int = 20, color: str = "#8B949E") -> QIcon:
    colored = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    renderer = QSvgRenderer(QByteArray(colored.encode()))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)


class SidebarButton(QPushButton):
    def __init__(self, label: str, icon_svg: str, index: int, parent=None):
        super().__init__(parent)
        self._index   = index
        self._svg     = icon_svg
        self._label   = label
        self._active  = False

        self.setCheckable(False)
        self.setFixedHeight(52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setText(f"   {label}")
        self.setIcon(_svg_icon(icon_svg, 18, C_TEXT_SUB))
        self.setIconSize(QSize(18, 18))
        self._set_style(False)

    def set_active(self, active: bool):
        self._active = active
        icon_color = C_ACCENT if active else C_TEXT_SUB
        self.setIcon(_svg_icon(self._svg, 18, icon_color))
        self._set_style(active)

    def _set_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(0,255,204,0.08);
                    color: {C_ACCENT};
                    border: none;
                    border-left: 3px solid {C_ACCENT};
                    border-radius: 0;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 13px;
                    font-weight: 700;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {C_TEXT_SUB};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 13px;
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: rgba(255,255,255,0.04);
                    color: {C_TEXT};
                    border-left: 3px solid {C_BORDER};
                }}
            """)


class Sidebar(QFrame):
    def __init__(self, on_navigate, parent=None):
        super().__init__(parent)
        self._on_navigate = on_navigate
        self.setFixedWidth(200)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SURFACE};
                border-right: 1px solid {C_BORDER};
            }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo / Brand
        logo_frame = QFrame()
        logo_frame.setFixedHeight(64)
        logo_frame.setStyleSheet(f"border-bottom: 1px solid {C_BORDER}; background: transparent;")
        lf = QHBoxLayout(logo_frame)
        lf.setContentsMargins(18, 0, 18, 0)

        # Football emoji as logo
        ball = QLabel("⚽")
        ball.setStyleSheet("font-size: 22px;")
        brand = QLabel("FTMS")
        brand.setStyleSheet(f"color: {C_ACCENT}; font-size: 16px; font-weight: 800; letter-spacing: 2px;")
        lf.addWidget(ball)
        lf.addWidget(brand)
        lf.addStretch()
        layout.addWidget(logo_frame)

        layout.addSpacing(12)

        # Nav section label
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"""
            color: {C_TEXT_SUB};
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 2px;
            padding-left: 20px;
            padding-bottom: 6px;
        """)
        layout.addWidget(nav_label)

        # Nav buttons
        nav_items = [
            ("Dashboard", ICONS["dashboard"]),
            ("Calendar",  ICONS["calendar"]),
            ("Drill Bank",ICONS["drills"]),
            ("Squad Hub",  ICONS["squad"]),
            ("Print Center",ICONS["print"]),
        ]
        self._buttons: list[SidebarButton] = []
        for i, (label, icon) in enumerate(nav_items):
            btn = SidebarButton(label, icon, i)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Bottom info
        bottom = QFrame()
        bottom.setStyleSheet(f"border-top: 1px solid {C_BORDER}; background: transparent;")
        bf = QVBoxLayout(bottom)
        bf.setContentsMargins(18, 10, 18, 10)
        bf.setSpacing(2)
        ver = QLabel("v1.0.0")
        ver.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 10px;")
        tagline = QLabel("Football Training Manager")
        tagline.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 9px;")
        bf.addWidget(ver); bf.addWidget(tagline)
        layout.addWidget(bottom)

        self._navigate(0)

    def _navigate(self, index: int):
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == index)
        self._on_navigate(index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTMS — Football Training Management System")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(GLOBAL_QSS)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Stack of views
        self.stack = QStackedWidget()

        self.dashboard = DashboardView()
        self.calendar  = CalendarView()
        self.drills    = DrillBankView()
        self.squad     = SquadHubView()
        self.print_ctr = PrintCenterView()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.calendar)
        self.stack.addWidget(self.drills)
        self.stack.addWidget(self.squad)
        self.stack.addWidget(self.print_ctr)

        # Sidebar
        self.sidebar = Sidebar(on_navigate=self._navigate)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        # Refresh data when switching views
        views = [self.dashboard, self.calendar, self.drills, self.squad, self.print_ctr]
        if hasattr(views[index], 'refresh'):
            views[index].refresh()
