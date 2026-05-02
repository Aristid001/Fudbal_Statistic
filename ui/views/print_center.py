"""FTMS – Print Center View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QMessageBox, QSpinBox, QScrollArea,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

from ui.theme import (C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER,
                      C_BG, C_GREEN, C_RED, C_AMBER, accent_button)
from core.logic import (
    get_all_sessions, get_monthly_attendance_report
)
from core.pdf_engine import (
    generate_training_plan_pdf, generate_attendance_pdf,
    open_pdf, open_print_dialog
)

import calendar
from datetime import datetime


class PDFWorker(QThread):
    done    = pyqtSignal(str)
    error   = pyqtSignal(str)

    def __init__(self, fn, *args):
        super().__init__()
        self._fn   = fn
        self._args = args

    def run(self):
        try:
            path = self._fn(*self._args)
            self.done.emit(path)
        except Exception as e:
            self.error.emit(str(e))


class PrintCard(QFrame):
    def __init__(self, icon: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
            }}
            QFrame:hover {{ border: 1px solid {C_ACCENT}; }}
        """)
        l = QVBoxLayout(self)
        l.setContentsMargins(20, 18, 20, 18)
        l.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 32px;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 15px; font-weight: 700;")
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        desc_lbl.setWordWrap(True)

        l.addWidget(icon_lbl)
        l.addWidget(title_lbl)
        l.addWidget(desc_lbl)
        l.addStretch()


