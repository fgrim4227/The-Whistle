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
        "item_key": "Llave del Bosque",
        "item_crowbar": "Palanca",
        "item_throwable": "Objeto Arrojable",
        "item_lockpick": "Ganzúa",
        "item_old_key": "Llave Antigua",
        "item_cabinet": "Vitrina",
        "item_safe": "Caja Fuerte",
        "item_note": "Nota",
        "item_fuse_box": "Caja de fusibles",
        "item_fuse_key": "Llave de la Caja de Fusibles",

        # Interactions & Prompts
        "prompt_interact": "Presiona E para interactuar",
        "prompt_hide": "Presiona E para esconderte",
        "prompt_exit_hide": "Presiona E para salir del escondite",
        "prompt_open_door": "Presiona E para abrir",
        "prompt_open_door_danger": "Presiona E para abrir (¡Se escucha respiración pesada al otro lado!)",
        "prompt_use_stairs": "Presiona E para usar las escaleras",
        "prompt_door_locked": "La puerta está cerrada con llave.",
        "prompt_door_barred": "La puerta está bloqueada con tablones clavados.",
        "prompt_door_bolted": "La puerta está trabada con un cerrojo desde el otro lado.",
        "prompt_unbolt_door": "Presiona E para descorrer el cerrojo",
        "prompt_pick_cabinet": "Presiona E para forzar la vitrina con la ganzúa",
        "prompt_cabinet_locked": "La vitrina tiene una cerradura fina. Necesitas una ganzúa.",
        "prompt_open_safe": "Presiona E para abrir la caja fuerte",
        "prompt_read_note": "Presiona E para leer la nota",
        "note_close_hint": "[ E / ESPACIO ] Doblar y guardar nota",
        "prompt_fuse_box": "Presiona E para inspeccionar la caja de fusibles",
        "prompt_fuse_box_locked": "La caja de fusibles está cerrada con llave.",
        "prompt_open_fuse_box": "Presiona E para abrir con la llave de fusibles",
        "prompt_door_banging": "¡ALGO ESTÁ GOLPEANDO LA PUERTA VIOLENTAMENTE! ¡ESCÓNDETE!",
        "prompt_exit_sensor_active": "El sensor de seguridad bloquea la puerta de salida.",
        "prompt_talk_npc": "Presiona E para hablar con {name}",
        "prompt_pickup": "Presiona E para recoger",
        "prompt_search": "Presiona E para revisar",

        # Survivor Notes
        "note_first_room_title": "Nota Arrugada: Consejos de Supervivencia",
        "note_first_room_body": "Si escuchas el silbido acercándose, no intentes correr... esconderte es tu única salvación. Métete en los armarios o agáchate debajo de las mesas para que no pueda verte. Aguanta la respiración hasta que se aleje.",
        "note_kitchen_title": "Nota apresurada de Jose Gregorio",
        "note_kitchen_body": "Si encuentras esto, logré huir hacia el piso superior. Dejé la ganzúa pegada aquí para ti. Úsala en la vitrina del comedor contiguo: allí guardaban llaves viejas de la cabaña. ¡No hagas ruido, esa criatura escucha todo!",
        "note_hallway_title": "Jesus...",
        "note_hallway_body": "Los silbidos son una trampa mortal. Si se oyen cerca, está lejos... pero si los escuchas como un susurro en tu nuca, escóndete de inmediato. La caja fuerte del dormitorio principal tiene la llave de salida, pero necesitas la llave antigua.",

        # NPC Elena Story Dialogues
        "elena_dialogue_intro": "¡Andreas! Menos mal... El Silbón trancó la salida con tablones. Toma esta ganzúa, la escondí en mi delantal... busca en el comedor contiguo.",
        "elena_dialogue_dining": "Revisa la vitrina del comedor con la ganzúa. Allí guardaban las llaves viejas de la cabaña.",
        "elena_dialogue_bedroom": "Esa llave antigua abre el cuarto principal de arriba... cuidado, El Silbón merodea por las escaleras.",
        "elena_dialogue_crowbar": "Busca la palanca en el almacén para quitar los tablones de la sala.",
        "elena_dialogue_escape": "¡La salida está libre! ¡Abre la puerta del bosque y salgamos de aquí!",

        # Monologues / Thoughts
        "thought_got_lockpick": "Jose gregorio me dejo una Ganzúa...",
        "thought_note_got_lockpick": "Encontré una Ganzúa doblada dentro de la nota de Jose gregorio.",
        "thought_projectile_crash": "¡El objeto hizo un estruendo al estrellarse!",
        "thought_got_old_key": "Conseguí una Llave Antigua de la vitrina.",
        "thought_got_exit_key": "¡La caja fuerte contenía la Llave de Salida del Bosque!",
        "thought_unbolted": "He descorrido el cerrojo. ¡El pasaje hacia el comedor está abierto!",
        "thought_door_unbarred": "He retirado los tablones con la palanca.",
        "thought_fuse_box": "La caja de fusibles principal. Parece que los cables están desconectados... tal vez pueda restaurar la energía más tarde.",
        "thought_fuse_box_locked": "La caja de fusibles está cerrada con llave. Debe haber una llave en algún lugar abajo...",
        "thought_got_fuse_key": "¡Encontré la llave de la caja de fusibles! Tendré que volver al cuarto de arriba con cuidado...",
        "thought_exit_no_power": "La puerta de salida tiene un sensor de seguridad activo. Debo reactivar la energía en la caja de fusibles arriba.",
        "thought_exit_locked_chains": "Las cadenas están aseguradas con un candado. Necesito la llave del bosque de la caja fuerte.",
        
        # Instructions Modal
        "inst_move": "WASD / Flechas : Moverse",
        "inst_flashlight": "F : Encender / Apagar Linterna",
        "inst_interact": "E : Interactuar / Esconderse / Abrir",
        "inst_throw": "Q / Espacio : Lanzar objeto en mano (75% Stun, 25% Furia)",
        "inst_inventory": "1-5 / C : Seleccionar / Ciclar objeto en inventario",
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
        "thought_stairs_blocked": "Las escaleras hacia la planta baja están bloqueadas por ahora...",
        
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
        "item_key": "Forest Exit Key",
        "item_crowbar": "Crowbar",
        "item_throwable": "Throwable Object",
        "item_lockpick": "Lockpick",
        "item_old_key": "Old Key",
        "item_cabinet": "Cabinet",
        "item_safe": "Safe",
        "item_note": "Note",
        "item_fuse_box": "Fuse Box",
        "item_fuse_key": "Fuse Box Key",

        # Interactions & Prompts
        "prompt_interact": "Press E to interact",
        "prompt_hide": "Press E to hide",
        "prompt_exit_hide": "Press E to exit hiding spot",
        "prompt_open_door": "Press E to open",
        "prompt_open_door_danger": "Press E to open (Heavy breathing audible on the other side!)",
        "prompt_use_stairs": "Press E to use the stairs",
        "prompt_door_locked": "The door is locked tight.",
        "prompt_door_barred": "The door is blocked with nailed planks.",
        "prompt_door_bolted": "The door is bolted from the other side.",
        "prompt_unbolt_door": "Press E to unbolt the door",
        "prompt_pick_cabinet": "Press E to pick the display case lock",
        "prompt_cabinet_locked": "The display case has a delicate lock. You need a lockpick.",
        "prompt_open_safe": "Press E to open the safe",
        "prompt_read_note": "Press E to read the note",
        "note_close_hint": "[ E / SPACE ] Fold and stash note",
        "prompt_fuse_box": "Press E to inspect fuse box",
        "prompt_fuse_box_locked": "The fuse box is locked tight.",
        "prompt_open_fuse_box": "Press E to unlock fuse box with key",
        "prompt_door_banging": "SOMETHING IS VIOLENTLY BANGING ON THE DOOR! HIDE!",
        "prompt_exit_sensor_active": "The security sensor blocks the exit door.",
        "prompt_talk_npc": "Press E to talk to {name}",
        "prompt_pickup": "Press E to pick up",
        "prompt_search": "Press E to search",

        # Survivor Notes
        "note_first_room_title": "Crumpled Note: Survival Advice",
        "note_first_room_body": "If you hear the whistle drawing near, do not run... hiding is your only salvation. Slip into wardrobes or crawl under tables so he cannot see you. Hold your breath until he wanders away.",
        "note_kitchen_title": "Jose Gregorio's Hurried Note",
        "note_kitchen_body": "If you find this, I managed to flee upstairs. I left the lockpick taped here for you. Use it on the dining room cabinet next door: they kept old cabin keys in there. Keep quiet, that creature hears everything!",
        "note_hallway_title": "Jesus...",
        "note_hallway_body": "The whistles are a deadly trap. If they sound close, he is far... but if you hear them like a whisper on your neck, hide immediately. The master bedroom safe has the exit key, but you need the old key.",

        # NPC Elena Story Dialogues
        "elena_dialogue_intro": "Andreas! Thank goodness... The Whistler barred the exit. Take this lockpick from my apron... search the dining room next door.",
        "elena_dialogue_dining": "Check the dining room cabinet with the lockpick. They kept old cabin keys in there.",
        "elena_dialogue_bedroom": "That old key opens the master bedroom upstairs... be careful, The Whistler is lurking around the stairs.",
        "elena_dialogue_crowbar": "Find the crowbar in the storage room to pry the planks off the living room door.",
        "elena_dialogue_escape": "The exit is clear! Unlock the forest door and let's get out of here!",

        # Monologues / Thoughts
        "thought_got_lockpick": "Jose Gregorio left me a Lockpick...",
        "thought_note_got_lockpick": "Found a Lockpick folded inside Jose Gregorio's note.",
        "thought_projectile_crash": "The object crashed with a loud noise!",
        "thought_got_old_key": "Obtained an Old Key from the display case.",
        "thought_got_exit_key": "The safe contained the Forest Exit Key!",
        "thought_unbolted": "I've unbolted the door. The passage to the dining room is now open!",
        "thought_door_unbarred": "Pried off the wooden planks with the crowbar.",
        "thought_fuse_box": "The main fuse box. The wiring seems disconnected... maybe I can restore power later.",
        "thought_fuse_box_locked": "The fuse box is locked. There must be a key somewhere downstairs...",
        "thought_got_fuse_key": "Found the fuse box key! I'll have to head back to the upstairs room carefully...",
        "thought_exit_no_power": "The exit door has an active security sensor. I must restore power at the fuse box upstairs.",
        "thought_exit_locked_chains": "The chains are secured with a padlock. I need the forest key from the safe.",

        # Instructions Modal
        "inst_move": "WASD / Arrow Keys : Move Andreas",
        "inst_flashlight": "F : Toggle Flashlight",
        "inst_interact": "E : Interact / Hide / Open Door",
        "inst_throw": "Q / Space : Throw equipped item (75% Stun, 25% Enrage)",
        "inst_inventory": "1-5 / C : Select / Cycle inventory item",
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
        "thought_stairs_blocked": "The stairs down to the ground floor are blocked for now...",
        
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
