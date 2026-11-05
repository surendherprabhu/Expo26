"""
PROJECT RIA — Research Intelligence Aariz
SDG 9 — Industry, Innovation & Infrastructure

Run this script to launch the application:
    python3 main.py
"""

import sys
import os

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app_window import AppWindow

def main():
    app = AppWindow()
    app.run()

if __name__ == "__main__":
    main()
