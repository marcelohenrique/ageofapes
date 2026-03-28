from time import sleep
import emulator_api

# New: toggle verbose debug output (tap/configure_display prints)
DEBUG = False

# Coordenadas dos botões — ajuste conforme sua resolução ou emulador
COORDS = {
    # "top_left_back_button": (21, 78),
    # "top_left_back_button": (15, 78), # working in s8+
    "top_left_back_button": (20, 80),

    "first_search_button": (60, 540),
    "small_mutants_search_button": (320, 480),
    "giganto_search_button": (480, 480),
    "giganto_search_button_coral_mine": (578, 480), # Na segunda às 13h (16h utc) foram abertas novas zonas e apareceu a opção coral mine entre as opções de busca, o que alterou a posição do botão de giganto.
    "giganto_search_button_coral_mine_berseker_fish": (640, 480), # Apareceu um novo botão no menu de busca para Berserker Fish, isso alterou a posição do botão de busca de giganto no kvk.
    "reduce_search_level": (83, 642),
    "second_search_button": (1104, 646),
    "attack_small_mutants_button": (995, 505),
    "first_rally_button": (1057, 550),
    "second_rally_button": (996, 500),
    
    "first_delegation_first_march": (878, 321),
    "first_delegation_second_march": (1034, 321),
    "second_delegation_first_march": (878, 504),
    "second_delegation_second_march": (1034, 504),
    
    "march_button": (1040, 660), # 1096 - valor antigo que estava na mesma posição do botão items. agora a posição do clique fica entre os botões gang e items.
    
    "preset_march_2": (1235, 267),
    
    "small_mutants": (800, 500),

    "troop_march_button": (953, 456),

    # Added mappings for other buttons previously hardcoded
    "help_gang": (980, 670),
    "items_ap_recharge_use": (1008, 299),
    "items_ap_recharge_2x": (808, 299),
    "map_city_button": (69, 652),
    "gang_gifts_claimall": (970, 650),
    "gang_gifts_tab": (135, 536),
    "player_info": (55, 50),
    "add_action_points": (808, 478),
    "ap_max_limit_confirm": (761, 437),
    "use_ap_bottles": (1006, 298),

    "roger_menu": (257, 619),
    "roger_military_tab": (50, 347),
    "roger_menu_daily_essentials_tab": (40, 586),
    "roger_menu_daily_essentials_tab_convoy_button": (626, 219),
    "roger_medical_claim": (542, 501),
    "medical_station_clear": (1015, 173),
    "medical_station_qty_input": (1020, 257),
    "medical_station_ok": (1199, 667),
    "medical_station_click_out_of_troops_qty": (575, 145),
    "medical_station_heal_help": (955, 602),
    "city_food_button": (701, 25),

    "items_auto_use_button": (1000, 299),
    "items_iron_tab": (89, 310),
    # "items_close": (1115, 102),
    "items_close": (1045, 105),
}

# === Display scaling configuration ===
# Base coordinates were captured on this reference device/resolution
BASE_WIDTH = 1280
BASE_HEIGHT = 720
BASE_DPI = 240

# Target values (defaults to base). Use configure_display() to change.
TARGET_WIDTH = BASE_WIDTH
TARGET_HEIGHT = BASE_HEIGHT
TARGET_DPI = BASE_DPI

# Per-device scaling storage. Keys are device_id strings.
# Each value is a dict: { 'scale_x', 'scale_y', 'dpi_scale', 'target_width', 'target_height', 'target_dpi' }
DEVICE_SCALES = {}

# Global default scale (used when no device_id is provided)
GLOBAL_SCALE = {
    'scale_x': 1.0,
    'scale_y': 1.0,
    'dpi_scale': 1.0,
    'target_width': TARGET_WIDTH,
    'target_height': TARGET_HEIGHT,
    'target_dpi': TARGET_DPI,
}


