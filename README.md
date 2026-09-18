# The Whistle (El Silbón) — 2D Survival Horror

<div align="center">

**Final Project — Video Game Programming (6th Semester)**  
**Developers:** Francisco Grimaldo & Isaac Montes  
**Engine & Libraries:** Python 3.12, Pygame 2.6, Gale Engine  

[![Language: English](https://img.shields.io/badge/Language-English-blue.svg)](#-the-whistle---2d-survival-horror)
[![Idioma: Español](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-red.svg)](#-el-silb%C3%B3n---survival-horror-2d)

[ 🇺🇸 Read in English ](#-the-whistle---2d-survival-horror) &nbsp;|&nbsp; [ 🇪🇸 Leer en Español ](#-el-silb%C3%B3n---survival-horror-2d)

</div>

---

## 🇺🇸 The Whistle - 2D Survival Horror

### 📖 Synopsis & Story

Driving late at night along a desolated highway, an off-duty paramedic named **Andreas** suffers a sudden mechanical breakdown. Spotting a faint light flickering in the dense woodland, he ventures off the road seeking help. Upon reaching an isolated cabin, a blood-chilling shriek echoes from within; rushing through the entrance to intervene, he is struck by a blunt blow to the head and plunges into unconsciousness.

Andreas awakens alone in a pitch-black chamber, disoriented and clutching a flashlight with barely any battery charge. He quickly discovers he is trapped in the domain of **El Silbón**, the legendary vengeful wanderer of Venezuelan folklore. To escape with his life, Andreas must explore the interconnected cabin, solve mechanical and electronic puzzles, pry barred doors, hide in the shadows, and evade an unrelenting hunter guided by sound and intuition.

---

### 🎮 Core Gameplay Mechanics

1. **The Folklore Whistle Paradox:**
   - *If the whistling sounds distant, El Silbón is right next to you.*
   - *If the whistling sounds loud and clear, he is far away.*
   - Dynamic 3D audio attenuation challenges the player's acoustic awareness in real time.

2. **Volumetric Directional Flashlight:**
   - The cabin is shrouded in dense ambient darkness.
   - The flashlight casts a multi-layered, smooth volumetric cone of light oriented to the player's facing direction (`F` to toggle).
   - Battery drains continuously while on. Spare batteries must be scavenged to restore charge.
   - Light instantly catches El Silbón's attention from across the room — turn it off when he approaches!

3. **Stealth & Concealment:**
   - Wardrobes, dining tables, and desks serve as physical hiding spots (`E` to enter/exit).
   - Concealment drops active pursuit, provided the flashlight is turned off and the monster does not witness you entering.
   - Beware: lingering near an alerted monster may prompt him to search the furniture directly!

4. **Tactical Throwables (Stun vs. Enrage):**
   - Scavenge stones and tools to throw (`Q` key) as distractions or last-ditch defenses.
   - **80% Chance:** Stuns El Silbón for 3.0–4.5 seconds, providing a window to flee.
   - **20% Chance:** Triggers a lethal Berserk rush, dramatically boosting his movement speed.
   - Projectiles colliding with walls or furniture create loud acoustic impacts that lure the monster to investigate.

5. **Granny-Style Single-Slot Inventory:**
   - Realistic physical capacity: Andreas carries exactly **1 active tool** in hand at a time.
   - Drop items on the floor (`G` key) anytime to swap or strategically leave keys near their respective doors. Dropped items remain persistently in-world across room transitions.

6. **Real-Time Active Minigames & Puzzles:**
   - **Prying Barricades (Crowbar):** Button-mashing tug-of-war to wrench planks off sealed doors.
   - **Vintage Cabinet (Lockpick):** Tension-angle lockpicking simulating pick stress and shear lines.
   - **Master Safe (Acoustic Dial):** Precision rotary combination lock requiring acoustic listening for internal tumbler clicks.
   - **Fuse Box (Wire Patching):** Repairing damaged circuit terminals to restore electricity to the cabin.
   - **Security Keypad:** 4-digit code puzzle with illuminated buttons, tactile input beeps, and buzzer alarms.
   - *Real-time tension:* El Silbón continues stalking and moving through the cabin while minigames are active.

7. **Director AI & A\* Navigation (Alien: Isolation Inspiration):**
   - The **Director AI** evaluates pacing, player safety, and ambient tension, feeding organic perceptual cues to the monster without giving away exact coordinates.
   - El Silbón navigates complex cabin geometry via grid-based **A\* Pathfinding**, routing around obstacles, furniture margins, and through doorways.

8. **Environmental Lore & Guidance:**
   - Interactive parchment notes left by survivor **José Gregorio** provide organic hints, lore, and guidance, replacing intrusive UI banners.

9. **Display & Fullscreen Support:**
   - Native hardware-accelerated integer scaling (`pygame.SCALED | pygame.RESIZABLE`) preserving a crisp 16:9 virtual canvas (512x288) on any monitor.
   - Instant fullscreen toggle via `F11` or `Alt + Enter`.

---

### 🕹️ Controls

| Action | Primary Key | Alternative / Secondary |
| :--- | :--- | :--- |
| **Move** | `W`, `A`, `S`, `D` | Arrow Keys (`↑`, `←`, `↓`, `→`) |
| **Sprint** | `Left Shift` | `Right Shift` |
| **Interact / Open / Hide** | `E` | `Space` |
| **Toggle Flashlight** | `F` | — |
| **Throw Equipped Item** | `Q` | `Space` (when holding throwable) |
| **Drop Held Item** | `G` | — |
| **Objectives Notebook** | `TAB` | — |
| **Pause Menu** | `P` | — |
| **Toggle Language (ES / EN)** | `L` | — |
| **Toggle Fullscreen** | `F11` | `Alt` + `Enter` |
| **Cancel / Exit / Close Minigame** | `ESC` | — |

---

### 🏗️ Software Architecture & Design Patterns

The codebase is engineered with strict modularity, clean separation of concerns, and classic game development patterns:

- **Hierarchical State Stack (`gale.state.StateStack`):** Manages transitions and layered modal overlays (`WarningIntro`, `StartState`, `IntroRoadState`, `IntroForestState`, `PlayState`, `PauseState`, `ObjectiveState`, `NoteState`, `GameOverState`, `VictoryState`).
- **Finite State Machines (FSM):**
  - **Player:** `PlayerIdleState`, `PlayerWalkState`, `PlayerHidingState`.
  - **Monster (El Silbón):** `MonsterPatrolState`, `MonsterMovingToDoorState`, `MonsterKnockingState`, `MonsterInvestigateState`, `MonsterStalkingState`, `MonsterChaseState`, `MonsterBreathingState`, `MonsterCatchingState`, `MonsterBerserkState`, `MonsterStunnedState`.
- **Command Pattern (`src/commands.py`):** Decouples keyboard input handling from entity action execution.
- **Strategy & Dispatcher Pattern (`src/definitions/interactions.py`):** Replaces monolithic `if/elif` blocks with table-driven interaction handlers for floor items, furniture, notes, and doors.
- **Factory Pattern (`src/minigames/MinigameFactory.py`):** Polymorphic instantiation and dynamic registration of real-time puzzle overlays.
- **Data-Driven Level & Entity Definitions (`src/definitions/`):** Centralizes rooms, door linkages, waypoints, items, and animation specifications.
- **Tiled Map Integration (`src/world/TiledLevelLoader.py`):** Parses multi-layer orthogonal JSON maps exported from Tiled, dynamically caching tilesets and collision boundaries.
- **Volumetric Lighting System (`src/systems/LightingSystem.py`):** Multi-layered subtractive stencil mask blending ambient darkness, personal player halos, and directional flashlight cones.
- **Spatial Audio Manager (`src/systems/AudioManager.py`):** 16 dedicated mixer channels providing distance attenuation, door-listening muffling, and folklore whistle modulation.

---

### 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/fgrim4227/The-Whistle.git
   cd The-Whistle
   ```

2. **Create & Activate Virtual Environment:**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Game:**
   ```bash
   python main.py
   ```

*(Note: Pre-compiled standalone Windows executables are also published in the repository's Releases section).*

---

## 🇪🇸 El Silbón - Survival Horror 2D

### 📖 Sinopsis e Historia

Mientras viaja de noche por una solitaria carretera nacional, el vehículo de un paramédico fuera de servicio llamado **Andreas** sufre una repentina avería mecánica. Al divisar una tenue luz parpadeando en la espesura del bosque, se adentra buscando auxilio. Al aproximarse a una cabaña aislada, un desgarrador grito femenino lo alerta; sin dudarlo, irrumpe para socorrerla, pero al cruzar el umbral recibe un golpe seco en la cabeza y cae inconsciente.

Andreas despierta solo en una habitación en penumbra total, desorientado y con una linterna con batería precaria. Pronto descubre que la cabaña es el dominio de **El Silbón**, el legendario espectro errante del folclore llanero. Para escapar con vida, Andreas deberá explorar la cabaña interconectada, resolver acertijos mecánicos y electrónicos, forzar barricadas, esconderse en las sombras y evadir a un cazador implacable guiado por el sonido y la intuición.

---

### 🎮 Mecánicas Principales

1. **La Paradoja del Silbido (Mito Folclórico):**
   - *Si el silbido se escucha lejano, El Silbón está extremadamente cerca.*
   - *Si el silbido se escucha fuerte y claro, está lejos.*
   - La atenuación acústica 3D desafía la percepción auditiva del jugador en tiempo real.

2. **Linterna Direccional Volumétrica:**
   - La cabaña está sumergida en una densa oscuridad ambiental.
   - La linterna proyecta un cono de luz volumétrico suave orientado en la dirección de la mirada (`F` para encender/apagar).
   - La batería se desgasta continuamente con el uso. Encuentra pilas en muebles y cajones para recargarla.
   - La luz atrae al Silbón a gran distancia: si escuchas sus pasos pesados, ¡apaga la linterna!

3. **Sigilo y Escondites:**
   - Armarios, mesas de comedor y escritorios sirven como escondites físicos (`E` para entrar/salir).
   - Esconderse interrumpe la persecución del monstruo, siempre que la linterna esté apagada y no te haya visto entrar.
   - Atención: permanecer demasiado tiempo cerca de un monstruo alertado puede hacer que revise los muebles directamente.

4. **Objetos Arrojadizos Tácticos (Aturdimiento vs. Furia):**
   - Recoge piedras y herramientas para lanzarlas (`tecla Q`) como distracción o defensa desesperada.
   - **80% de probabilidad:** Aturde al Silbón entre 3.0 y 4.5 segundos, permitiendo huir.
   - **20% de probabilidad:** Desata su furia Berserk, aumentando radicalmente su velocidad de carrera.
   - Los proyectiles que impactan contra paredes o muebles generan ruidos acústicos que atraen al monstruo a investigar el área.

5. **Inventario Físico de 1 Solo Espacio (Estilo Granny):**
   - Capacidad física realista: Andreas solo puede llevar **1 herramienta activa** en la mano a la vez.
   - Suelta objetos en el suelo (`tecla G`) en cualquier momento para intercambiarlos o dejar llaves estratégicamente cerca de sus puertas. Los objetos soltados permanecen de forma persistente en el mundo.

6. **Minijuegos y Acertijos en Tiempo Real:**
   - **Desclavar Barricadas (Palanca):** Forcejeo de botones para arrancar tablones de puertas selladas.
   - **Gabinete Clásico (Ganzúa):** Simulación de ganzúa con ángulo de tensión y líneas de cizalla.
   - **Caja Fuerte Principal (Dial Acústico):** Cerradura rotativa que requiere escuchar los clics auditivos de los pernos internos.
   - **Caja de Fusibles (Cableado Eléctrico):** Reparación de terminales eléctricos para restaurar la luz de la cabaña.
   - **Teclado de Seguridad:** Acertijo de combinación de 4 dígitos con botones iluminados, pitidos táctiles y alarmas audibles.
   - *Tensión en tiempo real:* El Silbón continúa merodeando físicamente por la cabaña mientras resuelves los minijuegos.

7. **Director AI y Navegación A\* (Inspirado en Alien: Isolation):**
   - El **Director AI** evalúa la tensión, seguridad y ritmo de la partida, suministrando pistas sensoriales orgánicas al monstruo sin revelar coordenadas exactas.
   - El Silbón navega la arquitectura de la cabaña mediante **A\* Pathfinding**, esquivando muebles, bordes y cruzando puertas.

8. **Narrativa Ambiental:**
   - Notas de pergamino dejadas por el sobreviviente **José Gregorio** ofrecen pistas y fragmentos de historia, eliminando avisos invasivos de la interfaz.

9. **Soporte de Pantalla Completa y Escalado:**
   - Escalado entero por hardware (`pygame.SCALED | pygame.RESIZABLE`) preservando una resolución virtual nítida de 16:9 (512x288) en cualquier monitor.
   - Alternancia rápida a pantalla completa con `F11` o `Alt + Enter`.

---

### 🕹️ Controles

| Acción | Tecla Principal | Tecla Alternativa |
| :--- | :--- | :--- |
| **Moverse** | `W`, `A`, `S`, `D` | Flechas Direccionales (`↑`, `←`, `↓`, `→`) |
| **Correr (Sprint)** | `Shift Izquierdo` | `Shift Derecho` |
| **Interactuar / Abrir / Esconderse** | `E` | `Espacio` |
| **Encender / Apagar Linterna** | `F` | — |
| **Lanzar Objeto Equipado** | `Q` | `Espacio` (con arrojadizo) |
| **Soltar Objeto en Mano** | `G` | — |
| **Libreta de Objetivos** | `TAB` | — |
| **Menú de Pausa** | `P` | — |
| **Cambiar Idioma (ES / EN)** | `L` | — |
| **Pantalla Completa** | `F11` | `Alt` + `Enter` |
| **Cancelar / Salir / Cerrar Minijuego**| `ESC` | — |

---

### 🏗️ Arquitectura de Software y Patrones de Diseño

El proyecto cuenta con una arquitectura modular basada en estándares profesionales de desarrollo de videojuegos:

- **Pila de Estados Jerárquica (`gale.state.StateStack`):** Gestión de escenas y pantallas modales superpuestas (`WarningIntro`, `StartState`, `IntroRoadState`, `IntroForestState`, `PlayState`, `PauseState`, `ObjectiveState`, `NoteState`, `GameOverState`, `VictoryState`).
- **Máquinas de Estados Finitos (FSM):**
  - **Jugador:** `PlayerIdleState`, `PlayerWalkState`, `PlayerHidingState`.
  - **Monstruo (El Silbón):** `MonsterPatrolState`, `MonsterMovingToDoorState`, `MonsterKnockingState`, `MonsterInvestigateState`, `MonsterStalkingState`, `MonsterChaseState`, `MonsterBreathingState`, `MonsterCatchingState`, `MonsterBerserkState`, `MonsterStunnedState`.
- **Patrón Comando (`src/commands.py`):** Desacopla la captura de eventos de entrada de la ejecución de acciones en entidades.
- **Patrón Estrategia y Despachador (`src/definitions/interactions.py`):** Reemplaza extensas cadenas `if/elif` por tablas de despacho para objetos, puertas y muebles.
- **Patrón Fábrica (`src/minigames/MinigameFactory.py`):** Instanciación polimórfica y registro dinámico de minijuegos activos.
- **Definiciones Basadas en Datos (`src/definitions/`):** Centralización de habitaciones, enlaces de puertas, waypoints, items y animaciones.
- **Integración de Mapas Tiled (`src/world/TiledLevelLoader.py`):** Carga y parseo dinámico de mapas JSON multicapa, gestionando tilesets y obstáculos de colisión.
- **Sistema de Iluminación Volumétrica (`src/systems/LightingSystem.py`):** Máscara sustractiva con stencil combinando oscuridad ambiental, halo del jugador y cono direccional de linterna.
- **Gestor de Audio Espacial (`src/systems/AudioManager.py`):** 16 canales de sonido simultáneos con atenuación por distancia, escucha a través de puertas y modulación folclórica del silbido.

---

### 🚀 Instalación y Ejecución

1. **Clonar el Repositorio:**
   ```bash
   git clone https://github.com/fgrim4227/The-Whistle.git
   cd The-Whistle
   ```

2. **Crear y Activar Entorno Virtual:**
   ```bash
   # En Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # En Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Iniciar el Juego:**
   ```bash
   python main.py
   ```

*(Nota: En la sección de Releases del repositorio también se encuentran ejecutables empaquetados autónomos para Windows).*