class PrintCenterView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._last_pdf = None
        self._build_ui()
        self._load_sessions()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # Header
        title = QLabel("Print Center")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #E6EDF3;")
        sub = QLabel("Generate and print professional PDF reports")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 13px; margin-top: 4px;")
        root.addWidget(title); root.addWidget(sub)

        # ── Training Plan Card ────────────────────────────────────────────────
        plan_lbl = QLabel("TRAINING PLAN")
        plan_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
        root.addWidget(plan_lbl)

        plan_card = QFrame()
        plan_card.setStyleSheet(f"background: {C_SURFACE}; border: 1px solid {C_BORDER}; border-radius: 12px;")
        pc_layout = QVBoxLayout(plan_card)
        pc_layout.setContentsMargins(20, 16, 20, 16)
        pc_layout.setSpacing(12)

        desc1 = QLabel("Generate a printable A4 training plan for any session — includes drill schedule, intensity overview, and coach notes.")
        desc1.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        desc1.setWordWrap(True)
        pc_layout.addWidget(desc1)

        sess_row = QHBoxLayout()
        sess_lbl = QLabel("Select Session:")
        sess_lbl.setStyleSheet(f"color: {C_TEXT}; min-width: 120px;")
        self.session_combo = QComboBox()
        self.session_combo.setMinimumWidth(280)
        self.plan_status = QLabel("")
        self.plan_status.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
        sess_row.addWidget(sess_lbl)
        sess_row.addWidget(self.session_combo)
        sess_row.addWidget(self.plan_status)
        sess_row.addStretch()
        pc_layout.addLayout(sess_row)

        btn_row1 = QHBoxLayout()
        gen_plan_btn   = accent_button("📄  Generate PDF")
        print_plan_btn = QPushButton("🖨  Print")
        open_plan_btn  = QPushButton("👁  Open PDF")
        gen_plan_btn.clicked.connect(self._generate_plan)
        print_plan_btn.clicked.connect(lambda: self._do_print(self._last_pdf))
        open_plan_btn.clicked.connect(lambda: self._do_open(self._last_pdf))
        btn_row1.addWidget(gen_plan_btn)
        btn_row1.addWidget(print_plan_btn)
        btn_row1.addWidget(open_plan_btn)
        btn_row1.addStretch()
        pc_layout.addLayout(btn_row1)
        root.addWidget(plan_card)

        # ── Attendance Report Card ────────────────────────────────────────────
        att_lbl = QLabel("MONTHLY ATTENDANCE REPORT")
        att_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
        root.addWidget(att_lbl)

        att_card = QFrame()
        att_card.setStyleSheet(f"background: {C_SURFACE}; border: 1px solid {C_BORDER}; border-radius: 12px;")
        ac_layout = QVBoxLayout(att_card)
        ac_layout.setContentsMargins(20, 16, 20, 16)
        ac_layout.setSpacing(12)

        desc2 = QLabel("Generate a monthly attendance table for all players — includes presence/absence breakdown and attendance percentage per player.")
        desc2.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        desc2.setWordWrap(True)
        ac_layout.addWidget(desc2)

        month_row = QHBoxLayout()
        month_lbl = QLabel("Month:")
        month_lbl.setStyleSheet(f"color: {C_TEXT}; min-width: 120px;")
        self.month_combo = QComboBox()
        now = datetime.now()
        for i in range(1, 13):
            self.month_combo.addItem(calendar.month_name[i], i)
        self.month_combo.setCurrentIndex(now.month - 1)
        year_lbl = QLabel("Year:")
        year_lbl.setStyleSheet(f"color: {C_TEXT}; margin-left: 16px;")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2035)
        self.year_spin.setValue(now.year)
        self.att_status = QLabel("")
        self.att_status.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
        month_row.addWidget(month_lbl)
        month_row.addWidget(self.month_combo)
        month_row.addWidget(year_lbl)
        month_row.addWidget(self.year_spin)
        month_row.addWidget(self.att_status)
        month_row.addStretch()
        ac_layout.addLayout(month_row)

        btn_row2 = QHBoxLayout()
        gen_att_btn   = accent_button("📊  Generate PDF")
        print_att_btn = QPushButton("🖨  Print")
        open_att_btn  = QPushButton("👁  Open PDF")
        self._last_att_pdf = None
        gen_att_btn.clicked.connect(self._generate_attendance)
        print_att_btn.clicked.connect(lambda: self._do_print(self._last_att_pdf))
        open_att_btn.clicked.connect(lambda: self._do_open(self._last_att_pdf))
        btn_row2.addWidget(gen_att_btn)
        btn_row2.addWidget(print_att_btn)
        btn_row2.addWidget(open_att_btn)
        btn_row2.addStretch()
        ac_layout.addLayout(btn_row2)
        root.addWidget(att_card)

        root.addStretch()

    def _load_sessions(self):
        sessions = get_all_sessions()
        self.session_combo.clear()
        self._sessions = sessions
        for s in sessions:
            label = f"{s.session_date}  ·  {s.focus_area or 'General Training'}  ·  {len(s.drills)} drills"
            self.session_combo.addItem(label, s.id)
        if not sessions:
            self.session_combo.addItem("No sessions available", -1)

    def _generate_plan(self):
        sid = self.session_combo.currentData()
        if not sid or sid == -1:
            QMessageBox.warning(self, "No Session", "Please select a session first.")
            return
        session = next((s for s in self._sessions if s.id == sid), None)
        if not session: return
        self.plan_status.setText("Generating…")
        self.plan_status.setStyleSheet(f"color: {C_AMBER}; font-size: 11px;")

        self._worker = PDFWorker(generate_training_plan_pdf, session)
        self._worker.done.connect(self._plan_done)
        self._worker.error.connect(self._pdf_error)
        self._worker.start()

    def _plan_done(self, path: str):
        self._last_pdf = path
        self.plan_status.setText(f"✓ Saved: {path.split('/')[-1]}")
        self.plan_status.setStyleSheet(f"color: {C_GREEN}; font-size: 11px;")

    def _generate_attendance(self):
        month = self.month_combo.currentData()
        year  = self.year_spin.value()
        self.att_status.setText("Generating…")
        self.att_status.setStyleSheet(f"color: {C_AMBER}; font-size: 11px;")

        report = get_monthly_attendance_report(year, month)
        self._worker2 = PDFWorker(generate_attendance_pdf, year, month, report)
        self._worker2.done.connect(self._att_done)
        self._worker2.error.connect(self._pdf_error)
        self._worker2.start()

    def _att_done(self, path: str):
        self._last_att_pdf = path
        self.att_status.setText(f"✓ Saved: {path.split('/')[-1]}")
        self.att_status.setStyleSheet(f"color: {C_GREEN}; font-size: 11px;")

    def _pdf_error(self, msg: str):
        QMessageBox.critical(self, "PDF Error", f"Failed to generate PDF:\n{msg}")

    def _do_print(self, path):
        if not path:
            QMessageBox.information(self, "Print", "Generate a PDF first.")
            return
        open_print_dialog(path)

    def _do_open(self, path):
        if not path:
            QMessageBox.information(self, "Open PDF", "Generate a PDF first.")
            return
        open_pdf(path)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_sessions()
