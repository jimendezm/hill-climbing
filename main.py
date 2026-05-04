import pygame
import sys
import copy
import time
import random
import math

import hc
import utils

# ── Palette ────────────────────────────────────────────────────────────────────
BG            = (15,  15,  20)
GRID_LINE     = (35,  35,  45)
CELL_EMPTY    = (22,  22,  30)
CELL_HOVER    = (35,  40,  55)
CELL_HL       = (30,  80, 160)
CELL_CAND     = (90,  65,  10)
CELL_BEST     = (20,  90,  50)
CELL_SA       = (80,  30, 120)
TEXT_MAIN     = (220, 220, 230)
TEXT_DIM      = (110, 110, 130)
TEXT_INFO     = ( 90, 160, 255)
TEXT_WARN     = (255, 190,  50)
TEXT_OK       = ( 60, 200, 110)
TEXT_SA       = (190, 100, 255)
ACCENT        = ( 80, 130, 255)
ACCENT_SA     = (160,  60, 220)
BTN_IDLE      = (30,  32,  45)
BTN_HOVER     = (45,  50,  70)
BTN_ACTIVE    = (60,  90, 180)
BTN_ACTIVE_SA = (100, 40, 180)
BTN_BORDER    = (60,  65,  90)
PANEL_BG      = (18,  18,  26)

# ── Grid config ────────────────────────────────────────────────────────────────
ROWS   = 5
COLS   = 10
CELL   = 64
PAD    = 20
GRID_X = PAD
GRID_Y = 110
GRID_W = COLS * CELL
GRID_H = ROWS * CELL
WIN_W  = GRID_W + PAD * 2
WIN_H  = GRID_Y + GRID_H + 280

# ── Initial map ────────────────────────────────────────────────────────────────
INITIAL_MAP = [
    [None, None, None, None, utils.OBJECT_HOSPITAL, None, None, None, utils.OBJECT_HOUSE, None],
    [None, None, utils.OBJECT_HOUSE, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None],
    [None, utils.OBJECT_HOUSE, None, None, None, None, None, None, None, utils.OBJECT_HOSPITAL],
    [None, None, None, None, None, None, utils.OBJECT_HOUSE, None, None, None],
]

# SA params
SA_T_MIN     = 0.1
SA_T_INITIAL = 10.0
SA_COOLING   = 0.95

# ── HC step generator ──────────────────────────────────────────────────────────
def hc_step_generator(initial_map):
    current_map  = copy.deepcopy(initial_map)
    current_cost = utils.cost(current_map)
    it = 0

    while True:
        it += 1
        best_map  = current_map
        best_cost = current_cost
        best_from = best_to = None

        for hospital in utils.find_objects(current_map, utils.OBJECT_HOSPITAL):
            for candidate_move in utils.actions(current_map, hospital):
                candidate_map  = utils.result(current_map, hospital, candidate_move)
                candidate_cost = utils.cost(candidate_map)

                yield {
                    "type":      "candidate",
                    "from":      hospital,
                    "to":        candidate_move,
                    "map":       current_map,
                    "iter":      it,
                    "cand_cost": candidate_cost,
                    "cur_cost":  current_cost,
                }

                if candidate_cost < best_cost:
                    best_cost = candidate_cost
                    best_map  = candidate_map
                    best_from = hospital
                    best_to   = candidate_move

        if best_cost < current_cost:
            current_map  = best_map
            current_cost = best_cost
            yield {
                "type": "move",
                "from": best_from,
                "to":   best_to,
                "map":  current_map,
                "iter": it,
                "cost": current_cost,
            }
        else:
            yield {"type": "done", "map": current_map, "iter": it, "cost": current_cost}
            return

