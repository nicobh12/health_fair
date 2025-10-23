"""main.py
Entry point to run the Health Fair console game.
"""
import os
from ui.console_ui import ConsoleUI

def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'diseases.json')
    ui = ConsoleUI(data_path)
    ui.main_loop()

if __name__ == '__main__':
    main()
