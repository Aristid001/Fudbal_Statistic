"""
FTMS – Football Training Management System
Entry point: initialises DB, applies HiDPI settings, launches main window.
"""

import sys
import os
from pathlib import Path


def _configure_paths():
    """Add project root to sys.path so imports work from both script & frozen exe."""
    if getattr(sys, 'frozen', False):
        root = Path(sys.executable).parent
    else:
        root = Path(__file__).parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def main():
    _configure_paths()

    # ── Qt HiDPI ─────────────────────────────────────────────────────────────
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore    import Qt
    from PyQt6.QtGui     import QFont

    app = QApplication(sys.argv)
    app.setApplicationName("FTMS")
    app.setApplicationDisplayName("Football Training Management System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FTMS")

    # Default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # ── Database ──────────────────────────────────────────────────────────────
    from core.database import init_database
    init_database()

    # ── Main window ───────────────────────────────────────────────────────────
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()