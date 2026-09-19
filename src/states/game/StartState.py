"""
Main Menu state with language toggle, instructions modal, and nightmare launch.
"""

import math
import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t, toggle_language, get_language
from gale.state import BaseState
from src.systems.AudioManager import AudioManager
from src.systems.LightingSystem import LightingSystem

class StartState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.selected_index = 0
        self.show_instructions = False
        self.show_credits = False
        self.fog_timer = 0.0
        self.audio = AudioManager()
        self.lighting = LightingSystem()

    def enter(self, *args, **kwargs) -> None:
        self.selected_index = 0
        self.show_instructions = False
        self.audio.start_title_audio()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if self.show_instructions:
            if input_id in ("enter", "quit", "interact"):
                self.show_instructions = False
            return
        if self.show_credits:
            if input_id in ("enter", "quit", "interact"):
                self.show_credits = False
            return
        if input_id == "move_up":
            self.selected_index = (self.selected_index - 1) % 5
        elif input_id == "move_down":
            self.selected_index = (self.selected_index + 1) % 5
        elif input_id == "toggle_language":
            toggle_language()
        elif input_id == "enter":
            self._select_option()

    def exit(self) -> None:
        settings.stop_all_audio()

    def _select_option(self) -> None:
        if self.selected_index == 0:
            # Stop menu music before entering cinematic intro
            settings.stop_all_audio()
            # Launch game: play cinematic intro road sequence
            from src.states.game.IntroRoadState import IntroRoadState
            self.state_machine.push(IntroRoadState(self.state_machine))
        elif self.selected_index == 1:
            toggle_language()
        elif self.selected_index == 2:
            self.show_instructions = True
        elif self.selected_index == 3:
            self.show_credits = True
        elif self.selected_index == 4:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        self.fog_timer += dt
        if self.audio.update_title_audio(dt):
            self.lighting.trigger_thunder_flash()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0,0,0))
        bg = settings.TEXTURES.get("title_bg")
        if bg:
            bg = pygame.transform.scale(bg, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            surface.blit(bg, (0, 0))
        else:
            surface.fill(settings.COLOR_DARK_BLUE)

        self.lighting.render_title_screen(surface, 0.016)

        alpha_pulse = int(180 + 75 * math.sin(self.fog_timer * 3.0))
        title_color = (alpha_pulse, 20, 20)

        # Title and Subtitle
        title_surf = settings.FONTS["title"].render(t("menu_title"), True, title_color)
        sub_surf = settings.FONTS["medium"].render(t("menu_subtitle"), True, settings.COLOR_GRAY)
        
        surface.blit(title_surf, (settings.VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 40))
        surface.blit(sub_surf, (settings.VIRTUAL_WIDTH // 2 - sub_surf.get_width() // 2, 85))

        if self.show_instructions:
            self._render_instructions(surface)
            return
        if self.show_credits:
            self._render_credits(surface)
            return
        # Main Menu Options
        options = [
            t("menu_start"),
            f"{t('menu_language')} [{get_language().upper()}]",
            t("menu_instructions"),
            "Credits",
            t("menu_quit"),
        ]

        start_y = 135
        for i, text in enumerate(options):
            is_selected = (i == self.selected_index)
            color = settings.COLOR_GOLD if is_selected else settings.COLOR_WHITE
            prefix = "► " if is_selected else "  "
            
            font = settings.FONTS["medium"] if is_selected else settings.FONTS["small"]
            opt_surf = font.render(prefix + text, True, color)
            opt_rect = opt_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, start_y + i * 26))
            surface.blit(opt_surf, opt_rect)

        # Footer navigation hint
        hint_surf = settings.FONTS["small"].render(t("menu_select"), True, settings.COLOR_GRAY)
        surface.blit(hint_surf, (settings.VIRTUAL_WIDTH // 2 - hint_surf.get_width() // 2, settings.VIRTUAL_HEIGHT - 25))

    def _render_instructions(self, surface: pygame.Surface) -> None:
        # Modal instructions dialog
        modal_rect = pygame.Rect(40, 22, settings.VIRTUAL_WIDTH - 80, settings.VIRTUAL_HEIGHT - 44)
        pygame.draw.rect(surface, (20, 20, 30), modal_rect, border_radius=8)
        pygame.draw.rect(surface, settings.COLOR_DARK_RED, modal_rect, width=2, border_radius=8)

        title = settings.FONTS["medium"].render(t("menu_instructions"), True, settings.COLOR_GOLD)
        surface.blit(title, (modal_rect.centerx - title.get_width() // 2, modal_rect.top + 10))

        lines = [
            t("inst_move"),
            t("inst_flashlight"),
            t("inst_interact"),
            t("inst_throw"),
            t("inst_objectives"),
            t("inst_pause"),
            t("inst_fullscreen"),
            "",
            t("inst_warning"),
            t("inst_back"),
        ]

        for idx, line in enumerate(lines):
            color = settings.COLOR_GOLD if idx == 8 else settings.COLOR_WHITE
            line_surf = settings.FONTS["small"].render(line, True, color)
            surface.blit(line_surf, (modal_rect.left + 25, modal_rect.top + 36 + idx * 16))
    def _render_credits(self, surface: pygame.Surface) -> None:
        modal_rect = pygame.Rect(40, 22, settings.VIRTUAL_WIDTH - 80, settings.VIRTUAL_HEIGHT - 44)
        pygame.draw.rect(surface, (20, 20, 30), modal_rect, border_radius=8)
        pygame.draw.rect(surface, settings.COLOR_DARK_RED, modal_rect, width=2, border_radius=8)

        title = settings.FONTS["medium"].render("CREDITS & ASSETS", True, settings.COLOR_GOLD)
        surface.blit(title, (modal_rect.centerx - title.get_width() // 2, modal_rect.top + 10))
 
        lines = [
            "Demon Woods Parallax Background by Aethrall", 
            "https://aethrall.itch.io/demon-woods-parallax-background",
            "-FREE Modern House Tile Set by Manic Pixel Dream Girl:",
            "https://manicpixeldreamgirl.itch.io/modern...", 
            "-32x32 (and 16x16) RPG Tiles by Stephen Challener:" ,
            "https://opengameart.org/content/32x32-and-16x16-rpg..." ,
            "-Free Pixel Art Plants (Trees, Bushes, Grass) by Shaade: ",
            "https://shaade.itch.io/free-pixel-art",
            t("inst_back"),
        ]

        for idx, line in enumerate(lines):
            color = settings.COLOR_GOLD if idx % 2 != 0 else settings.COLOR_WHITE
            line_surf = settings.FONTS["small"].render(line, True, color)
            surface.blit(line_surf, (modal_rect.left + 25, modal_rect.top + 36 + idx * 16))