# ── SA step generator ──────────────────────────────────────────────────────────
def sa_step_generator(initial_map, T_initial, T_min, cooling_rate):
    current_map  = copy.deepcopy(initial_map)
    current_cost = utils.cost(current_map)
    temperature  = T_initial
    it = 0

    while temperature > T_min:
        it += 1
        movable = utils.find_objects(current_map, utils.OBJECT_HOSPITAL)
        if not movable:
            break

        hospital = random.choice(movable)
        possible = utils.actions(current_map, hospital)
        if not possible:
            break

        move          = random.choice(possible)
        neighbor_map  = utils.result(current_map, hospital, move)
        neighbor_cost = utils.cost(neighbor_map)
        delta         = neighbor_cost - current_cost

        if delta < 0:
            accepted = True
            prob     = 1.0
        else:
            prob     = math.exp(-delta / temperature)
            accepted = random.random() < prob

        yield {
            "type":        "sa_candidate",
            "from":        hospital,
            "to":          move,
            "map":         current_map,
            "iter":        it,
            "cand_cost":   neighbor_cost,
            "cur_cost":    current_cost,
            "temperature": temperature,
            "delta":       delta,
            "prob":        prob,
            "accepted":    accepted,
        }

        if accepted:
            current_map  = neighbor_map
            current_cost = neighbor_cost
            yield {
                "type":        "sa_move",
                "from":        hospital,
                "to":          move,
                "map":         current_map,
                "iter":        it,
                "cost":        current_cost,
                "temperature": temperature,
                "delta":       delta,
                "prob":        prob,
            }

        temperature *= cooling_rate

    yield {"type": "done", "map": current_map, "iter": it, "cost": current_cost}

# ── Helpers ────────────────────────────────────────────────────────────────────
def random_map():
    m = [[None] * COLS for _ in range(ROWS)]
    cells = [(c, r) for r in range(ROWS) for c in range(COLS)]
    random.shuffle(cells)
    for c, r in cells[:4]:  m[r][c] = utils.OBJECT_HOUSE
    for c, r in cells[4:6]: m[r][c] = utils.OBJECT_HOSPITAL
    return m

def draw_rounded_rect(surf, color, rect, r=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)

