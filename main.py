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
    from PyQt6.QtGui     import QFont, QFontDatabase

    app = QApplication(sys.argv)
    app.setApplicationName("FTMS")
    app.setApplicationDisplayName("Football Training Management System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FTMS")

    # Default font - use system-safe fallbacks
    available_fonts = QFontDatabase.families()
    font_name = "Segoe UI"
    if font_name not in available_fonts:
        # Try other common fonts
        for fallback in ["Inter", "SF Pro Display", "Ubuntu", "DejaVu Sans", "Arial", "Sans Serif"]:
            if fallback in available_fonts:
                font_name = fallback
                break
        else:
            font_name = ""  # Use system default
    
    try:
        font = QFont(font_name, 10) if font_name else QFont()
        # Ensure positive point size to avoid QFont warnings
        if font.pointSize() <= 0:
            font.setPointSize(10)
        app.setFont(font)
    except Exception:
        # Fallback to default font if anything fails
        fallback_font = QFont()
        if fallback_font.pointSize() <= 0:
            fallback_font.setPointSize(10)
        app.setFont(fallback_font)

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