def configure_display(device_id: str = None, width: int = None, height: int = None, dpi: int = None):
    """Configura resolução/DPI alvo para escalonamento de coordenadas.

    Se device_id for fornecido, a escala será guardada para esse dispositivo.
    Caso contrário, atualiza a escala global usada por dispositivos não mapeados.

    Exemplo: configure_display(device_id='emulator-5554', width=1480, height=720, dpi=240)
    """
    global GLOBAL_SCALE, TARGET_WIDTH, TARGET_HEIGHT, TARGET_DPI

    # determine base targets
    target_w = GLOBAL_SCALE.get('target_width', TARGET_WIDTH)
    target_h = GLOBAL_SCALE.get('target_height', TARGET_HEIGHT)
    target_dpi = GLOBAL_SCALE.get('target_dpi', TARGET_DPI)

    if width:
        target_w = width
    if height:
        target_h = height
    if dpi:
        target_dpi = dpi

    scale_x = target_w / BASE_WIDTH if BASE_WIDTH else 1.0
    scale_y = target_h / BASE_HEIGHT if BASE_HEIGHT else 1.0
    dpi_scale = (target_dpi / BASE_DPI) if BASE_DPI and target_dpi else 1.0

    scale_entry = {
        'scale_x': scale_x,
        'scale_y': scale_y,
        'dpi_scale': dpi_scale,
        'target_width': target_w,
        'target_height': target_h,
        'target_dpi': target_dpi,
    }

    if device_id:
        DEVICE_SCALES[device_id] = scale_entry
        if DEBUG:
            print(f"[display] configured for device={device_id} target={target_w}x{target_h}@{target_dpi} scale_x={scale_x:.3f} scale_y={scale_y:.3f} dpi_scale={dpi_scale:.3f}")
    else:
        GLOBAL_SCALE = scale_entry
        if DEBUG:
            print(f"[display] configured global target={target_w}x{target_h}@{target_dpi} scale_x={scale_x:.3f} scale_y={scale_y:.3f} dpi_scale={dpi_scale:.3f}")


def _get_scales_for_device(device_id: str):
    """Retorna uma tupla (scale_x, scale_y, dpi_scale) para o device_id, usando GLOBAL_SCALE como fallback."""
    if device_id and device_id in DEVICE_SCALES:
        s = DEVICE_SCALES[device_id]
        return s['scale_x'], s['scale_y'], s['dpi_scale']
    s = GLOBAL_SCALE
    return s['scale_x'], s['scale_y'], s['dpi_scale']


def _scale_coords(device_id: str, x: int, y: int):
    """Retorna coordenadas escaladas como inteiros usando as escalas do dispositivo.

    Agora também realiza 'clamp' nas coordenadas usando o target_width/target_height
    conhecidos para evitar cliques fora da tela caso a escala esteja errada.
    """
    scale_x, scale_y, dpi_scale = _get_scales_for_device(device_id)

    # tenta obter largura/altura alvo do storage de escalas (fallback em GLOBAL_SCALE)
    if device_id and device_id in DEVICE_SCALES:
        target_w = DEVICE_SCALES[device_id].get('target_width')
        target_h = DEVICE_SCALES[device_id].get('target_height')
    else:
        target_w = GLOBAL_SCALE.get('target_width')
        target_h = GLOBAL_SCALE.get('target_height')

    if not target_w or not target_h:
        # fallback sensato
        target_w, target_h = BASE_WIDTH, BASE_HEIGHT

    # aplica escala
    sx = x * scale_x * dpi_scale
    sy = y * scale_y * dpi_scale

    # round
    sx_i = int(round(sx))
    sy_i = int(round(sy))

    # clamp (evita clicar fora da tela caso escala esteja errada)
    max_x = max(0, int(target_w) - 1)
    max_y = max(0, int(target_h) - 1)
    clamped = False
    if sx_i < 0:
        sx_i = 0
        clamped = True
    if sy_i < 0:
        sy_i = 0
        clamped = True
    if sx_i > max_x:
        sx_i = max_x
        clamped = True
    if sy_i > max_y:
        sy_i = max_y
        clamped = True

    if DEBUG:
        print(f"[scale] device={device_id} orig=({x},{y}) -> scaled=({sx_i},{sy_i}) using scale_x={scale_x:.3f} scale_y={scale_y:.3f} dpi_scale={dpi_scale:.3f} target={target_w}x{target_h} (clamped={clamped})")

    return sx_i, sy_i


# Monkeypatch emulator_api.tap so existing calls keep working but use scaled coords
_orig_tap = emulator_api.tap

