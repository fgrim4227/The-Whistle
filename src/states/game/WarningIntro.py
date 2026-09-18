"""
Content warning state (WarningIntro).
Shown before anything else plays.
"""

import pygame
from gale.input_handler import InputData
from gale.state import BaseState
from gale.timer import Timer

import settings

class WarningIntro(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.time: float = 0.0
        self.phase: str = "showing"
        self.skipped: bool = False
        self.circle_alpha: float = 0.0
        self.headphones_alpha: float = 0.0
        self.warning_alpha: float = 0.0

        self._load_assets()

    def _load_assets(self) -> None:
        self.warning_icon = settings.TEXTURES["warning_icon"]
        self.headphones_icon = settings.TEXTURES["warning_headphones"]
        self.circle_icon = settings.TEXTURES["warning_circle"]

    def enter(self, *args, **kwargs) -> None:
        self.time = 0.0
        self.phase = "showing"
        self.skipped = False
        self._text1()

    def _text1(self) -> None:
        self.phase = "headphones"
        self.headphones_alpha = 0.0

        Timer.tween(2.0, 
                    [(self, {"headphones_alpha": 255.0})],
                      on_finish=None)


        def _fade_out_headphones():
            Timer.tween(2.0, 
                        [(self, {"headphones_alpha": 0.0})],
                          on_finish=self._text2)
            
        Timer.after(5.0, _fade_out_headphones)


    def _text2(self)-> None:
        self.phase = "warning"
        self.warning_alpha = 0.0
        Timer.tween(2.0, 
            [(self, {"warning_alpha": 255.0})],
                on_finish=None)
        
        def _fade_out_warning():
                Timer.tween(2.0,
                    [(self, {"warning_alpha": 0.0})],
                        on_finish=self._text3)
                    
        Timer.after(5.0, _fade_out_warning)

    def _text3(self) -> None:
        self.phase = "circle"
        self.circle_alpha = 0.0

        Timer.tween(2.0, 
                    [(self, {"circle_alpha": 255.0})],
                      on_finish=None)


        def _fade_out_circle():
            Timer.tween(2.0, 
                        [(self, {"circle_alpha": 0.0})],
                          on_finish=self._go_to_start)
            
        Timer.after(5.0, _fade_out_circle)


    def exit(self) -> None:
        Timer.clear()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return
        if input_id not in ("enter", "action", "interact"):
            return

        # Cancels whatever fade is mid-flight so the skip is instant, and
        # clears the icon it interrupted so it doesn't linger frozen
        # behind the next one.
        Timer.clear()
        if self.phase == "headphones":
            self.headphones_alpha = 0.0
            self._text2()
        elif self.phase == "warning":
            self.warning_alpha = 0.0
            self._text3()
        elif self.phase == "circle":
            self._go_to_start()

    def _go_to_start(self) -> None:
        if self.skipped:
            return
        self.skipped = True
        Timer.clear()
        from src.states.game.StartState import StartState
        self.state_machine.pop()
        self.state_machine.push(StartState(self.state_machine))

    def update(self, dt: float) -> None:
        self.time += dt

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_DARK_BLUE)

        self.headphones_icon.set_alpha(round(self.headphones_alpha))
        headphones_rect = self.headphones_icon.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 40)
        )
        surface.blit(self.headphones_icon, headphones_rect)

        headphones_text = (
            "Use headphones for a better experience in this game."
        )
        headphones_font = settings.FONTS.get("small", settings.FONTS["medium"])
        headphones_surf = headphones_font.render(headphones_text, True, (235, 235, 235))
        headphones_surf.set_alpha(round(self.headphones_alpha))
        surface.blit(
            headphones_surf,
            headphones_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, headphones_rect.bottom + 20)),
        )

        self.warning_icon.set_alpha(round(self.warning_alpha))
        icon_rect = self.warning_icon.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 40)
        )
        surface.blit(self.warning_icon, icon_rect)

        warning_text = (
            "This videogame contains flashing lights, loud noises and jumpscares!"
        )
        warning_font = settings.FONTS.get("small", settings.FONTS["medium"])
        warning_surf = warning_font.render(warning_text, True, (235, 235, 235))
        warning_surf.set_alpha(round(self.warning_alpha))
        surface.blit(
            warning_surf,
            warning_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, icon_rect.bottom + 20)),
        )


        self.circle_icon.set_alpha(round(self.circle_alpha))
        circle_rect = self.circle_icon.get_rect(
                center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 40)
                )
        surface.blit(self.circle_icon, circle_rect)
        
        circle_text = (
                    "WhiteCircle presents..."
                )
        circle_font = settings.FONTS.get("small", settings.FONTS["medium"])
        circle_surf = circle_font.render(circle_text, True, (235, 235, 235))
        circle_surf.set_alpha(round(self.circle_alpha))
        surface.blit(
                    circle_surf,
                    circle_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, circle_rect.bottom + 20)),
                )
        
