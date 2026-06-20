"""Application entry point."""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    project_root = Path(sys._MEIPASS)
else:
    project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.gui.resources import asset_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Lupa")
    app.setOrganizationName("Pesquisa Acadêmica")
    app.setWindowIcon(QIcon(str(asset_path("lupa-icon.png"))))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
