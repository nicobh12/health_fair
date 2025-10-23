"""console_ui.py
Interfaz por consola usando colorama para mejorar lectura.
"""
from typing import List
from logic.dataset import Dataset
from logic.game_engine import GameEngine
import os, json
try:
    from colorama import init, Fore, Style
except ImportError:
    # fallback no-color
    class _Fake:
        def __getattr__(self, name):
            return ''
    init = lambda **k: None
    Fore = Style = _Fake()
init(autoreset=True)

class ConsoleUI:
    def __init__(self, data_path: str):
        self.dataset = Dataset(data_path)
        self.engine = GameEngine(self.dataset)

    def _print_header(self, text: str):
        print(Fore.CYAN + Style.BRIGHT + text + Style.RESET_ALL)

    def main_loop(self):
        self._print_header("=== Health Fair — Simulador de diagnóstico médico ===\n")
        playing = True
        while playing:
            self.engine.reset_case()
            patient = self.engine.patient
            print(Fore.YELLOW + f"Nuevo paciente ha llegado. Reporta inicialmente: {', '.join(patient.true_symptoms)}" + Style.RESET_ALL)
            rounds = 0
            while True:
                print('\n' + Fore.MAGENTA + "Probabilidades actuales:" + Style.RESET_ALL)
                for k, v in sorted(self.engine.belief.items(), key=lambda x: -x[1])[:10]:
                    d = self.dataset.get_by_id(k)
                    print(f" {Fore.WHITE}({d.id}) {d.name}: {Fore.GREEN}{v:.3f}{Style.RESET_ALL}")

                print('\n' + Fore.BLUE + 'Acciones disponibles:' + Style.RESET_ALL)
                print('1) Preguntar por síntoma')
                print('2) Hacer diagnóstico')
                print('3) Mostrar perfil del paciente')
                print('4) Descartar enfermedad')
                print('0) Salir del juego')
                opt = input('> ').strip()

                if opt == '1':
                    choices = self.engine.suggest_symptoms(3)
                    if not choices:
                        print('No hay síntomas disponibles para preguntar.')
                        continue
                    print('\n' + Fore.YELLOW + 'Opciones de síntomas para preguntar:' + Style.RESET_ALL)
                    for i, s in enumerate(choices, 1):
                        print(f"{i}) {s}")
                    sel = input('> ').strip()
                    if not sel.isdigit() or not (1 <= int(sel) <= len(choices)):
                        print('Opción inválida.')
                        continue
                    s = choices[int(sel) - 1]
                    res = self.engine.ask_symptom(s)
                    ans_text = res['answer']
                    if res['reported_bool']:
                        print(Fore.GREEN + f"Paciente responde: {ans_text}" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"Paciente responde: {ans_text}" + Style.RESET_ALL)
                    rounds += 1

                elif opt == '2':
                    print('\nEnfermedades no descartadas:')
                    for d in self.dataset.diseases:
                        if self.engine.belief.get(d.id, 0) > 0:
                            print(f" ({d.id}) {d.name}")
                    choice = input('Escribe el código (ej. CC): ').strip().upper()
                    if choice not in self.engine.belief:
                        print('Código inválido.')
                        continue
                    correct = self.engine.make_diagnosis(choice)
                    if correct:
                        print(Fore.GREEN + '\n✅ Diagnóstico correcto!\n' + Style.RESET_ALL)
                    else:
                        true = self.engine.patient.true_disease
                        print(Fore.RED + f'\n❌ Incorrecto. La enfermedad real era: {true.name}\n' + Style.RESET_ALL)
                    break

                elif opt == '3':
                    p = self.engine.patient.profile
                    print('\n' + Fore.CYAN + 'Perfil del paciente:' + Style.RESET_ALL)
                    for k, v in p.items():
                        print(f" - {k.capitalize()}: {v}")

                elif opt == '4':
                    print('\nEnfermedades no descartadas:')
                    for d in self.dataset.diseases:
                        if self.engine.belief.get(d.id, 0) > 0:
                            print(f" ({d.id}) {d.name}")
                    to_remove = input('Código de enfermedad a descartar: ').strip().upper()
                    if to_remove in self.engine.belief:
                        self.engine.discard_disease(to_remove)
                        print(Fore.YELLOW + f"{to_remove} descartada del diagnóstico." + Style.RESET_ALL)
                    else:
                        print('Código no válido.')

                elif opt == '0':
                    playing = False
                    break
                else:
                    print('Opción no válida.')

            if not playing:
                break
            cont = input('\n¿Jugar otro caso? (s/n): ').strip().lower()
            if cont != 's':
                break
        print('\n' + Fore.CYAN + 'Gracias por jugar Health Fair!' + Style.RESET_ALL)
