"""
Internationalization module (i18n).
Synchronized bilingual support in Spanish and English backed by settings.IS_ENGLISH boolean.
"""

from typing import Dict, Any
import settings

STRINGS: Dict[str, Dict[str, str]] = {
    "es": {
        # Main Menu
        "menu_title": "EL SILBÓN",
        "menu_subtitle": "Pesadilla en la Cabaña",
        "menu_start": "Comenzar Pesadilla",
        "menu_language": "Idioma: Español (Presiona L para cambiar)",
        "menu_instructions": "Controles e Instrucciones",
        "menu_quit": "Salir",
        "menu_select": "Usa las flechas / W-S y ENTER para seleccionar",
        
        # Pause Menu
        "pause_title": "PAUSA",
        "pause_resume": "Continuar",
        "pause_menu": "Volver al Menú Principal",

        # HUD and Status
        "hud_battery": "Batería",
        "hud_equipped": "Objeto",
        "hud_none": "Ninguno",
        "hud_hidden": "[ OCULTO EN EL ARMARIO - NO TE MUEVAS ]",
        "hud_silbon_near": "[ ¡EL SILBIDO SE ESCUCHA LEJOS... ESTÁ AQUÍ! ]",
        
        # Items
        "item_battery": "Batería",
        "item_key": "Llave",
        "item_crowbar": "Palanca",
        "item_throwable": "Objeto Arrojable",

        # Interactions & Prompts
        "prompt_interact": "Presiona E para interactuar",
        "prompt_hide": "Presiona E para esconderte",
        "prompt_exit_hide": "Presiona E para salir del escondite",
        "prompt_open_door": "Presiona E para abrir",
        "prompt_door_locked": "La puerta está cerrada con llave.",
        "prompt_door_barred": "La puerta está bloqueada con tablones clavados.",
        "prompt_door_banging": "¡ALGO ESTÁ GOLPEANDO LA PUERTA VIOLENTAMENTE! ¡ESCÓNDETE!",
        "prompt_talk_npc": "Presiona E para hablar con {name}",
        "prompt_pickup": "Presiona E para recoger",
        "prompt_search": "Presiona E para revisar",
        
        # Instructions Modal
        "inst_move": "WASD / Flechas : Moverse",
        "inst_flashlight": "F : Encender / Apagar Linterna",
        "inst_interact": "E : Interactuar / Esconderse / Abrir",
        "inst_throw": "Q / Espacio : Lanzar objeto en mano (75% Stun, 25% Furia)",
        "inst_objectives": "TAB : Libreta de Objetivos",
        "inst_pause": "P / ESC : Pausa",
        "inst_warning": "Atención: Cuando escuches el silbido lejano, ¡está muy cerca!",
        "inst_back": "Presiona ENTER para regresar",

        # Internal Monologues (Paramedic)
        "thought_intro": "Mi cabeza... ¿dónde diablos estoy? Debo encontrar mi linterna y salir de aquí.",
        "thought_dark": "Está demasiado oscuro. No debo malgastar la batería de la linterna.",
        "thought_scared": "Solo respira... mantén la calma... ¿en qué me he metido?",
        "thought_silbon_whistle": "¿Ese silbido...? Suena distante, pero siento su respiración cerca...",
        "thought_door_locked": "Necesito encontrar una herramienta o la llave adecuada.",
        "thought_monster_stunned": "¡Le di! Debo correr antes de que se recupere.",
        "thought_monster_enraged": "¡Maldición! ¡Se enfureció, es demasiado rápido!",
        
        # Objective Log
        "obj_title": "OBJETIVOS DE SUPERVIVENCIA",
        "obj_1_flashlight": "1. Busca una fuente de luz o pilas de repuesto.",
        "obj_2_explore": "2. Explora las habitaciones contiguas con sigilo.",
        "obj_3_crowbar": "3. Encuentra la palanca para retirar los tablones del pasillo.",
        "obj_4_key": "4. Encuentra la llave maestra de la puerta principal.",
        "obj_5_escape": "5. Abre la puerta de salida y escapa hacia el bosque.",
        "obj_close": "Presiona TAB o ESC para cerrar la libreta.",
        
        # Minigames
        "minigame_crowbar_title": "Retirando tablones",
        "minigame_crowbar_hint": "Presiona ESPACIO en el momento exacto para hacer palanca",
        "minigame_safe_title": "Descifrando la caja fuerte",
        "minigame_safe_hint": "Gira el dial con A/D hasta escuchar el clic mecánico",
        
        # Game Over / Victory
        "gameover_title": "TE HA ATRAPADO",
        "gameover_quote": "El Silbón llevó tus huesos en su saco...",
        "gameover_restart": "Presiona ENTER para intentar sobrevivir nuevamente",
        
        "victory_title": "¡LOGRASTE ESCAPAR!",
        "victory_quote": "Corriste a través de la densa niebla del bosque hasta el amanecer.",
        "victory_restart": "Presiona ENTER para volver al menú principal",
    },
    "en": {
        # Main Menu
        "menu_title": "THE WHISTLER",
        "menu_subtitle": "Nightmare at the Cabin",
        "menu_start": "Begin Nightmare",
        "menu_language": "Language: English (Press L to toggle)",
        "menu_instructions": "Controls & Instructions",
        "menu_quit": "Quit",
        "menu_select": "Use Arrows / W-S and ENTER to select",
        
        # Pause Menu
        "pause_title": "PAUSE",
        "pause_resume": "Resume",
        "pause_menu": "Return to Main Menu",

        # HUD and Status
        "hud_battery": "Battery",
        "hud_equipped": "Item",
        "hud_none": "None",
        "hud_hidden": "[ HIDDEN IN WARDROBE - DO NOT MOVE ]",
        "hud_silbon_near": "[ THE WHISTLE SOUNDS FAR... HE IS HERE! ]",
        
        # Items
        "item_battery": "Battery",
        "item_key": "Key",
        "item_crowbar": "Crowbar",
        "item_throwable": "Throwable Object",

        # Interactions & Prompts
        "prompt_interact": "Press E to interact",
        "prompt_hide": "Press E to hide",
        "prompt_exit_hide": "Press E to exit hiding spot",
        "prompt_open_door": "Press E to open",
        "prompt_door_locked": "The door is locked tight.",
        "prompt_door_barred": "The door is blocked with nailed planks.",
        "prompt_door_banging": "SOMETHING IS VIOLENTLY BANGING ON THE DOOR! HIDE!",
        "prompt_talk_npc": "Press E to talk to {name}",
        "prompt_pickup": "Press E to pick up",
        "prompt_search": "Press E to search",
        
        # Instructions Modal
        "inst_move": "WASD / Arrow Keys : Move Andreas",
        "inst_flashlight": "F : Toggle Flashlight",
        "inst_interact": "E : Interact / Hide / Open Door",
        "inst_throw": "Q / Space : Throw equipped item (75% Stun, 25% Enrage)",
        "inst_objectives": "TAB : Objectives Log",
        "inst_pause": "P / ESC : Pause",
        "inst_warning": "Warning: When the whistle sounds far away, HE IS NEAR!",
        "inst_back": "Press ENTER to return",

        # Internal Thoughts (Paramedic)
        "thought_intro": "My head... where on earth am I? I need to find my flashlight and get out.",
        "thought_dark": "It's pitch black. I can't afford to waste flashlight battery.",
        "thought_scared": "Just breathe... stay calm... what have I gotten myself into?",
        "thought_silbon_whistle": "That whistling...? It sounds distant, but I can feel his breath near...",
        "thought_door_locked": "I need to find the right key or a prying tool.",
        "thought_monster_stunned": "Direct hit! I must run before he recovers.",
        "thought_monster_enraged": "Damn it! He's enraged, he's moving way too fast!",
        
        # Objective Log
        "obj_title": "SURVIVAL OBJECTIVES",
        "obj_1_flashlight": "1. Find a light source or spare batteries.",
        "obj_2_explore": "2. Stealthily explore the adjacent rooms.",
        "obj_3_crowbar": "3. Locate a crowbar to pry the boarded hallway door.",
        "obj_4_key": "4. Locate the master key to the main entrance.",
        "obj_5_escape": "5. Unlock the exit door and flee into the dark woods.",
        "obj_close": "Press TAB or ESC to close notebook.",
        
        # Minigames
        "minigame_crowbar_title": "Prying Wooden Planks",
        "minigame_crowbar_hint": "Press SPACE at the right moment to exert force",
        "minigame_safe_title": "Cracking the Safe",
        "minigame_safe_hint": "Rotate the dial with A/D until hearing the acoustic click",
        
        # Game Over / Victory
        "gameover_title": "YOU HAVE BEEN CAUGHT",
        "gameover_quote": "The Whistler placed your bones inside his sack...",
        "gameover_restart": "Press ENTER to attempt to survive again",
        
        "victory_title": "YOU ESCAPED!",
        "victory_quote": "You dashed through the thick misty forest until dawn broke.",
        "victory_restart": "Press ENTER to return to Main Menu",
    },
}


def get_language() -> str:
    return "en" if settings.IS_ENGLISH else "es"


def set_language(lang: str) -> None:
    settings.IS_ENGLISH = (lang == "en")


def toggle_language() -> str:
    settings.IS_ENGLISH = not settings.IS_ENGLISH
    return get_language()


def t(key: str, **kwargs: Any) -> str:
    lang = get_language()
    text = STRINGS.get(lang, {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
