"""FTMS – Drill Bank View"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QSpinBox, QTextEdit,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ui.theme import (C_ACCENT, C_TEXT, C_TEXT_SUB, C_SURFACE, C_BORDER,
                      C_BG, C_GREEN, C_RED, C_AMBER, accent_button, danger_button)
from core.logic import get_all_drills, save_drill, delete_drill, Drill


CATEGORIES = ["", "Technical", "Tactical", "Physical", "Set Piece"]
POSITIONS  = ["ALL", "GK", "DEF", "MID", "FWD", "GK,DEF", "MID,FWD", "DEF,MID", "FWD,MID"]


class DrillDialog(QDialog):
    def __init__(self, drill: Drill = None, parent=None):
        super().__init__(parent)
        self.drill = drill
        self.setWindowTitle("Edit Drill" if drill else "Add Drill")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build()
        if drill:
            self._populate(drill)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_lbl = QLabel("DRILL DETAILS")
        title_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
        layout.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(10)

        self.f_title    = QLineEdit(); self.f_title.setPlaceholderText("e.g. 4v4 Small-Sided Game")
        self.f_category = QComboBox(); self.f_category.addItems(["Technical","Tactical","Physical","Set Piece"])
        self.f_desc     = QTextEdit(); self.f_desc.setMaximumHeight(100)
        self.f_duration = QSpinBox(); self.f_duration.setRange(5, 120); self.f_duration.setSuffix(" min")
        self.f_intensity= QSpinBox(); self.f_intensity.setRange(1, 10)
        self.f_positions= QComboBox(); self.f_positions.addItems(POSITIONS)

        form.addRow("Title *",       self.f_title)
        form.addRow("Category *",    self.f_category)
        form.addRow("Description",   self.f_desc)
        form.addRow("Duration",      self.f_duration)
        form.addRow("Intensity (1–10)", self.f_intensity)
        form.addRow("Positions",     self.f_positions)
        layout.addLayout(form)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        self.save_btn = accent_button("Save Drill")
        self.save_btn.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addStretch(); btns.addWidget(self.save_btn)
        layout.addLayout(btns)

    def _populate(self, d: Drill):
        self.f_title.setText(d.title)
        idx = self.f_category.findText(d.category)
        if idx >= 0: self.f_category.setCurrentIndex(idx)
        self.f_desc.setPlainText(d.description)
        self.f_duration.setValue(d.duration_mins)
        self.f_intensity.setValue(d.intensity)
        idx2 = self.f_positions.findText(d.positions)
        if idx2 >= 0: self.f_positions.setCurrentIndex(idx2)

    def _save(self):
        title = self.f_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation", "Drill title is required.")
            return
        save_drill(
            title=title,
            category=self.f_category.currentText(),
            description=self.f_desc.toPlainText().strip(),
            duration_mins=self.f_duration.value(),
            intensity=self.f_intensity.value(),
            positions=self.f_positions.currentText(),
            drill_id=self.drill.id if self.drill else None
        )
        self.accept()


class DrillBankView(QWidget):
    drill_selected = pyqtSignal(int)  # drill_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Drill Bank")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #E6EDF3;")
        sub = QLabel("Your searchable library of football exercises")
        sub.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 13px; margin-top: 4px;")
        v = QVBoxLayout(); v.addWidget(title); v.addWidget(sub)
        add_btn = accent_button("＋  Add Drill")
        add_btn.clicked.connect(self._add_drill)
        hdr.addLayout(v); hdr.addStretch(); hdr.addWidget(add_btn)
        root.addLayout(hdr)

        # Filters
        filt_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search drills…")
        self.search_box.textChanged.connect(self.refresh)
        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["All Categories"] + ["Technical","Tactical","Physical","Set Piece"])
        self.cat_filter.currentTextChanged.connect(self.refresh)
        self.count_lbl = QLabel("0 drills")
        self.count_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        filt_row.addWidget(self.search_box, 3)
        filt_row.addWidget(self.cat_filter, 1)
        filt_row.addStretch()
        filt_row.addWidget(self.count_lbl)
        root.addLayout(filt_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Title","Category","Duration","Intensity","Positions","Load"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 110)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 70)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._edit_selected)
        root.addWidget(self.table, 1)

        # Bottom action bar
        actions = QHBoxLayout()
        self.edit_btn   = QPushButton("✏  Edit")
        self.delete_btn = danger_button("🗑  Delete")
        self.edit_btn.clicked.connect(self._edit_selected)
        self.delete_btn.clicked.connect(self._delete_selected)
        actions.addStretch()
        actions.addWidget(self.edit_btn)
        actions.addWidget(self.delete_btn)
        root.addLayout(actions)

        # Detail panel (shown on selection)
        self.detail = QFrame()
        self.detail.setStyleSheet(f"""
            QFrame {{ background: {C_SURFACE}; border: 1px solid {C_BORDER}; border-radius: 10px; }}
        """)
        self.detail.setMaximumHeight(120)
        dl = QVBoxLayout(self.detail)
        dl.setContentsMargins(14, 10, 14, 10)
        self.detail_lbl = QLabel("Select a drill to see its description")
        self.detail_lbl.setStyleSheet(f"color: {C_TEXT_SUB}; font-size: 12px;")
        self.detail_lbl.setWordWrap(True)
        dl.addWidget(self.detail_lbl)
        root.addWidget(self.detail)

        self.table.selectionModel().selectionChanged.connect(self._show_detail)

    def refresh(self):
        search = self.search_box.text().strip() if hasattr(self, 'search_box') else ""
        cat_text = self.cat_filter.currentText() if hasattr(self, 'cat_filter') else ""
        cat = "" if cat_text in ("", "All Categories") else cat_text
        drills = get_all_drills(category=cat, search=search)

        self._drills = drills
        self.table.setRowCount(len(drills))
        self.count_lbl.setText(f"{len(drills)} drill{'s' if len(drills) != 1 else ''}")

        for row, d in enumerate(drills):
            self.table.setRowHeight(row, 44)

            title_item = QTableWidgetItem(d.title)
            title_item.setForeground(QColor(C_TEXT))
            self.table.setItem(row, 0, title_item)

            cat_item = QTableWidgetItem(d.category)
            cat_item.setForeground(QColor(C_ACCENT))
            cat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, cat_item)

            dur_item = QTableWidgetItem(f"{d.duration_mins} min")
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            dur_item.setForeground(QColor(C_TEXT_SUB))
            self.table.setItem(row, 2, dur_item)

            int_item = QTableWidgetItem(f"{d.intensity}/10  {d.intensity_label}")
            int_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            int_item.setForeground(QColor(d.intensity_color))
            self.table.setItem(row, 3, int_item)

            pos_item = QTableWidgetItem(d.positions)
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pos_item.setForeground(QColor(C_TEXT_SUB))
            self.table.setItem(row, 4, pos_item)

            load_item = QTableWidgetItem(str(d.load))
            load_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            load_color = C_RED if d.intensity >= 9 else (C_AMBER if d.intensity >= 7 else C_GREEN)
            load_item.setForeground(QColor(load_color))
            self.table.setItem(row, 5, load_item)

    def _show_detail(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        row = self.table.currentRow()
        if 0 <= row < len(self._drills):
            d = self._drills[row]
            self.detail_lbl.setText(d.description or "No description.")
            self.detail_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 12px;")

    def _add_drill(self):
        dlg = DrillDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _edit_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._drills):
            return
        dlg = DrillDialog(drill=self._drills[row], parent=self)
        if dlg.exec():
            self.refresh()

    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._drills):
            return
        d = self._drills[row]
        reply = QMessageBox.question(
            self, "Delete Drill",
            f"Delete '{d.title}'?\nThis will remove it from any sessions.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_drill(d.id)
            self.refresh()
