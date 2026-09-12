# El Silbón - 2D Top-Down Survival Horror

**Proyecto Final - Programación de Videojuegos (6to Semestre)**  
**Desarrolladores:** Francisco Grimaldo & Isaac Montes  
**Motor y Biblioteca:** Python, Pygame, Gale  

---

## 📖 Sinopsis e Historia

Mientras viajaba de noche por la solitaria carretera nacional, el vehículo de un paramédico fuera de servicio sufre una avería mecánica. Al divisar una tenue luz a lo lejos entre la espesura del bosque, se adentra buscando auxilio. Al acercarse a una cabaña aislada, el desgarrador grito de una mujer lo alerta; sin dudarlo, irrumpe para socorrerla, pero al cruzar el umbral recibe un golpe seco en la cabeza y cae inconsciente.

Al despertar en una habitación en penumbra, desorientado y con una linterna con batería precaria, descubre que no está solo: la cabaña es el dominio de **El Silbón**, el mítico espectro errante. Para sobrevivir, deberá explorar las habitaciones, resolver acertijos, desbloquear pasajes con herramientas, esconderse en las sombras y huir con vida.

---

## 🎮 Mecánicas Principales

1. **Paradoja del Silbido (Mito Folclórico):**
   * *Si el silbido se escucha lejano, El Silbón está extremadamente cerca.*
   * *Si el silbido se escucha fuerte y claro, está lejos.*
   * Esta mecánica guía o confunde la toma de decisiones del jugador en tiempo real.

2. **Linterna y Cono de Luz:**
   * La cabaña se encuentra sumergida en penumbra total.
   * La linterna proyecta un cono de luz en la dirección que mira el jugador (`F` para encender/apagar).
   * La batería se desgasta continuamente con el uso. Encuentra pilas en muebles y cajones para recargarla.
   * La luz atrae al Silbón a gran distancia: si escuchas sus pasos pesados, ¡apaga la linterna!

3. **Escondites de Sigilo:**
   * Esconderse en armarios y bajo mesas/escritorios interrumpe la persecución del monstruo, siempre que la linterna esté apagada y no te haya visto entrar.

4. **Lanzar Objetos (75% Stun / 25% Furia Berserk):**
   * Puedes recoger botellas, piedras o herramientas del entorno y arrojarlas.
   * **75% de probabilidad:** Aturde al Silbón de 2 a 5 segundos.
   * **25% de probabilidad:** Desata su furia, aumentando radicalmente su velocidad de carrera.

5. **Puzzles y Minijuegos en Tiempo Real:**
   * Forzar tablas con palanca (crowbar).
   * Descifrar combinación de caja fuerte girando el dial y escuchando los clics acústicos.
   * El Silbón continúa merodeando mientras interactúas, generando máxima tensión.

6. **Sistema Bilingüe (Español / English):**
   * Selector de idioma instantáneo en el menú principal (`ES` / `EN`).

---

## 🕹️ Controles

| Acción | Tecla / Control |
| :--- | :--- |
| **Moverse** | Teclas de Dirección / W, A, S, D |
| **Interactuar / Esconderse / Abrir** | Tecla `E` / Espacio |
| **Encender / Apagar Linterna** | Tecla `F` |
| **Lanzar Objeto en Mano** | Tecla `Q` o Espacio |
| **Ver Objetivos Actuales** | Tecla `TAB` |
| **Pausar / Opciones** | Tecla `P` / `ESC` |

---

## 🏗️ Arquitectura de Software

El proyecto sigue una arquitectura basada en **StateStack** sobre la biblioteca `Gale`:
* `ElSilbonGame`: Subclase de `gale.game.Game`.
* `StateStack`: Administra las escenas (`StartState`, `PlayState`, `MinigameState`, `PauseState`, `ObjectiveState`, `GameOverState`, `VictoryState`).
* `House` y `Room`: Carga y gestión modular de habitaciones desde archivos JSON exportados de **Tiled Map Editor** (32x32 px).
* `BaseEntity`: Jerarquía compartida para `Player`, `Monster` (El Silbón) y `NPC`.
* `LightingSystem`: Máscara alfa sobre superficie de Pygame para el cono de luz y penumbra.
* `AudioManager`: Modulación espacial del silbido y efectos sonoros diegéticos.

---

## 🚀 Requisitos e Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/el-silbon-survival.git
   cd el-silbon-survival
   ```
2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecutar el juego:
   ```bash
   python main.py
   ```
