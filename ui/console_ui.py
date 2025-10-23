"""console_ui.py - UI for Health Fair v10 (classical Bayes)"""
import os, json
from colorama import init, Fore, Style
from logic.dataset import Dataset
from logic.utils import clear_console

init(autoreset=True)

class ConsoleUI:
    def __init__(self, data_path, symptom_map, debug=False):
        from colorama import Fore, Style
        from os import system, name
        self.Fore, self.Style = Fore, Style
        self.system, self.name = system, name
        self.engine = None
        self.points = 100
        self.debug = debug
        self._clear()

    def _clear(self):
        self.system('cls' if self.name == 'nt' else 'clear')

    def _print_symptoms(self, confirmed, denied):
        print(f"Síntomas confirmados:")
        for s in confirmed:
            print(f"  {self.Fore.GREEN}✅ {s}{self.Style.RESET_ALL}")
        for s in denied:
            print(f"  {self.Fore.RED}❌ {s}{self.Style.RESET_ALL}")
        print()

    def __init__(self, data_path: str, symptom_map_path: str, debug: bool = False):
        self.dataset = Dataset(data_path, symptom_map_path)
        self.display_map = self.dataset.display_to_key()
        self.key_to_display = {v:k for k,v in self.display_map.items()}
        self.engine = __import__('logic.game_engine', fromlist=['']).GameEngine(self.dataset)
        self.debug = debug

    def _header(self):
        clear_console()
        print(Fore.CYAN + Style.BRIGHT + '=== HEALTH FAIR — SIMULADOR DE DIAGNÓSTICO (v10) ===' + Style.RESET_ALL)

    def run(self):
        while True:
            self.engine.reset_case()
            self._header()
            patient = self.engine.patient
            initial = patient.true_symptoms[0] if patient.true_symptoms else None
            if initial:
                print(Fore.YELLOW + f"Síntoma inicial reportado: {self.key_to_display.get(initial, initial)}" + Style.RESET_ALL)
            if self.debug:
                print(Fore.MAGENTA + f"[DEBUG] Enfermedad real: {patient.true_disease.name}" + Style.RESET_ALL)
                print(Fore.MAGENTA + f"[DEBUG] Síntomas verdaderos: {', '.join(patient.true_symptoms)}" + Style.RESET_ALL)
            while True:
                print('\nProbabilidades actuales:')
                for k,v in sorted(self.engine.belief.items(), key=lambda x: -x[1]):
                    d = self.dataset.get_by_id(k)
                    color = Fore.GREEN if v>=0.5 else (Fore.YELLOW if v>=0.2 else Fore.RED)
                    print(f" {color}({d.id}) {d.name}: {v:.3f}{Style.RESET_ALL}")
                print('\nAcciones:')
                print('1) Preguntar por síntoma')
                print('2) Hacer diagnóstico')
                print('3) Mostrar perfil del paciente (historia familiar)')
                print('4) Descartar enfermedad')
                print('0) Salir')
                opt = input('> ').strip()
                if opt == '0':
                    clear_console()
                    print('Gracias por jugar!')
                    return
                if opt == '1':
                    choices = self.engine.suggest_symptoms(3)
                    if not choices:
                        input('No hay síntomas disponibles. Presiona Enter...')
                        continue
                    print('\nSíntomas para preguntar:')
                    for i, key in enumerate(choices,1):
                        print(f"{i}) {self.key_to_display.get(key, key)}")
                    sel = input('> ').strip()
                    if not sel.isdigit() or int(sel) not in range(1, len(choices)+1):
                        continue
                    chosen = choices[int(sel)-1]
                    res = self.engine.ask_symptom(chosen)
                    if res['reported_bool']:
                        print(Fore.GREEN + f"Paciente responde: {res['answer']}" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"Paciente responde: {res['answer']}" + Style.RESET_ALL)
                    if self.debug:
                        print('\n[DEBUG] confirmed:', self.engine.patient.confirmed)
                        print('[DEBUG] negated:', self.engine.patient.negated)
                        print('[DEBUG] belief:', res['belief'])
                    input('\nPresiona Enter para continuar...')
                    self._header()
                elif opt == '2':
                    print('\nEnfermedades no descartadas:')
                    for k in self.engine.belief.keys():
                        print(f" ({k}) {self.dataset.get_by_id(k).name}")
                    code = input('\nCódigo: ').strip().upper()
                    ok = self.engine.make_diagnosis(code)
                    if ok:
                        print(Fore.GREEN + '\n✅ Diagnóstico correcto!' + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"\n❌ Incorrecto. La enfermedad real era: {self.engine.patient.true_disease.name}" + Style.RESET_ALL)
                    input('\nPresiona Enter...')
                    break
                elif opt == '3':
                    prof = self.engine.open_family_history()
                    print('\nHistoria familiar:')
                    for k,v in prof.items():
                        print(f" - {k}: {v}")
                    input('\nPresiona Enter...')
                elif opt == '4':
                    print('\nEnfermedades actuales:')
                    for k in self.engine.belief.keys():
                        print(f" ({k}) {self.dataset.get_by_id(k).name}")
                    d = input('\nCódigo a descartar: ').strip().upper()
                    self.engine.discard_disease(d)
                    print(Fore.YELLOW + 'Enfermedad descartada.' + Style.RESET_ALL)
                    input('\nPresiona Enter...')
                else:
                    input('Opción inválida. Presiona Enter...')
                self._header()
