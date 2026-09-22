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
        "hud_none": "Ninguno",
        
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
        "prompt_use_stairs": "Presiona E para usar las escaleras",
        "prompt_door_locked": "La puerta está cerrada con llave.",
        "prompt_door_barred": "La puerta está bloqueada con tablones clavados.",
        "prompt_door_barred_other_side": "La puerta está tapiada con tablones desde el otro lado.",
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
        "prompt_keypad": "Presiona E para introducir el código del pasadizo",
        "prompt_exit_sensor_active": "El sensor de seguridad bloquea la puerta de salida.",
        "prompt_pickup": "Presiona E para recoger",
        "prompt_search": "Presiona E para revisar",

        # Survivor Notes
        "note_first_room_title": "Nota Arrugada: Consejos de Supervivencia",
        "note_first_room_body": "Si escuchas el silbido acercándose, no intentes correr... esconderte es tu única salvación. Métete en los armarios o agáchate debajo de las mesas para que no pueda verte. Aguanta la respiración hasta que se aleje.",
        "note_kitchen_title": "Nota apresurada de Jose Gregorio",
        "note_kitchen_body": "Si encuentras esto, logré huir hacia el piso superior. Dejé la ganzúa pegada aquí para ti. Úsala en la vitrina del comedor contiguo: allí guardaban llaves viejas de la cabaña. ¡No hagas ruido, esa criatura escucha todo!",
        "note_hallway_title": "Jesus...",
        "note_hallway_body": "Los silbidos son una trampa mortal. Si se oyen cerca, está lejos... pero si los escuchas como un susurro en tu nuca, escóndete de inmediato. La caja fuerte del dormitorio principal tiene la llave de salida, pero necesitas la llave antigua.",
        "note_lower_hallway_title": "Nota Ensangrentada: Salida",
        "note_lower_hallway_body": "Tengo que escapar por la sala principal. La puerta exterior está asegurada con un sistema electrónico y cadenas pesadas. Necesito buscar herramientas en las habitaciones contiguas para abrir el paso.",
        "note_dining_room_title": "Diario de Jose Gregorio: La Barricada",
        "note_dining_room_body": "Tapié la puerta que conecta con la sala usando tablones para detener a la bestia. Dejé la ganzúa en la cocina y guardé la llave antigua en la vitrina de este comedor. Necesitarás una palanca o barreta para arrancar las maderas de la puerta.",
        "note_fuse_warning_title": "Aviso: Cuadro Eléctrico",
        "note_fuse_warning_body": "El sistema de seguridad de la puerta de escape está energizado. Para desconectarlo, hay que subir al cuarto del generador en el piso superior y restaurar los fusibles con la llave de circuitos.",
        "note_master_safe_title": "Pista: La Caja Fuerte",
        "note_master_safe_body": "La combinación de la caja fuerte es difícil, pero el mecanismo hace un chasquido metálico especial cuando la perilla alcanza el número correcto. Escucha con atención cada rotación.",
        "note_study_title": "Documento del Arquitecto: Pasaje de Emergencia",
        "note_study_body": "El túnel de servicio entre el dormitorio principal y la bodega permite trasladar provisiones en secreto. El cerrojo de combinación está configurado con el año de construcción de la finca: 1973. Si esa bestia acecha el pasillo central, este túnel es el único atajo seguro.",
        "note_bathroom_title": "Nota Manchada: Dolor",
        "note_bathroom_body": "No aguanto mas, ayer vi como ese ser maligno le quebro todos los huesos a zadkiel... ya no aguanto los silbidos, este puede ser mi final",
        "note_secret_passage_title": "Nota de zadkiel",
        "note_secret_passage_body": "He logrado sobrevivir por los corredores del dormitorio y el cuarto de estudio, peo siento mucha hambre y manguangua... solo hay una cosa para comer",

        # Monologues / Thoughts
        "thought_got_lockpick": "Jose gregorio me dejo una Ganzúa...",
        "thought_note_got_lockpick": "Encontré una Ganzúa doblada dentro de la nota de Jose gregorio.",
        "thought_projectile_crash": "¡El objeto hizo un estruendo al estrellarse!",
        "thought_got_old_key": "Conseguí una Llave Antigua de la vitrina.",
        "thought_got_exit_key": "¡La caja fuerte contenía la Llave de Salida del Bosque!",
        "thought_unbolted": "He descorrido el cerrojo. ¡El pasaje hacia el comedor está abierto!",
        "thought_door_unbarred": "He retirado los tablones con la palanca.",
        "thought_door_barred_other_side": "Está bloqueada con tablones por el otro lado. Tendré que encontrar otra forma de llegar y quitarlos.",
        "thought_fuse_box": "La caja de fusibles principal. Parece que los cables están desconectados... tal vez pueda restaurar la energía más tarde.",
        "thought_fuse_box_locked": "La caja de fusibles está cerrada con llave. Debe haber una llave en algún lugar abajo...",
        "thought_got_fuse_key": "¡Encontré la llave de la caja de fusibles! Tendré que volver al cuarto de arriba con cuidado...",
        "thought_exit_no_power": "La puerta de salida tiene un sensor de seguridad activo. Debo reactivar la energía en la caja de fusibles arriba.",
        "thought_exit_locked_chains": "Las cadenas están aseguradas con un candado. Necesito la llave del bosque de la caja fuerte.",
        "thought_passage_unlocked": "¡El cerrojo electrónico se abrió! El pasadizo secreto ahora está desbloqueado desde ambos lados.",
        
        # Instructions Modal
        "inst_move": "WASD / Flechas : Moverse",
        "inst_flashlight": "F : Encender / Apagar Linterna",
        "inst_interact": "E : Interactuar / Esconderse / Abrir",
        "inst_throw": "Q / Espacio : Lanzar objeto en mano (75% Stun, 25% Furia)",
        "inst_objectives": "TAB : Libreta de Objetivos",
        "inst_pause": "P / ESC : Pausa",
        "inst_fullscreen": "F11 / Alt+Enter : Pantalla Completa",
        "inst_exit": "ESC cuando estas en el juego y aceptas la confirmacion",
        "inst_warning": "Atención: Cuando escuches el silbido lejano, ¡está muy cerca!",
        "inst_back": "Presiona ENTER para regresar",

        # Confirmation Menu
        "confirm_quit_title": "¿SEGURO QUE DESEAS SALIR?",
        "menu_yes": "Sí",
        "menu_no": "No",

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
        "obj_current_task": "Misión Actual:",
        "obj_explore": "Explora la casa y busca una salida al exterior.",
        "obj_kitchen_lockpick": "Consigue la ganzúa dejada en la cocina.",
        "obj_dining_cabinet": "Abre la vitrina del comedor con la ganzúa para conseguir la llave antigua.",
        "obj_crowbar": "Encuentra la palanca y retira los tablones de la puerta hacia la sala.",
        "obj_fuse_power": "Restaura la energía en la caja de fusibles (piso superior) para desactivar el sensor.",
        "obj_master_safe": "Abre el dormitorio principal y descifra la caja fuerte para obtener la llave del bosque.",
        "obj_escape_forest": "¡Desbloquea las cadenas de la puerta de salida en la sala y escapa!",
        "obj_completed_stamp": "[COMPLETADO]",
        "obj_close": "Presiona TAB o ESC para cerrar la libreta.",
        
        # Minigames
        "minigame_keypad_title": "CERRADURA DE SEGURIDAD",
        "minigame_keypad_hint": "Introduce la clave de 4 dígitos y presiona ENTER",
        "keypad_success": "¡CÓDIGO CORRECTO! ATENDIDO",
        "keypad_error": "¡CÓDIGO ERRÓNEO!",
        "minigame_keypad_controls": "[0-9] Teclado  |  [ENTER] Confirmar  |  [ESC] Salir",
        "minigame_crowbar_title": "RETIRAR TABLÓN - PALANCA",
        "minigame_crowbar_planks_left": "Tablones restantes: {count}",
        "minigame_crowbar_break": "¡¡CRACK!! ¡TABLÓN ARRANCADO!",
        "minigame_crowbar_action": "¡¡PRESIONA [ESPACIO] RÁPIDAMENTE!!",
        "minigame_crowbar_controls": "[ESPACIO / E] Hacer palanca  |  [ESC] Soltar y huir",
        "minigame_fuse_title": "CAJA DE FUSIBLES - ENERGÍA",
        "minigame_fuse_hint": "Conecta los terminales del mismo color",
        "minigame_fuse_controls": "[W/S/Flechas] Navegar  |  [ESPACIO] Conectar  |  [ESC] Salir",
        "minigame_fuse_connected": "¡Circuito cerrado!",
        "minigame_fuse_shortcircuit": "¡¡CORTOCIRCUITO!! ¡Chispazo ruidoso!",
        "minigame_safe_title": "CAJA FUERTE - COMBINACIÓN",
        "minigame_safe_hint": "Escucha el clic acústico al girar...",
        "minigame_safe_controls": "[A/D] Girar  |  [ESPACIO] Fijar número  |  [ESC] Salir",
        "minigame_safe_latch": "¡Pestillo {count} fijado!",
        "minigame_safe_jam": "¡Mecanismo trabado! ¡Ruido metálico!",
        "minigame_lockpick_hint": "Busca el ángulo sin forzar...",
        "minigame_lockpick_controls": "[A/D] Ángulo  |  [W / ESPACIO] Girar  |  [ESC] Salir",
        "minigame_lockpick_slip": "¡La ganzúa resbaló con fuerza! ¡Alerta!",
        
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
        "hud_none": "None",
        
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
        "prompt_use_stairs": "Press E to use the stairs",
        "prompt_door_locked": "The door is locked tight.",
        "prompt_door_barred": "The door is blocked with nailed planks.",
        "prompt_door_barred_other_side": "The door is barred with planks from the other side.",
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
        "prompt_keypad": "Press E to enter the passage passcode",
        "prompt_exit_sensor_active": "The security sensor blocks the exit door.",
        "prompt_pickup": "Press E to pick up",
        "prompt_search": "Press E to search",

        # Survivor Notes
        "note_first_room_title": "Crumpled Note: Survival Advice",
        "note_first_room_body": "If you hear the whistle drawing near, do not run... hiding is your only salvation. Slip into wardrobes or crawl under tables so he cannot see you. Hold your breath until he wanders away.",
        "note_kitchen_title": "Jose Gregorio's Hurried Note",
        "note_kitchen_body": "If you find this, I managed to flee upstairs. I left the lockpick taped here for you. Use it on the dining room cabinet next door: they kept old cabin keys in there. Keep quiet, that creature hears everything!",
        "note_hallway_title": "Jesus...",
        "note_hallway_body": "The whistles are a deadly trap. If they sound close, he is far... but if you hear them like a whisper on your neck, hide immediately. The master bedroom safe has the exit key, but you need the old key.",
        "note_lower_hallway_title": "Bloodstained Note: The Exit",
        "note_lower_hallway_body": "I have to escape through the main living room. The exterior door is secured by an electronic system and heavy chains. I must search adjoining rooms for tools to clear the way.",
        "note_dining_room_title": "Jose Gregorio's Journal: The Barricade",
        "note_dining_room_body": "I barricaded the door connecting to the living room with planks to stall the beast. I left the lockpick in the kitchen and stored the old key inside this dining room cabinet. You'll need a crowbar to pry the planks off.",
        "note_fuse_warning_title": "Notice: Electrical Breaker",
        "note_fuse_warning_body": "The exit door security lock is energized. To disconnect it, head upstairs to the generator room and restore the fuse box with the circuit key.",
        "note_master_safe_title": "Clue: The Safe",
        "note_master_safe_body": "The safe combination is difficult, but the internal gear produces a distinctive metallic click when the dial aligns. Listen carefully with each rotation.",
        "note_study_title": "Architect's Blueprint: Emergency Passage",
        "note_study_body": "The service tunnel between the master bedroom and the storage room allows moving supplies covertly. The combination lock is set to the estate's construction year: 1973. If that beast lurks in the central hallway, this tunnel is the only safe shortcut.",
        "note_bathroom_title": "Stained Note: Pain",
        "note_bathroom_body": "I cannot take this anymore. Yesterday I saw how that thing broke all of zadkiel's bones, I can't handle the whistles anymore...",
        "note_secret_passage_title": "Zadkiel's Note",
        "note_secret_passage_body": "I have managed to survive thanks to the corridors from the bedroom and the studyroom, but i am manguanguing and hungry, there's only one thing to eat ",

        # Monologues / Thoughts
        "thought_got_lockpick": "Jose Gregorio left me a Lockpick...",
        "thought_note_got_lockpick": "Found a Lockpick folded inside Jose Gregorio's note.",
        "thought_projectile_crash": "The object crashed with a loud noise!",
        "thought_got_old_key": "Obtained an Old Key from the display case.",
        "thought_got_exit_key": "The safe contained the Forest Exit Key!",
        "thought_unbolted": "I've unbolted the door. The passage to the dining room is now open!",
        "thought_door_unbarred": "Pried off the wooden planks with the crowbar.",
        "thought_door_barred_other_side": "It's barred with planks from the other side. I'll have to find another way around to pry them off.",
        "thought_fuse_box": "The main fuse box. The wiring seems disconnected... maybe I can restore power later.",
        "thought_fuse_box_locked": "The fuse box is locked. There must be a key somewhere downstairs...",
        "thought_got_fuse_key": "Found the fuse box key! I'll have to head back to the upstairs room carefully...",
        "thought_exit_no_power": "The exit door has an active security sensor. I must restore power at the fuse box upstairs.",
        "thought_exit_locked_chains": "The chains are secured with a padlock. I need the forest key from the safe.",
        "thought_passage_unlocked": "The electronic lock clicked open! The secret passage is now unlocked from both sides.",

        # Instructions Modal
        "inst_move": "WASD / Arrow Keys : Move Andreas",
        "inst_flashlight": "F : Toggle Flashlight",
        "inst_interact": "E : Interact / Hide / Open Door",
        "inst_throw": "Q / Space : Throw equipped item (75% Stun, 25% Enrage)",
        "inst_objectives": "TAB : Objectives Log",
        "inst_pause": "P / ESC : Pause",
        "inst_fullscreen": "F11 / Alt+Enter : Toggle Fullscreen",
        "inst_exit": "ESC when you're in the game, then you confirm with yes",
        "inst_warning": "Warning: When the whistle sounds far away, HE IS NEAR!",
        "inst_back": "Press ENTER to return",
        # Confirmation Menu
        "confirm_quit_title": "ARE YOU SURE YOU WANT TO QUIT?",
        "menu_yes": "Yes",
        "menu_no": "No",    
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
        "obj_current_task": "Current Mission:",
        "obj_explore": "Explore the cabin and search for an exit.",
        "obj_kitchen_lockpick": "Retrieve the lockpick left in the kitchen.",
        "obj_dining_cabinet": "Unlock the dining room cabinet to get the old key.",
        "obj_crowbar": "Find the crowbar and pry off the planks to the living room.",
        "obj_fuse_power": "Restore power at the upstairs fuse box to deactivate the exit sensor.",
        "obj_master_safe": "Unlock the master bedroom and crack the safe to get the forest key.",
        "obj_escape_forest": "Unlock the chains on the living room exit door and escape!",
        "obj_completed_stamp": "[COMPLETED]",
        "obj_close": "Press TAB or ESC to close notebook.",
        
        # Minigames
        "minigame_keypad_title": "SECURITY KEYPAD",
        "minigame_keypad_hint": "Enter 4-digit code and press ENTER",
        "keypad_success": "CORRECT CODE! UNLOCKED",
        "keypad_error": "INCORRECT CODE!",
        "minigame_keypad_controls": "[0-9] Keypad  |  [ENTER] Confirm  |  [ESC] Exit",
        "minigame_crowbar_title": "REMOVE PLANK - CROWBAR",
        "minigame_crowbar_planks_left": "Planks remaining: {count}",
        "minigame_crowbar_break": "CRACK!! PLANK RIPPED OFF!",
        "minigame_crowbar_action": "PRESS [SPACE] RAPIDLY!!",
        "minigame_crowbar_controls": "[SPACE / E] Pry  |  [ESC] Drop and flee",
        "minigame_fuse_title": "FUSE BOX - POWER",
        "minigame_fuse_hint": "Connect the terminals of the same color",
        "minigame_fuse_controls": "[W/S/Arrows] Navigate  |  [SPACE] Connect  |  [ESC] Exit",
        "minigame_fuse_connected": "Circuit closed!",
        "minigame_fuse_shortcircuit": "SHORT CIRCUIT!! Loud spark!",
        "minigame_safe_title": "SAFE - COMBINATION",
        "minigame_safe_hint": "Listen for the acoustic click as you turn...",
        "minigame_safe_controls": "[A/D] Turn  |  [SPACE] Lock number  |  [ESC] Exit",
        "minigame_safe_latch": "Latch {count} locked!",
        "minigame_safe_jam": "Mechanism jammed! Metallic noise!",
        "minigame_lockpick_hint": "Find the angle without forcing it...",
        "minigame_lockpick_controls": "[A/D] Angle  |  [W / SPACE] Turn  |  [ESC] Exit",
        "minigame_lockpick_slip": "The lockpick slipped hard! Alert!",
        
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
