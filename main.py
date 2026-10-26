import sys

from PyQt5.QtWidgets import QApplication

from app.main_window import EyeOfAgamotto


def main() -> int:
    app = QApplication(sys.argv)
    window = EyeOfAgamotto()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
