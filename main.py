import pygame, sys
from button import Button
from typing import List
from logic.dataset import Dataset
from logic.game_engine import GameEngine
import os, json


class DropdownButton:
    def __init__(self, pos, text, options, font, base_color, hovering_color, width=500, height=40):
        self.x, self.y = pos
        self.font = font
        self.text = text
        self.options = options
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.width = width
        self.height = height
        self.open = False
        self.selected = None

        # Rect principal
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)

    def draw(self, screen, mouse_pos):
        # Dibujar botón principal
        color = self.hovering_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(screen, (80, 80, 80), self.rect, border_radius=6)
        text_surface = self.font.render(self.text, True, color)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

        # Si está abierto, mostrar opciones
        if self.open:
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(
                    self.rect.x, self.rect.bottom + i * self.height, self.width, self.height
                )
                hover = opt_rect.collidepoint(mouse_pos)
                pygame.draw.rect(screen, (60, 60, 60) if not hover else (100, 100, 100), opt_rect, border_radius=6)
                opt_text = self.font.render(option, True, self.hovering_color if hover else self.base_color)
                screen.blit(opt_text, opt_text.get_rect(center=opt_rect.center))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clic en el botón principal
            if self.rect.collidepoint(mouse_pos):
                self.open = not self.open
                return None

            # Clic en alguna opción
            if self.open:
                for i, option in enumerate(self.options):
                    opt_rect = pygame.Rect(
                        self.rect.x, self.rect.bottom + i * self.height, self.width, self.height
                    )
                    if opt_rect.collidepoint(mouse_pos):
                        self.selected = option
                        self.open = False
                        return option  # Devuelve la opción elegida
                # Clic fuera: cerrar menú
                self.open = False
        return None


# ============================
# Inicialización
# ============================

dataset = Dataset(os.path.join(os.path.dirname(__file__), 'data', 'diseases.json'))
engine = GameEngine(dataset)

pygame.init()
SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load("assets/Background.jpeg")

