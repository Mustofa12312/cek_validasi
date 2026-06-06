"""
main.py — Entry point Validasi Data Kependudukan.
"""

import sys
import os

# Pastikan direktori root ada di path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