def tap_scaled(device_id, adb_path, x, y):
    sx, sy = _scale_coords(device_id, x, y)
    # debug print
    if DEBUG:
        print(f"[tap_scaled] {x},{y} -> {sx},{sy} (device={device_id})")

    # safety: se o tap retornou coordenadas idênticas ao original, ainda assim
    # garantimos que estão dentro dos limites do dispositivo antes de enviar.
    try:
        # usa target width/height conhecido para checagem rápida
        if device_id and device_id in DEVICE_SCALES:
            tw = DEVICE_SCALES[device_id]['target_width']
            th = DEVICE_SCALES[device_id]['target_height']
        else:
            tw = GLOBAL_SCALE.get('target_width', BASE_WIDTH)
            th = GLOBAL_SCALE.get('target_height', BASE_HEIGHT)
        if sx < 0 or sx >= tw or sy < 0 or sy >= th:
            print(f"[WARN] Tap calculado fora dos limites ({sx},{sy}) para device {device_id} size={tw}x{th}. Clamped before sending.")
            sx = max(0, min(sx, int(tw) - 1))
            sy = max(0, min(sy, int(th) - 1))
    except Exception:
        # se algo falhar aqui, prossegue sem clamping adicional
        pass

    return _orig_tap(device_id, adb_path, sx, sy)

# apply monkeypatch
emulator_api.tap = tap_scaled

# Ensure emulator_api verbosity follows this module's DEBUG flag
emulator_api.VERBOSE = DEBUG

# By default keep base scaling; call configure_display(...) from your launcher when needed

def click_coord(device_id, adb_path, coord_key):
    """Clique em uma coordenada definida em COORDS usando a chave coord_key."""
    if coord_key not in COORDS:
        raise KeyError(f"Coord key '{coord_key}' not found in COORDS")
    print(f"Clicando em '{coord_key}'...")
    x, y = COORDS[coord_key]
    emulator_api.tap(device_id, adb_path, x, y)

# def click_items_fechar_button(device_id, adb_path):
#     print("Clica no botão de fechar itens.")
#     x, y = (114, 110)  # exemplo: coordenadas do botão de fechar
#     emulator_api.tap(device_id, adb_path, x, y)

def auto_use_rss(device_id, adb_path):
    """Usa recursos automaticamente quando estiverem baixos."""
    click_coord(device_id, adb_path, "city_food_button")
    sleep(2)
    click_coord(device_id, adb_path, "items_auto_use_button")
    sleep(2)
    click_coord(device_id, adb_path, "items_iron_tab")
    sleep(2)
    click_coord(device_id, adb_path, "items_auto_use_button")
    sleep(2)
    click_coord(device_id, adb_path, "items_close")


def heal_troops(troops_qty, device_id, adb_path, additional_time=0):
    """Cura tropas feridas usando apenas click_coord e send_text."""
    click_coord(device_id, adb_path, "roger_menu")
    sleep(1 + additional_time)
    click_coord(device_id, adb_path, "roger_military_tab")
    sleep(1 + additional_time)
    _medical_station_claim_button_coords = (565, 476, 684, 522)
    while True:
        template_raw  = emulator_api.capturar_retangulo(device['id'], *_medical_station_claim_button_coords)
        match_found, locations = emulator_api.match_template(template_raw, 'medical_station_claim_button.png')
        if match_found:
            break
        sleep(1 + additional_time)
    click_coord(device_id, adb_path, "roger_medical_claim")
    sleep(1 + additional_time)
    click_coord(device_id, adb_path, "roger_menu")
    sleep(1 + additional_time)
    click_coord(device_id, adb_path, "roger_military_tab")
    sleep(1 + additional_time)
    click_coord(device_id, adb_path, "roger_medical_claim")
    sleep(1 + additional_time)
    click_coord(device_id, adb_path, "medical_station_clear")
    sleep(1 + additional_time)
    click_coord(device_id, adb_path, "medical_station_qty_input")
    sleep(1 + additional_time)
    # Insere a quantidade de tropas a curar
    emulator_api.send_text(device_id, adb_path, str(troops_qty))
    sleep(1 + additional_time)
    # click_coord(device_id, adb_path, "medical_station_ok")
    click_coord(device_id, adb_path, "medical_station_click_out_of_troops_qty")
    sleep(1 + additional_time)
    for _ in range(2):
        click_coord(device_id, adb_path, "medical_station_heal_help")
        sleep(1 + additional_time)
    emulator_api.press_back_esc(device_id, adb_path)
    click_coord(device_id, adb_path, "items_close")
    sleep(1 + additional_time)
    press_top_left_back_button(device_id, adb_path)
    sleep(1 + additional_time)

    # Removendo as opções de help e rss automático para simplificar o processo.
    # press_help_button(device_id, adb_path)
    # sleep(2)
    # auto_use_rss(device_id, adb_path)
    # sleep(2)

