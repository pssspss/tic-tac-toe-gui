"""Standalone launcher for the Tic-Tac-Toe Tkinter GUI application outside IDE."""
import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.interface import main

if __name__ == "__main__":
    main()
