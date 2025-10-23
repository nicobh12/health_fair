Health Fair - Simulador de diagnóstico (versión actualizada)

Instrucciones rápidas:
1. Asegúrate de tener Python 3.8+ instalado.
2. Instala colorama si no está instalado:
   pip install colorama
3. Ejecuta desde la carpeta del proyecto:
   python main.py

Estructura:
- logic/
  - dataset.py
  - probability_engine.py
  - game_engine.py
- ui/
  - console_ui.py
- data/
  - diseases.json
- main.py

Notas:
- Todos los cálculos probabilísticos se realizan en logic/probability_engine.py.
- Después de preguntar por un síntoma, se recalculan (para todas) las probabilidades usando Bayes.