# def use_action_points(device_id, adb_path):
#     """Usa todos os action points disponíveis."""
#     click_player_info(device_id, adb_path)
#     sleep(2)
#     click_add_action_points_button(device_id, adb_path)
#     sleep(2)
#     click_ap_max_limit_tip_confirm_button(device_id, adb_path)
#     sleep(2)
#     click_use_ap_bottles_button(device_id, adb_path)
#     sleep(2)
#     press_back_esc(device_id, adb_path)

# High-level actions simplified to use click_coord

def kill_giganto(device_id, adb_path, giganto_level=1, delegation=False, hasBus=False, selectedMarch=1, presetMarch=None, isKvk=False):
    """Executa sequência automatizada para atacar um Giganto usando apenas click_coord.
       Parametros:
       device_id: ID do dispositivo
       adb_path: Caminho do adb
       giganto_level: Nível do Giganto a ser atacado
       delegation: Se está usando tropas delegadas (o menu de seleção de tropas muda)
       hasBus: Se o jogador possui ônibus disponíveis (o menu de seleção de tropas muda)
       selectedMarch: Marcha selecionada para o ataque.
          1 - Seleciona a marcha principal simples (ps: incluir uma opção de selecionar preset marches futuramente)
          2 - Seleciona o ônibus
          3 - Seleciona a primeira marcha da primeira delegação
          4 - Seleciona a segunda marcha da primeira delegação
          5 - Seleciona a primeira marcha da segunda delegação
          6 - Seleciona a segunda marcha da segunda delegação
        
       """
    click_coord(device_id, adb_path, "first_search_button")
    sleep(2)
    # click_coord(device_id, adb_path, "giganto_search_button")
    # click_coord(device_id, adb_path, "giganto_search_button_coral_mine")
    click_coord(device_id, adb_path, "giganto_search_button_coral_mine_berseker_fish")
    sleep(1)
    for _ in range(5 - giganto_level):
        click_coord(device_id, adb_path, "reduce_search_level")
        sleep(1)
    click_coord(device_id, adb_path, "second_search_button")
    sleep(5)
    click_coord(device_id, adb_path, "first_rally_button")
    sleep(2)
    click_coord(device_id, adb_path, "second_rally_button")
    sleep(5)

    # delegation - select rally troop
    if delegation:
        if selectedMarch == 1:
            click_coord(device_id, adb_path, "march_button") # EDIT button
            sleep(2)
            if presetMarch:
                click_coord(device_id, adb_path, "preset_march_" + str(presetMarch)) # preset march
                sleep(2)
            click_coord(device_id, adb_path, "march_button")
            sleep(2)
            if not isKvk:
                for _ in range(3):
                    click_coord(device_id, adb_path, "items_ap_recharge_use")
                    sleep(2)
                emulator_api.press_back_esc(device_id, adb_path)
                sleep(2)
        elif selectedMarch == 3: # first delegation first march
            if hasBus:
                click_coord(device_id, adb_path, "second_delegation_first_march") # ônibus
                sleep(2)
            else:
                click_coord(device_id, adb_path, "first_delegation_first_march")
                sleep(2)
        elif selectedMarch == 4: # first delegation second march
            if hasBus:
                click_coord(device_id, adb_path, "second_delegation_second_march") # ônibus
                sleep(2)
            else:
                click_coord(device_id, adb_path, "first_delegation_second_march")
                sleep(2)
        elif selectedMarch == 5: # second delegation first march
            if hasBus:
                emulator_api.swipe(device_id, adb_path, 1228, 504, 1228, 175) # swipe para selecionar ônibus
                sleep(2)
            click_coord(device_id, adb_path, "second_delegation_first_march")
            sleep(2)
        elif selectedMarch == 6: # second delegation second march
            if hasBus:
                emulator_api.swipe(device_id, adb_path, 1228, 504, 1228, 175) # swipe para selecionar ônibus
                sleep(2)
            click_coord(device_id, adb_path, "second_delegation_second_march")
            sleep(2)

    click_coord(device_id, adb_path, "march_button")
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    go_to_outside_city_position(device_id, adb_path)

