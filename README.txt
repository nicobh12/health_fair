Health Fair v8 - mejoras solicitadas

Cambios principales:
- El paciente posee TODOS los síntomas definidos para su enfermedad (configurable en game_engine).
- Cada pregunta (sí/no) recalcula totalmente las probabilidades considerando evidencia afirmativa y negativa.
- Bayes está en espacio logarítmico y se mezcla con 'match_ratio' mediante un factor aditivo para evitar underflow.
- Penalizaciones por ausencia de síntomas críticos para enfermedades graves.
- Modo debug (--debug) que muestra enfermedad real y síntomas verdaderos para depuración.

Ejecución:
- Python 3.8+
- pip install colorama
- python main.py --debug