def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def play():
    engine.reset_case()
    patient = engine.patient
    rounds = 0
    
    ASK_SYMPTOMS = DropdownButton(
        pos=(900, 150),
        text="Preguntar por síntoma",
        options=engine.suggest_symptoms(3),
        font=get_font(20),
        base_color="White",
        hovering_color="Green"
    )
    
    Diagnosticar = DropdownButton(
        pos=(900, 200),
        text="Hacer diagnóstico",
        options=[f"({d.id}) {d.name}" for d in dataset.diseases if engine.belief.get(d.id, 0) > 0],
        font=get_font(20),
        base_color="White",
        hovering_color="Green"
    )
    
    
    DescartarEnfermedad = DropdownButton(
        pos=(900, 250),
        text="Descartar enfermedad",
        options= [f"({d.id}) {d.name}" for d in dataset.diseases if engine.belief.get(d.id, 0) > 0],
        font=get_font(20),
        base_color="White",
        hovering_color="Green"
    )
    preguntas = {
        }
    flag=0;
    enfermedad_diagnosticada=" "
    colorDiagnostico="red"
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")
        
        PLAY_TEXT = get_font(20).render("Has diagnosticado: ", True, "#007FF3")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(850, 450))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)
        PLAY_TEXT = get_font(15).render(enfermedad_diagnosticada.ljust(50), True, colorDiagnostico)
        PLAY_RECT = PLAY_TEXT.get_rect(center=(1050, 480))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)
        
        family = Button(
            image=None, 
            pos=(760, 300), 
            text_input="Ver Perfil", 
            font=get_font(20), 
            base_color="White", 
            hovering_color="Green"
        )
        family.changeColor(PLAY_MOUSE_POS)
        family.update(SCREEN)
        NewPatient = get_font(15).render("Nuevo paciente ha llegado. Reporta inicialmente: ", True, "#007FF3")
        NewPatient_RECT = NewPatient.get_rect(center=(500, 25))
        NewPatientReport = get_font(15).render(", ".join(patient.true_symptoms), True, "#7B792F")
        NewPatientReport_RECT = NewPatientReport.get_rect(center=(1000, 25))
        SCREEN.blit(NewPatient, NewPatient_RECT)
        SCREEN.blit(NewPatientReport, NewPatientReport_RECT)
        
        
        # Título
        PLAY_TEXT = get_font(20).render("Probabilidades actuales:", True, "#007FF3")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(290, 50))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)
        
        
        
        
        if flag==1:
            p = engine.patient.profile
            tra=330;
            for k, v in p.items():
                text=f" - {k.capitalize()}: {v}"
                PLAY_TEXT2 = get_font(15).render(f"{k.capitalize()}: ".ljust(30), True, "#9EB4FB")
                PLAY_RECT2 = PLAY_TEXT2.get_rect(center=(920, tra))
                SCREEN.blit(PLAY_TEXT2, PLAY_RECT2)
                PLAY_TEXT2 = get_font(15).render(v, True, "#6D663F")
                PLAY_RECT2 = PLAY_TEXT2.get_rect(center=(930, tra))
                SCREEN.blit(PLAY_TEXT2, PLAY_RECT2)
                tra+=20

        # Mostrar las 10 probabilidades más altas
        y = 100
        for k, v in sorted(engine.belief.items(), key=lambda x: -x[1])[:10]:
            d = dataset.get_by_id(k)
            texto = f"({d.id}) {d.name}: ".ljust(50)
            PLAY_TEXT1 = get_font(15).render(texto, True, "white")
            PLAY_RECT1 = PLAY_TEXT1.get_rect(center=(420, y))
            probabilidad = f"{v:.3f}".ljust(50)
            PLAY_TEXT2 = get_font(15).render(probabilidad, True, "#9AAFF2")
            PLAY_RECT2 = PLAY_TEXT2.get_rect(center=(820, y))
            SCREEN.blit(PLAY_TEXT1, PLAY_RECT1)
            SCREEN.blit(PLAY_TEXT2, PLAY_RECT2)
            y += 40

        ACTIONS_TEXT = get_font(20).render("Acciones disponibles:", True, "#F5F5F6")
        ACTIONS_RECT = ACTIONS_TEXT.get_rect(center=(900, 50))
        SCREEN.blit(ACTIONS_TEXT, ACTIONS_RECT)

        # Dibujar botón desplegable
        DescartarEnfermedad.draw(SCREEN, PLAY_MOUSE_POS)
        Diagnosticar.draw(SCREEN, PLAY_MOUSE_POS)
        ASK_SYMPTOMS.draw(SCREEN, PLAY_MOUSE_POS)
        
        
        

        # Botón "BACK"
        PLAY_BACK = Button(
            image=None, 
            pos=(840, 650), 
            text_input="Salir de este Caso", 
            font=get_font(20), 
            base_color="White", 
            hovering_color="Green"
        )
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)
        
        

        y = 450
        for pregunta, respuesta in preguntas.items():
            ASK_TEXT = get_font(15).render(pregunta, True, "#7E7EBC")
            ASK_TEXT_RECT = ASK_TEXT.get_rect(topleft=(40, y))
            ASW_TEXT = get_font(15).render(respuesta, True, "#0C692D" if respuesta=="sí" else "#873A3A")
            ASW_TEXT_RECT = ASW_TEXT.get_rect(topleft=(480, y))
            SCREEN.blit(ASK_TEXT, ASK_TEXT_RECT)
            SCREEN.blit(ASW_TEXT, ASW_TEXT_RECT)
            y += 20


        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Manejar dropdown
            result = ASK_SYMPTOMS.handle_event(event, PLAY_MOUSE_POS)
            if result:
                res = engine.ask_symptom(result)
                ans_text = res['answer']
                respuesta="no"
                ask=f"Presentas {result}?"
                if res['reported_bool']:
                    respuesta="sí"
                preguntas[ask] = f"{respuesta}"
                ASK_SYMPTOMS.options = engine.suggest_symptoms(3)
                rounds += 1
                
            result = Diagnosticar.handle_event(event, PLAY_MOUSE_POS)
            if result:
                import re
                match = re.search(r"\((.*?)\)", result)
                if match:
                    correct = engine.make_diagnosis(match.group(1))
                    if correct:
                        print("Diagnóstico correcto")
                        enfermedad_diagnosticada=result+" (CORRECTO)"
                        colorDiagnostico="green"
                    else:
                        print("Diagnóstico incorrecto")
                        enfermedad_diagnosticada=result+" (INCORRECTO)"
                        colorDiagnostico="red"

            result = DescartarEnfermedad.handle_event(event, PLAY_MOUSE_POS)
            if result:
                import re
                match = re.search(r"\((.*?)\)", result)
                to_remove = match.group(1)
                if to_remove in engine.belief:
                    engine.discard_disease(to_remove)
                    print(f"Enfermedad {to_remove} descartada")
                    DescartarEnfermedad.options = [f"({d.id}) {d.name}" for d in dataset.diseases if engine.belief.get(d.id, 0) > 0]
                    #Diagnosticar.options = [f"({d.id}) {d.name}" for d in dataset.diseases if engine.belief.get(d.id, 0) > 0]
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                if family.checkForInput(PLAY_MOUSE_POS):
                    flag=1 if flag==0 else 0

        pygame.display.update()


def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("HEALTH \nFAIR", True, "#0051e9")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(
            image=pygame.transform.scale(pygame.image.load("assets/Blue Rect.png"), (320, 100)),
            pos=(640, 250), 
            text_input="PLAY", font=get_font(75), base_color="#FFFFFF", hovering_color="Blue"
        )
        QUIT_BUTTON = Button(
            image=pygame.image.load("assets/Quit Rect.png"),
            pos=(640, 550), 
            text_input="QUIT", font=get_font(75), base_color="#2b2951", hovering_color="White"
        )
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


main_menu()