def go_to_outside_city_position(device_id, adb_path):
    """Clica no botão de mapa/cidade usando click_coord para ir para a posição fora da cidade."""
    click_coord(device_id, adb_path, "roger_menu")
    sleep(2)
    click_coord(device_id, adb_path, "roger_menu")
    sleep(2)
    click_coord(device_id, adb_path, "roger_menu_daily_essentials_tab")
    sleep(2)
    click_coord(device_id, adb_path, "roger_menu_daily_essentials_tab_convoy_button")
    sleep(3)
    click_coord(device_id, adb_path, "map_city_button")
    sleep(2)

def kill_small_mutants(device_id, adb_path):
    """Executa sequência automatizada para atacar mutantes usando apenas click_coord."""
    click_coord(device_id, adb_path, "first_search_button")
    sleep(2)
    click_coord(device_id, adb_path, "small_mutants_search_button")
    sleep(2)
    click_coord(device_id, adb_path, "second_search_button")
    sleep(3)
    click_coord(device_id, adb_path, "attack_small_mutants_button")
    sleep(2)
    click_coord(device_id, adb_path, "troop_march_button")
    sleep(2)

def press_help_button(device_id, adb_path):
    """Clica no botão de ajuda/gangue e volta, usando click_coord."""
    sleep(2)
    click_coord(device_id, adb_path, "help_gang")
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    press_top_left_back_button(device_id, adb_path)
    sleep(2)
    press_top_left_back_button(device_id, adb_path)

def get_gang_gifts(device_id, adb_path):
    """Clica no botão de presentes da gangue e dá claim all usando click_coord."""
    click_coord(device_id, adb_path, "help_gang")
    sleep(2)
    click_coord(device_id, adb_path, "gang_gifts_tab")
    sleep(2)
    click_coord(device_id, adb_path, "gang_gifts_claimall")
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)

def press_map_city_button(device_id, adb_path):
    """Clica no botão de mapa/cidade usando click_coord."""
    click_coord(device_id, adb_path, "map_city_button")
    sleep(2)

def press_top_left_back_button(device_id, adb_path):
    """Clica no botão de voltar no canto superior esquerdo usando click_coord."""
    click_coord(device_id, adb_path, "top_left_back_button")
    sleep(2)

if __name__ == "__main__":
    _target = "ldplayer"
    # _target = "bluestacks"
    # DEBUG = True
    # emulator_api.VERBOSE = True
    devices = emulator_api.list_devices(target=_target)
    if devices:
        while True:
        # for _ in range(1):
            for device in devices:
                print(f"Usando dispositivo {device['display_name']} ({device['id']}) [{device['type']}]")
                # kill_giganto(device["id"], device["adb_path"])
                # press_help_button(device["id"], device["adb_path"])
                # get_gang_gifts(device["id"], device["adb_path"])
                
                # heal_troops(1500, device["id"], device["adb_path"])
                # click_medical_station_clear_button(device["id"], device["adb_path"])
                # emulator_api.send_text(device["id"], device["adb_path"], str(7000))

                # press_top_left_back_button(device["id"], device["adb_path"])
                # click_coord(device["id"], device["adb_path"], "first_rally_button")
                # sleep(1)
                if device['id'] == '192.168.1.179:5555' or device['id'] == 'emulator-5568':
                # if not ( device['id'] == '192.168.1.179:5555' or device['id'] == 'emulator-5568' ):
                    print("Executando ações de cura para o smartphone...")
                    # Antes de clicar, configura a escala específica deste dispositivo
                    try:
                        width, height = emulator_api.get_screen_size(device['id'], device['adb_path'])
                        configure_display(device_id=device['id'], width=width, height=height)
                    except Exception as e:
                        print(f"[!] Não foi possível obter resolução/configurar escala para {device['id']}: {e}")

                    # Agora chama click_coord — o tap será escalado usando a escala do device_id
                    # click_coord(device['id'], device['adb_path'], "medical_station_clear")

                    heal_troops(1000, device['id'], device['adb_path'], additional_time=1)

                    # press_top_left_back_button(device['id'], device['adb_path'])

    else:
        print("Nenhum dispositivo conectado.")
