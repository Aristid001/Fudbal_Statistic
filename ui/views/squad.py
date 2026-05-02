"""FTMS – Squad Hub View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QTextEdit, QSpinBox,
    QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.theme import (C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER,
                      C_BG, C_GREEN, C_RED, C_AMBER, accent_button, danger_button)
from core.logic import get_all_players, save_player, delete_player, Player


POSITIONS = ["GK", "DEF", "MID", "FWD"]
STATUSES  = ["Fit", "Injured", "Suspended"]


class PlayerDialog(QDialog):
    def __init__(self, player: Player = None, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle("Edit Player" if player else "Add Player")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build()
        if player:
            self._populate(player)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("PLAYER PROFILE")
        title.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.f_name    = QLineEdit(); self.f_name.setPlaceholderText("Full Name")
        self.f_jersey  = QSpinBox(); self.f_jersey.setRange(1, 99)
        self.f_pos     = QComboBox(); self.f_pos.addItems(POSITIONS)
        self.f_status  = QComboBox(); self.f_status.addItems(STATUSES)
        self.f_dob     = QLineEdit(); self.f_dob.setPlaceholderText("YYYY-MM-DD")
        self.f_notes   = QTextEdit(); self.f_notes.setMaximumHeight(80)
        self.f_notes.setPlaceholderText("Any notes about this player…")

        form.addRow("Name *",      self.f_name)
        form.addRow("Jersey #",    self.f_jersey)
        form.addRow("Position *",  self.f_pos)
        form.addRow("Status",      self.f_status)
        form.addRow("Date of Birth", self.f_dob)
        form.addRow("Notes",       self.f_notes)
        layout.addLayout(form)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        self.save_btn = accent_button("Save Player")
        self.save_btn.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addStretch(); btns.addWidget(self.save_btn)
        layout.addLayout(btns)

    def _populate(self, p: Player):
        self.f_name.setText(p.name)
        self.f_jersey.setValue(p.jersey_number or 1)
        idx = self.f_pos.findText(p.position)
        if idx >= 0: self.f_pos.setCurrentIndex(idx)
        idx2 = self.f_status.findText(p.status)
        if idx2 >= 0: self.f_status.setCurrentIndex(idx2)
        self.f_dob.setText(p.date_of_birth or "")
        self.f_notes.setPlainText(p.notes or "")

    def _save(self):
        name = self.f_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Player name is required.")
            return
        save_player(
            name=name,
            position=self.f_pos.currentText(),
            jersey_number=self.f_jersey.value(),
            status=self.f_status.currentText(),
            date_of_birth=self.f_dob.text().strip(),
            notes=self.f_notes.toPlainText().strip(),
            player_id=self.player.id if self.player else None
        )
        self.accept()


class PositionBadge(QLabel):
    COLORS = {"GK": "#FFB300", "DEF": "#00AAFF", "MID": "#00FFCC", "FWD": "#FF4444"}
    def __init__(self, position: str, parent=None):
        super().__init__(position, parent)
        color = self.COLORS.get(position, C_TEXT_SUB)
        self.setStyleSheet(f"""
            background: rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.2);
            color: {color};
            border: 1px solid {color};
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class SquadHubView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._players: list[Player] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Squad Hub")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #E6EDF3;")
        sub = QLabel("Manage your players and track their status")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 13px; margin-top: 4px;")
        v = QVBoxLayout(); v.addWidget(title); v.addWidget(sub)
        add_btn = accent_button("＋  Add Player")
        add_btn.clicked.connect(self._add_player)
        hdr.addLayout(v); hdr.addStretch(); hdr.addWidget(add_btn)
        root.addLayout(hdr)

        # Squad summary bar
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet(f"""
            QFrame {{ background: {C_SURFACE}; border: 1px solid {C_BORDER}; border-radius: 10px; }}
        """)
        self.summary_frame.setFixedHeight(56)
        sf_layout = QHBoxLayout(self.summary_frame)
        sf_layout.setContentsMargins(16, 0, 16, 0)

        self.lbl_total    = self._squad_stat("Total", "0")
        self.lbl_fit      = self._squad_stat("Fit", "0", C_GREEN)
        self.lbl_injured  = self._squad_stat("Injured", "0", C_RED)
        self.lbl_suspended= self._squad_stat("Suspended", "0", C_AMBER)
        for w in [self.lbl_total, self.lbl_fit, self.lbl_injured, self.lbl_suspended]:
            sf_layout.addWidget(w)
            if w != self.lbl_suspended:
                sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine)
                sep.setStyleSheet(f"color: {C_BORDER};")
                sf_layout.addWidget(sep)
        sf_layout.addStretch()
        root.addWidget(self.summary_frame)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#","Name","Position","Status","DOB","Notes"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 140)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._edit_player)
        root.addWidget(self.table, 1)

        # Actions
        actions = QHBoxLayout()
        self.edit_btn   = QPushButton("✏  Edit Player")
        self.delete_btn = danger_button("🗑  Remove")
        self.edit_btn.clicked.connect(self._edit_player)
        self.delete_btn.clicked.connect(self._delete_player)
        actions.addStretch()
        actions.addWidget(self.edit_btn)
        actions.addWidget(self.delete_btn)
        root.addLayout(actions)

    def _squad_stat(self, label: str, value: str, color: str = None) -> QWidget:
        w = QWidget()
        l = QHBoxLayout(w); l.setContentsMargins(8,0,8,0); l.setSpacing(6)
        v_lbl = QLabel(value)
        v_lbl.setStyleSheet(f"color: {color or C_TEXT}; font-size: 16px; font-weight: 700;")
        t_lbl = QLabel(label)
        t_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 11px;")
        l.addWidget(v_lbl); l.addWidget(t_lbl)
        w._value_label = v_lbl
        return w

    def refresh(self):
        self._players = get_all_players()
        self.table.setRowCount(len(self._players))

        counts = {"Fit": 0, "Injured": 0, "Suspended": 0}
        for row, p in enumerate(self._players):
            counts[p.status] = counts.get(p.status, 0) + 1
            self.table.setRowHeight(row, 44)

            jersey = QTableWidgetItem(str(p.jersey_number or "–"))
            jersey.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            jersey.setForeground(QColor(C_TEXT_SUB))
            self.table.setItem(row, 0, jersey)

            name = QTableWidgetItem(p.name)
            name.setForeground(QColor(C_TEXT))
            self.table.setItem(row, 1, name)

            pos = QTableWidgetItem(p.position_full)
            pos_colors = {"GK":"#FFB300","DEF":"#00AAFF","MID":"#00FFCC","FWD":"#FF4444"}
            pos.setForeground(QColor(pos_colors.get(p.position, C_TEXT_SUB)))
            pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, pos)

            status = QTableWidgetItem(p.status)
            status.setForeground(QColor(p.status_color))
            status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, status)

            dob = QTableWidgetItem(p.date_of_birth or "–")
            dob.setForeground(QColor(C_TEXT_SUB))
            dob.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, dob)

            notes = QTableWidgetItem(p.notes or "")
            notes.setForeground(QColor(C_TEXT_SUB))
            self.table.setItem(row, 5, notes)

        # Update summary
        self.lbl_total._value_label.setText(str(len(self._players)))
        self.lbl_fit._value_label.setText(str(counts.get("Fit", 0)))
        self.lbl_injured._value_label.setText(str(counts.get("Injured", 0)))
        self.lbl_suspended._value_label.setText(str(counts.get("Suspended", 0)))

    def _add_player(self):
        dlg = PlayerDialog(parent=self)
        if dlg.exec(): self.refresh()

    def _edit_player(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._players): return
        dlg = PlayerDialog(player=self._players[row], parent=self)
        if dlg.exec(): self.refresh()

    def _delete_player(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._players): return
        p = self._players[row]
        reply = QMessageBox.question(
            self, "Remove Player",
            f"Remove '{p.name}' from the squad? All their attendance records will also be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_player(p.id)
            self.refresh()
