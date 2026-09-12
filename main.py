"""
Main entry point for 'El Silbón: Pesadilla en la Cabaña'.
"""

import sys
import os

# Ensure the root project directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.TheWhistle import TheWhistle

if __name__ == "__main__":
    game = TheWhistle()
    game.exec()