def draw_hospital(surf, cx, cy, size=28):
    r = size // 2
    s = max(6, size // 4)
    pygame.draw.rect(surf, (200, 60, 60), (cx - r, cy - r, size, size), border_radius=5)
    pygame.draw.rect(surf, (255, 255, 255), (cx - s // 2, cy - r + 4, s, size - 8))
    pygame.draw.rect(surf, (255, 255, 255), (cx - r + 4, cy - s // 2, size - 8, s))

def draw_house(surf, cx, cy, size=26):
    half = size // 2
    pts  = [(cx, cy - half), (cx - half, cy), (cx + half, cy)]
    pygame.draw.polygon(surf, (200, 160, 60), pts)
    pygame.draw.rect(surf, (220, 180, 80), (cx - half + 3, cy, size - 6, half))
    dw, dh = max(4, size // 5), max(5, size // 4)
    pygame.draw.rect(surf, (140, 100, 40), (cx - dw // 2, cy + half - dh, dw, dh))

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()

    font_lg = pygame.font.SysFont("monospace", 20, bold=True)
    font_md = pygame.font.SysFont("monospace", 14)
    font_sm = pygame.font.SysFont("monospace", 12)
    font_xl = pygame.font.SysFont("monospace", 22, bold=True)

    # ── State ──────────────────────────────────────────────────────────────────
    map_state   = copy.deepcopy(INITIAL_MAP)
    gen         = None
    running     = False
    done        = False
    mode        = ["hc"]     # mutable list so closures can write
    iters       = [0]
    cur_cost    = [utils.cost(map_state)]
    best_cost   = [cur_cost[0]]
    temperature = [SA_T_INITIAL]
    last_prob   = [None]
    last_delta  = [None]
    highlights  = []
    candidates  = []
    best_cells  = []
    sel_hosp    = [None]
    log_lines   = []
    speed_ms    = [120]
    last_step   = [0]
    slider_val  = [0.5]
    dragging    = [False]

    BH = 32
    MODE_Y = 12
    ACT_Y  = 54

    btns_mode = [
        {"rect": pygame.Rect(PAD,       MODE_Y, 135, BH), "label": "Hill Climbing",     "id": "hc"},
        {"rect": pygame.Rect(PAD + 148, MODE_Y, 165, BH), "label": "Simul. Annealing",  "id": "sa"},
    ]
    btns_act = [
        {"rect": pygame.Rect(PAD,       ACT_Y, 100, BH), "label": "▶ Correr",    "id": "run"},
        {"rect": pygame.Rect(PAD + 112, ACT_Y, 100, BH), "label": "  Paso",      "id": "step"},
        {"rect": pygame.Rect(PAD + 224, ACT_Y, 100, BH), "label": "  Reset",     "id": "reset"},
        {"rect": pygame.Rect(PAD + 336, ACT_Y, 110, BH), "label": "  Aleatorio", "id": "rand"},
    ]
    slider_rect = pygame.Rect(PAD + 464, ACT_Y + 7, 140, 18)

    def slider_to_ms(v):
        return int(600 - v * 580)

    def add_log(msg, color=TEXT_DIM):
        log_lines.append((msg, color))
        if len(log_lines) > 6:
            log_lines.pop(0)

    def full_reset(new_map):
        nonlocal map_state, gen, running, done, highlights, candidates, best_cells
        map_state       = new_map
        gen             = None
        running         = False
        done            = False
        iters[0]        = 0
        cur_cost[0]     = utils.cost(map_state)
        best_cost[0]    = cur_cost[0]
        temperature[0]  = SA_T_INITIAL
        last_prob[0]    = None
        last_delta[0]   = None
        highlights       = []
        candidates       = []
        best_cells       = []
        sel_hosp[0]     = None

    def start_run():
        nonlocal gen, running, done
        if done:
            return
        if mode[0] == "hc":
            gen = hc_step_generator(copy.deepcopy(map_state))
            add_log("Iniciando Hill Climbing...", TEXT_INFO)
        else:
            gen = sa_step_generator(copy.deepcopy(map_state),
                                    SA_T_INITIAL, SA_T_MIN, SA_COOLING)
            add_log(f"Iniciando SA  T0={SA_T_INITIAL}  enfr={SA_COOLING}", TEXT_SA)
        running = True

    def do_next_step():
        nonlocal map_state, gen, running, done, highlights, candidates, best_cells
        if gen is None:
            start_run()
            return
        try:
            step = next(gen)
        except StopIteration:
            running = False
            done    = True
            add_log("Generador agotado.", TEXT_DIM)
            return

        t = step["type"]

        if t == "candidate":
            candidates[:] = [step["to"]]
            highlights[:] = [step["from"]]
            best_cells[:] = []

        elif t == "move":
            map_state     = step["map"]
            iters[0]      = step["iter"]
            cur_cost[0]   = step["cost"]
            best_cost[0]  = min(best_cost[0], cur_cost[0])
            highlights[:] = [step["to"]]
            candidates[:] = []
            best_cells[:] = [step["to"]]
            add_log(
                f"HC iter {iters[0]}: ({step['from'][0]},{step['from'][1]})->"
                f"({step['to'][0]},{step['to'][1]}) cost={cur_cost[0]}",
                TEXT_OK,
            )

        elif t == "sa_candidate":
            candidates[:]  = [step["to"]]
            highlights[:]  = [step["from"]]
            best_cells[:]  = []
            temperature[0] = step["temperature"]
            last_prob[0]   = step["prob"]
            last_delta[0]  = step["delta"]

        elif t == "sa_move":
            map_state      = step["map"]
            iters[0]       = step["iter"]
            cur_cost[0]    = step["cost"]
            best_cost[0]   = min(best_cost[0], cur_cost[0])
            temperature[0] = step["temperature"]
            last_prob[0]   = step["prob"]
            last_delta[0]  = step["delta"]
            highlights[:]  = [step["to"]]
            candidates[:]  = []
            best_cells[:]  = [step["to"]]
            sign = "↓" if step["delta"] < 0 else "↑"
            add_log(
                f"SA {iters[0]}: {sign}Δ={step['delta']:+.1f} "
                f"p={step['prob']:.2f} T={step['temperature']:.3f} c={cur_cost[0]}",
                TEXT_SA,
            )

        elif t == "done":
            map_state     = step["map"]
            iters[0]      = step["iter"]
            cur_cost[0]   = step["cost"]
            best_cost[0]  = min(best_cost[0], cur_cost[0])
            highlights[:] = []
            candidates[:] = []
            best_cells[:] = []
            running       = False
            done          = True
            algo = "HC" if mode[0] == "hc" else "SA"
            add_log(f"✓ {algo} terminó. Costo final={cur_cost[0]}", TEXT_OK)

    add_log("Elige modo (HC / SA), luego ▶ Correr o N=paso.", TEXT_DIM)

    # ── Event loop ─────────────────────────────────────────────────────────────
    while True:
        now = time.time() * 1000
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE: start_run()
                if ev.key == pygame.K_n:     do_next_step()
                if ev.key == pygame.K_r:
                    full_reset(copy.deepcopy(INITIAL_MAP))
                    log_lines.clear(); add_log("Mapa reiniciado.", TEXT_DIM)
                if ev.key == pygame.K_g:
                    full_reset(random_map())
                    log_lines.clear(); add_log("Mapa aleatorio generado.", TEXT_INFO)

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if slider_rect.collidepoint(mx, my):
                    dragging[0] = True

                for btn in btns_mode:
                    if btn["rect"].collidepoint(mx, my) and btn["id"] != mode[0]:
                        mode[0] = btn["id"]
                        gen     = None
                        running = False
                        done    = False
                        highlights[:] = []; candidates[:] = []; best_cells[:] = []
                        add_log(
                            f"Modo: {'Hill Climbing' if mode[0]=='hc' else 'Simulated Annealing'}",
                            TEXT_INFO if mode[0] == "hc" else TEXT_SA,
                        )

                for btn in btns_act:
                    if btn["rect"].collidepoint(mx, my):
                        if btn["id"] == "run":   start_run()
                        if btn["id"] == "step":  do_next_step()
                        if btn["id"] == "reset":
                            full_reset(copy.deepcopy(INITIAL_MAP))
                            log_lines.clear(); add_log("Mapa reiniciado.", TEXT_DIM)
                        if btn["id"] == "rand":
                            full_reset(random_map())
                            log_lines.clear(); add_log("Mapa aleatorio generado.", TEXT_INFO)

                # Clic en grilla
                gx = (mx - GRID_X) // CELL
                gy = (my - GRID_Y) // CELL
                if 0 <= gx < COLS and 0 <= gy < ROWS and not running:
                    cell = map_state[gy][gx]
                    if cell == utils.OBJECT_HOSPITAL:
                        sel_hosp[0]   = (gx, gy)
                        highlights[:] = [(gx, gy)]
                        candidates[:] = utils.actions(map_state, (gx, gy))
                        best_cells[:] = []
                    elif sel_hosp[0] and (gx, gy) in utils.actions(map_state, sel_hosp[0]):
                        map_state     = utils.result(map_state, sel_hosp[0], (gx, gy))
                        cur_cost[0]   = utils.cost(map_state)
                        best_cost[0]  = min(best_cost[0], cur_cost[0])
                        sel_hosp[0]   = None
                        highlights[:] = [(gx, gy)]; candidates[:] = []; best_cells[:] = []
                        add_log(f"Manual->({gx},{gy}). Costo={cur_cost[0]}", TEXT_WARN)
                    else:
                        sel_hosp[0] = None
                        highlights[:] = []; candidates[:] = []; best_cells[:] = []

            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                dragging[0] = False

            if ev.type == pygame.MOUSEMOTION and dragging[0]:
                rel           = (mx - slider_rect.x) / slider_rect.width
                slider_val[0] = max(0.0, min(1.0, rel))
                speed_ms[0]   = slider_to_ms(slider_val[0])

        if running and now - last_step[0] >= speed_ms[0]:
            do_next_step()
            last_step[0] = now

        # ── Draw ───────────────────────────────────────────────────────────────
        screen.fill(BG)

        # Title
        is_sa      = mode[0] == "sa"
        title_col  = TEXT_SA if is_sa else TEXT_MAIN
        algo_lbl   = "Simulated Annealing" if is_sa else "Hill Climbing"
        title = font_xl.render(f"{algo_lbl}  —  Hospitales", True, title_col)
        screen.blit(title, (PAD, GRID_Y - 86))

        # Mode toggle buttons
        for btn in btns_mode:
            active = btn["id"] == mode[0]
            hover  = btn["rect"].collidepoint(mx, my)
            col    = (BTN_ACTIVE_SA if is_sa else BTN_ACTIVE) if active else (BTN_HOVER if hover else BTN_IDLE)
            bc     = (ACCENT_SA if is_sa else ACCENT) if active else BTN_BORDER
            draw_rounded_rect(screen, col, btn["rect"], r=6, border=2 if active else 1, border_color=bc)
            lc = TEXT_SA if (active and is_sa) else TEXT_MAIN
            lbl = font_md.render(btn["label"], True, lc)
            screen.blit(lbl, lbl.get_rect(center=btn["rect"].center))

        # Action buttons
        for btn in btns_act:
            hover  = btn["rect"].collidepoint(mx, my)
            active = btn["id"] == "run" and running
            col    = (BTN_ACTIVE_SA if is_sa else BTN_ACTIVE) if active else (BTN_HOVER if hover else BTN_IDLE)
            draw_rounded_rect(screen, col, btn["rect"], r=6, border=1, border_color=BTN_BORDER)
            lbl = font_md.render(btn["label"], True, TEXT_MAIN)
            screen.blit(lbl, lbl.get_rect(center=btn["rect"].center))

        # Slider
        screen.blit(font_sm.render("velocidad", True, TEXT_DIM), (slider_rect.x, slider_rect.y - 14))
        pygame.draw.rect(screen, GRID_LINE, slider_rect, border_radius=4)
        fw = int(slider_val[0] * slider_rect.width)
        pygame.draw.rect(screen, ACCENT_SA if is_sa else ACCENT,
                         (slider_rect.x, slider_rect.y, fw, slider_rect.height), border_radius=4)
        pygame.draw.circle(screen, TEXT_MAIN, (slider_rect.x + fw, slider_rect.centery), 8)

        # Grid cells
        for r in range(ROWS):
            for c in range(COLS):
                px = GRID_X + c * CELL
                py = GRID_Y + r * CELL
                rect = pygame.Rect(px + 1, py + 1, CELL - 2, CELL - 2)
                if (c, r) in best_cells:     col = CELL_BEST
                elif (c, r) in candidates:   col = CELL_SA if is_sa else CELL_CAND
                elif (c, r) in highlights:   col = CELL_HL
                elif rect.collidepoint(mx, my) and not running: col = CELL_HOVER
                else:                        col = CELL_EMPTY
                draw_rounded_rect(screen, col, rect, r=5)
                obj = map_state[r][c]
                if obj == utils.OBJECT_HOSPITAL:
                    draw_hospital(screen, px + CELL // 2, py + CELL // 2, 30)
                elif obj == utils.OBJECT_HOUSE:
                    draw_house(screen, px + CELL // 2, py + CELL // 2, 28)
                screen.blit(font_sm.render(f"{c},{r}", True, (50, 52, 70)), (px + 4, py + CELL - 16))

        # Grid lines
        for c in range(COLS + 1):
            pygame.draw.line(screen, GRID_LINE,
                             (GRID_X + c * CELL, GRID_Y), (GRID_X + c * CELL, GRID_Y + GRID_H))
        for r in range(ROWS + 1):
            pygame.draw.line(screen, GRID_LINE,
                             (GRID_X, GRID_Y + r * CELL), (GRID_X + GRID_W, GRID_Y + r * CELL))

        # Manhattan lines
        for (hpx, hpy) in utils.find_objects(map_state, utils.OBJECT_HOSPITAL):
            cx1 = GRID_X + hpx * CELL + CELL // 2
            cy1 = GRID_Y + hpy * CELL + CELL // 2
            for (hx2, hy2) in utils.find_objects(map_state, utils.OBJECT_HOUSE):
                pygame.draw.line(screen, (50, 80, 120),
                                 (cx1, cy1),
                                 (GRID_X + hx2 * CELL + CELL // 2, GRID_Y + hy2 * CELL + CELL // 2), 1)

        # Stats panel
        panel_y = GRID_Y + GRID_H + 14
        draw_rounded_rect(screen, PANEL_BG,
                          pygame.Rect(PAD, panel_y, WIN_W - PAD * 2, 80),
                          r=8, border=1, border_color=GRID_LINE)

        stats = [
            ("Costo actual", str(cur_cost[0]),  TEXT_WARN if cur_cost[0] > best_cost[0] else TEXT_OK),
            ("Mejor costo",  str(best_cost[0]), TEXT_OK),
            ("Iteraciones",  str(iters[0]),     TEXT_INFO),
        ]
        if is_sa:
            stats.append(("Temperatura",
                          f"{temperature[0]:.3f}", TEXT_SA))
            stats.append(("P. aceptar",
                          f"{last_prob[0]:.2f}" if last_prob[0] is not None else "-",
                          TEXT_SA))
        else:
            stats.append(("Estado",
                          "corriendo" if running else ("listo!" if done else "espera"),
                          TEXT_OK if done else (TEXT_WARN if running else TEXT_DIM)))

        col_w = (WIN_W - PAD * 2) // len(stats)
        for i, (lbl, val, vcol) in enumerate(stats):
            sx = PAD + i * col_w + 14
            screen.blit(font_sm.render(lbl, True, TEXT_DIM), (sx, panel_y + 12))
            screen.blit(font_lg.render(val, True, vcol),     (sx, panel_y + 32))

        # Log panel
        log_y = panel_y + 96
        draw_rounded_rect(screen, PANEL_BG,
                          pygame.Rect(PAD, log_y, WIN_W - PAD * 2, 100),
                          r=8, border=1, border_color=GRID_LINE)
        screen.blit(font_sm.render("log", True, TEXT_DIM), (PAD + 10, log_y + 6))
        for i, (msg, col) in enumerate(log_lines[-5:]):
            screen.blit(font_sm.render(msg, True, col), (PAD + 10, log_y + 22 + i * 15))

        # Legend
        legend_y = log_y + 108
        items = [
            (CELL_HL,                                    "hospital sel."),
            (CELL_SA if is_sa else CELL_CAND,            "candidato SA" if is_sa else "candidato"),
            (CELL_BEST,                                  "movimiento aceptado"),
        ]
        lx = PAD
        for bg, txt in items:
            pygame.draw.rect(screen, bg, (lx, legend_y, 14, 14), border_radius=3)
            l = font_sm.render(txt, True, TEXT_DIM)
            screen.blit(l, (lx + 18, legend_y))
            lx += 18 + l.get_width() + 20

        screen.blit(
            font_sm.render("ESPACIO: correr   N: paso   R: reset   G: aleatorio",
                           True, (45, 48, 65)),
            (PAD, legend_y + 22),
        )

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()