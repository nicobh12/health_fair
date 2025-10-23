"""main.py - Health Fair v10"""
import os, argparse
from ui.console_ui import ConsoleUI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    base = os.path.dirname(__file__)
    data = os.path.join(base, 'data', 'diseases.json')
    symptom_map = os.path.join(base, 'data', 'symptom_map.json')
    ui = ConsoleUI(data, symptom_map, debug=args.debug)
    ui.run()

if __name__ == '__main__':
    main()
