"""FTMS – Calendar & Session View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCalendarWidget, QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QSpinBox, QListWidget, QListWidgetItem, QMessageBox,
    QSplitter, QFrame, QScrollArea, QTimeEdit, QDateEdit,
    QCheckBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QColor, QTextCharFormat, QBrush

from ui.theme import (C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER,
                      C_BG, C_GREEN, C_RED, C_AMBER, accent_button, danger_button)
from core.logic import (
    get_all_sessions, get_session, save_session, delete_session,
    get_all_drills, get_all_players, save_attendance, get_attendance,
    TrainingSession, Drill, Player
)


class SessionDialog(QDialog):
    def __init__(self, date_str: str = "", session: TrainingSession = None, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Edit Session" if session else "Plan Training Session")
        self.setMinimumSize(720, 620)
        self.setModal(True)
        self._build()
        if session:
            self._populate(session)
        elif date_str:
            self.f_date.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        title = QLabel("SESSION PLANNER")
        title.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
        root.addWidget(title)

        # Top form row
        form_row = QHBoxLayout()
        form = QFormLayout(); form.setSpacing(8)
        self.f_date     = QDateEdit(QDate.currentDate()); self.f_date.setCalendarPopup(True)
        self.f_time     = QTimeEdit(QTime(9, 0))
        self.f_duration = QSpinBox(); self.f_duration.setRange(15, 240); self.f_duration.setValue(90); self.f_duration.setSuffix(" min")
        self.f_focus    = QLineEdit(); self.f_focus.setPlaceholderText("e.g. Pressing & Transitions")
        self.f_notes    = QTextEdit(); self.f_notes.setMaximumHeight(70)
        form.addRow("Date *",     self.f_date)
        form.addRow("Start Time", self.f_time)
        form.addRow("Duration",   self.f_duration)
        form.addRow("Focus Area", self.f_focus)
        form.addRow("Notes",      self.f_notes)
        form_row.addLayout(form, 1)
        root.addLayout(form_row)

        # Drill picker
        drill_lbl = QLabel("DRILLS  (double-click to add/remove)")
        drill_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-top: 4px;")
        root.addWidget(drill_lbl)

        picker = QHBoxLayout()

        # Left: available drills
        avail_frame = QFrame()
        avail_frame.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px;")
        af = QVBoxLayout(avail_frame); af.setContentsMargins(8,8,8,8); af.setSpacing(6)
        avail_title = QLabel("Available Drills")
        avail_title.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px; font-weight: 700;")
        self.avail_search = QLineEdit(); self.avail_search.setPlaceholderText("Filter…")
        self.avail_list   = QListWidget()
        self.avail_search.textChanged.connect(self._filter_drills)
        self.avail_list.itemDoubleClicked.connect(self._add_drill)
        af.addWidget(avail_title); af.addWidget(self.avail_search); af.addWidget(self.avail_list)

        mid_btns = QVBoxLayout()
        mid_btns.addStretch()
        btn_add = QPushButton("→"); btn_add.setFixedWidth(36); btn_add.clicked.connect(self._add_drill)
        btn_rem = QPushButton("←"); btn_rem.setFixedWidth(36); btn_rem.clicked.connect(self._remove_drill)
        mid_btns.addWidget(btn_add); mid_btns.addWidget(btn_rem)
        mid_btns.addStretch()

        # Right: session drills
        sess_frame = QFrame()
        sess_frame.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px;")
        sf = QVBoxLayout(sess_frame); sf.setContentsMargins(8,8,8,8); sf.setSpacing(6)
        sess_title = QLabel("Session Drills")
        sess_title.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px; font-weight: 700;")
        self.sess_list  = QListWidget()
        self.sess_list.itemDoubleClicked.connect(self._remove_drill)
        self.load_lbl = QLabel("Total Load: 0 pts")
        self.load_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
        self.warning_lbl = QLabel()
        self.warning_lbl.setStyleSheet(f"color: {C_RED}; font-size: 11px; font-weight: 700;")
        sf.addWidget(sess_title); sf.addWidget(self.sess_list)
        sf.addWidget(self.load_lbl); sf.addWidget(self.warning_lbl)

        picker.addWidget(avail_frame, 1)
        picker.addLayout(mid_btns)
        picker.addWidget(sess_frame, 1)
        root.addLayout(picker, 1)

        # Buttons
        btns = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        self.save_btn = accent_button("Save Session")
        self.save_btn.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addStretch(); btns.addWidget(self.save_btn)
        root.addLayout(btns)

        self._load_drills()
        self._drill_map: dict[int, Drill] = {}

    def _load_drills(self):
        self._all_drills = get_all_drills()
        self._filter_drills()

    def _filter_drills(self):
        search = self.avail_search.text().lower() if hasattr(self, 'avail_search') else ""
        self.avail_list.clear()
        for d in self._all_drills:
            if search and search not in d.title.lower():
                continue
            item = QListWidgetItem(f"{d.title}  [{d.intensity}/10 · {d.duration_mins}m]")
            item.setData(Qt.ItemDataRole.UserRole, d.id)
            item.setForeground(QColor(C_TEXT))
            self.avail_list.addItem(item)

    def _add_drill(self):
        item = self.avail_list.currentItem()
        if not item: return
        drill_id = item.data(Qt.ItemDataRole.UserRole)
        # Check not already added
        for i in range(self.sess_list.count()):
            if self.sess_list.item(i).data(Qt.ItemDataRole.UserRole) == drill_id:
                return
        drill = next((d for d in self._all_drills if d.id == drill_id), None)
        if not drill: return
        si = QListWidgetItem(f"{drill.title}  [{drill.intensity}/10 · {drill.duration_mins}m]")
        si.setData(Qt.ItemDataRole.UserRole, drill_id)
        si.setForeground(QColor(C_ACCENT))
        self.sess_list.addItem(si)
        self._update_load()

    def _remove_drill(self):
        row = self.sess_list.currentRow()
        if row >= 0:
            self.sess_list.takeItem(row)
        self._update_load()

    def _update_load(self):
        ids = [self.sess_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.sess_list.count())]
        drills = [d for d in self._all_drills if d.id in ids]
        total_load = sum(d.load for d in drills)
        avg_int = sum(d.intensity for d in drills) / len(drills) if drills else 0
        self.load_lbl.setText(f"Total Load: {total_load} pts  ·  Avg Intensity: {avg_int:.1f}/10")
        if avg_int > 8.5 or total_load > 200:
            self.warning_lbl.setText("⚠ HIGH LOAD — consider reducing drill intensity")
        else:
            self.warning_lbl.setText("")

    def _populate(self, s: TrainingSession):
        self.f_date.setDate(QDate.fromString(s.session_date, "yyyy-MM-dd"))
        self.f_time.setTime(QTime.fromString(s.start_time, "HH:mm"))
        self.f_duration.setValue(s.total_duration)
        self.f_focus.setText(s.focus_area or "")
        self.f_notes.setPlainText(s.notes or "")
        for d in s.drills:
            item = QListWidgetItem(f"{d.title}  [{d.intensity}/10 · {d.duration_mins}m]")
            item.setData(Qt.ItemDataRole.UserRole, d.id)
            item.setForeground(QColor(C_ACCENT))
            self.sess_list.addItem(item)
        self._update_load()

    def _save(self):
        date_str = self.f_date.date().toString("yyyy-MM-dd")
        time_str = self.f_time.time().toString("HH:mm")
        drill_ids = [self.sess_list.item(i).data(Qt.ItemDataRole.UserRole)
                     for i in range(self.sess_list.count())]
        save_session(
            session_date=date_str,
            start_time=time_str,
            total_duration=self.f_duration.value(),
            focus_area=self.f_focus.text().strip(),
            notes=self.f_notes.toPlainText().strip(),
            drill_ids=drill_ids,
            session_id=self.session.id if self.session else None
        )
        self.accept()


class AttendanceDialog(QDialog):
    def __init__(self, session: TrainingSession, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle(f"Attendance – {session.session_date}")
        self.setMinimumSize(400, 480)
        self.setModal(True)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        title = QLabel("ATTENDANCE REGISTER")
        title.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
        root.addWidget(title)

        sub = QLabel(f"Session: {self.session.session_date}  ·  {self.session.focus_area or 'Training'}")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        root.addWidget(sub)

        players = get_all_players()
        existing = get_attendance(self.session.id)
        self._checks: dict[int, QComboBox] = {}

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        cl = QVBoxLayout(container); cl.setSpacing(6)

        for p in players:
            row = QFrame()
            row.setStyleSheet(f"background: {C_SURFACE}; border-radius: 6px;")
            rl = QHBoxLayout(row); rl.setContentsMargins(10,6,10,6)
            name_lbl = QLabel(f"<b>{p.name}</b>  <span style='color:{C_TEXT_SUB}'>{p.position}</span>")
            name_lbl.setTextFormat(Qt.TextFormat.RichText)
            combo = QComboBox()
            combo.addItems(["Present","Absent","Excused"])
            combo.setFixedWidth(110)
            current = existing.get(p.id, "Present")
            idx = combo.findText(current)
            if idx >= 0: combo.setCurrentIndex(idx)
            self._checks[p.id] = combo
            rl.addWidget(name_lbl); rl.addStretch(); rl.addWidget(combo)
            cl.addWidget(row)

        cl.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save = accent_button("Save Attendance"); save.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addStretch(); btns.addWidget(save)
        root.addLayout(btns)

    def _save(self):
        records = {pid: combo.currentText() for pid, combo in self._checks.items()}
        save_attendance(self.session.id, records)
        self.accept()


class CalendarView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions: list[TrainingSession] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Training Calendar")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #E6EDF3;")
        sub = QLabel("Plan, review, and manage all training sessions")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 13px; margin-top: 4px;")
        v = QVBoxLayout(); v.addWidget(title); v.addWidget(sub)
        new_btn = accent_button("＋  New Session")
        new_btn.clicked.connect(lambda: self._new_session())
        hdr.addLayout(v); hdr.addStretch(); hdr.addWidget(new_btn)
        root.addLayout(hdr)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Calendar widget
        self.cal = QCalendarWidget()
        self.cal.setGridVisible(False)
        self.cal.setMinimumWidth(320)
        self.cal.clicked.connect(self._date_clicked)
        splitter.addWidget(self.cal)

        # Right panel
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        sess_lbl = QLabel("SESSIONS ON SELECTED DATE")
        sess_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        right_layout.addWidget(sess_lbl)

        self.session_list = QListWidget()
        self.session_list.itemDoubleClicked.connect(self._edit_session)
        right_layout.addWidget(self.session_list, 1)

        # Session actions
        action_row = QHBoxLayout()
        self.att_btn    = QPushButton("👥  Attendance")
        self.edit_btn   = QPushButton("✏  Edit")
        self.delete_btn = danger_button("🗑  Delete")
        self.att_btn.clicked.connect(self._open_attendance)
        self.edit_btn.clicked.connect(self._edit_session)
        self.delete_btn.clicked.connect(self._delete_session)
        for b in [self.att_btn, self.edit_btn, self.delete_btn]:
            action_row.addWidget(b)
        right_layout.addLayout(action_row)

        # Session detail
        self.detail_frame = QFrame()
        self.detail_frame.setStyleSheet(f"background: {C_SURFACE}; border: 1px solid {C_BORDER}; border-radius: 10px;")
        df = QVBoxLayout(self.detail_frame); df.setContentsMargins(12,10,12,10); df.setSpacing(4)
        self.detail_lbl = QLabel("Select a session to see details")
        self.detail_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        self.detail_lbl.setWordWrap(True)
        df.addWidget(self.detail_lbl)
        right_layout.addWidget(self.detail_frame)

        splitter.addWidget(right)
        splitter.setSizes([340, 400])
        root.addWidget(splitter, 1)
        self.session_list.itemClicked.connect(self._show_session_detail)

    def refresh(self):
        self._sessions = get_all_sessions()
        self._mark_calendar()
        self._date_clicked(self.cal.selectedDate())

    def _mark_calendar(self):
        """Highlight dates that have sessions."""
        fmt_session = QTextCharFormat()
        fmt_session.setBackground(QBrush(QColor(0, 255, 204, 50)))
        fmt_session.setForeground(QBrush(QColor(C_ACCENT)))

        # Clear all highlights first
        self.cal.setDateTextFormat(QDate(), QTextCharFormat())
        for s in self._sessions:
            d = QDate.fromString(s.session_date, "yyyy-MM-dd")
            if d.isValid():
                self.cal.setDateTextFormat(d, fmt_session)

    def _date_clicked(self, date: QDate):
        date_str = date.toString("yyyy-MM-dd")
        day_sessions = [s for s in self._sessions if s.session_date == date_str]
        self.session_list.clear()
        self._day_sessions = day_sessions

        for s in day_sessions:
            item = QListWidgetItem(
                f"⏱ {s.start_time}  ·  {s.focus_area or 'Training'}  ·  "
                f"{len(s.drills)} drills  ·  {s.total_duration} min"
            )
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            item.setForeground(QColor(C_TEXT))
            self.session_list.addItem(item)

        if not day_sessions:
            self.detail_lbl.setText(f"No sessions on {date_str}. Double-click a date to plan one.")
            self.detail_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")

    def _show_session_detail(self, item):
        sid = item.data(Qt.ItemDataRole.UserRole)
        s = next((x for x in self._day_sessions if x.id == sid), None)
        if not s: return
        drill_names = " → ".join(d.title for d in s.drills) or "No drills"
        warning = "  ⚠ HIGH LOAD" if s.load_warning else ""
        text = (
            f"<b style='color:{C_ACCENT}'>{s.focus_area or 'General Training'}</b>"
            f"{warning}<br>"
            f"<span style='color:{C_TEXT_SUB}'>{s.start_time} · {s.total_duration} min · "
            f"Load {s.total_load} pts</span><br>"
            f"<span style='color:{C_TEXT_SUB}'>Drills: {drill_names}</span>"
        )
        self.detail_lbl.setText(text)
        self.detail_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.detail_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 12px;")

    def _get_selected_session(self):
        item = self.session_list.currentItem()
        if not item: return None
        sid = item.data(Qt.ItemDataRole.UserRole)
        return next((s for s in self._day_sessions if s.id == sid), None)

    def _new_session(self, date_str: str = ""):
        if not date_str:
            date_str = self.cal.selectedDate().toString("yyyy-MM-dd")
        dlg = SessionDialog(date_str=date_str, parent=self)
        if dlg.exec(): self.refresh()

    def _edit_session(self):
        s = self._get_selected_session()
        if not s: return
        dlg = SessionDialog(session=s, parent=self)
        if dlg.exec(): self.refresh()

    def _delete_session(self):
        s = self._get_selected_session()
        if not s: return
        reply = QMessageBox.question(
            self, "Delete Session",
            f"Delete session on {s.session_date}? This will remove all attendance records too.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_session(s.id)
            self.refresh()

    def _open_attendance(self):
        s = self._get_selected_session()
        if not s:
            QMessageBox.information(self, "Attendance", "Please select a session first.")
            return
        dlg = AttendanceDialog(session=s, parent=self)
        dlg.exec()
