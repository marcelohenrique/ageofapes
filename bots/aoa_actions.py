from time import sleep
import emulator_api

# Coordenadas dos botões — ajuste conforme sua resolução ou emulador
COORDS = {
    "first_search_button": (60, 540),
    "giganto_search_button": (480, 480),
    "reduce_search_level": (83, 642),
    "second_search_button": (1104, 646),
    "first_rally_button": (998, 549),
    "second_rally_button": (996, 500),
    "march_button": (1096, 660),
    "small_mutants": (800, 500),

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
    "roger_medical_claim": (627, 501),
    "medical_station_clear": (1082, 173),
    "medical_station_qty_input": (1079, 257),
    "medical_station_ok": (1199, 667),
    "medical_station_heal_help": (1000, 602),
    "city_food_button": (701, 25),
    "items_auto_use_button": (1000, 299),
    "items_iron_tab": (89, 310),
    "items_close": (1115, 102),
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

SCALE_X = 1.0
SCALE_Y = 1.0
DPI_SCALE = 1.0


def configure_display(width: int = None, height: int = None, dpi: int = None):
    """Configura resolução/DPI alvo para escalonamento de coordenadas.

    Exemplo: configure_display(width=1480, height=720, dpi=240)
    """
    global TARGET_WIDTH, TARGET_HEIGHT, TARGET_DPI, SCALE_X, SCALE_Y, DPI_SCALE
    if width:
        TARGET_WIDTH = width
    if height:
        TARGET_HEIGHT = height
    if dpi:
        TARGET_DPI = dpi

    SCALE_X = TARGET_WIDTH / BASE_WIDTH if BASE_WIDTH else 1.0
    SCALE_Y = TARGET_HEIGHT / BASE_HEIGHT if BASE_HEIGHT else 1.0
    DPI_SCALE = (TARGET_DPI / BASE_DPI) if BASE_DPI and TARGET_DPI else 1.0
    print(f"[display] configured target={TARGET_WIDTH}x{TARGET_HEIGHT}@{TARGET_DPI} scale_x={SCALE_X:.3f} scale_y={SCALE_Y:.3f} dpi_scale={DPI_SCALE:.3f}")


def _scale_coords(x: int, y: int):
    """Retorna coordenadas escaladas como inteiros."""
    sx = x * SCALE_X * DPI_SCALE
    sy = y * SCALE_Y * DPI_SCALE
    return int(round(sx)), int(round(sy))


# Monkeypatch emulator_api.tap so existing calls keep working but use scaled coords
_orig_tap = emulator_api.tap

def tap_scaled(device_id, adb_path, x, y):
    sx, sy = _scale_coords(x, y)
    # debug print
    print(f"[tap_scaled] {x},{y} -> {sx},{sy} (device={device_id})")
    return _orig_tap(device_id, adb_path, sx, sy)

# apply monkeypatch
emulator_api.tap = tap_scaled

# By default keep base scaling; call configure_display(...) from your launcher when needed

def click_coord(device_id, adb_path, coord_key):
    """Clique em uma coordenada definida em COORDS usando a chave coord_key."""
    if coord_key not in COORDS:
        raise KeyError(f"Coord key '{coord_key}' not found in COORDS")
    x, y = COORDS[coord_key]
    emulator_api.tap(device_id, adb_path, x, y)

def click_search(device_id, adb_path):
    print("Clica no botão de busca.")
    click_coord(device_id, adb_path, "first_search_button")

def click_giganto(device_id, adb_path):
    print("Clica no botão Giganto.")
    click_coord(device_id, adb_path, "giganto_search_button")

def click_reduce_search_level(device_id, adb_path):
    print("Clica no botão para reduzir o nível de busca.")
    click_coord(device_id, adb_path, "reduce_search_level")

def click_second_search(device_id, adb_path):
    print("Clica no segundo botão de busca.")
    click_coord(device_id, adb_path, "second_search_button")

def click_small_mutants(device_id, adb_path):
    print("Clica no botão Small Mutants.")
    click_coord(device_id, adb_path, "small_mutants")

def click_first_rally(device_id, adb_path):
    print("Clica no primeiro botão de rally.")
    click_coord(device_id, adb_path, "first_rally_button")

def click_second_rally(device_id, adb_path):
    print("Clica no segundo botão de rally.")
    click_coord(device_id, adb_path, "second_rally_button")

def click_march(device_id, adb_path):
    print("Clica no botão de marcha.")
    click_coord(device_id, adb_path, "march_button")

def click_help_gang(device_id, adb_path):
    print("Clica no botão de ajuda/gangue.")
    click_coord(device_id, adb_path, "help_gang")

def click_items_ap_recharge_use_button(device_id, adb_path):
    print("Clica no botão de usar item de recarga de action points.")
    click_coord(device_id, adb_path, "items_ap_recharge_use")

def click_items_ap_recharge_2x_button(device_id, adb_path):
    print("Clica no botão de usar 2x item de recarga de action points.")
    click_coord(device_id, adb_path, "items_ap_recharge_2x")

# def click_items_fechar_button(device_id, adb_path):
#     print("Clica no botão de fechar itens.")
#     x, y = (114, 110)  # exemplo: coordenadas do botão de fechar
#     emulator_api.tap(device_id, adb_path, x, y)

def press_map_city_button(device_id, adb_path):
    """Clica no botão de mapa/cidade."""
    click_coord(device_id, adb_path, "map_city_button")

# gang gifts

def click_gang_gifts_claimall_button(device_id, adb_path):
    click_coord(device_id, adb_path, "gang_gifts_claimall")

def click_gang_gifts_tab(device_id, adb_path):
    click_coord(device_id, adb_path, "gang_gifts_tab")

# player info
def click_player_info(device_id, adb_path):
    click_coord(device_id, adb_path, "player_info")

# action points
def click_add_action_points_button(device_id, adb_path):
    click_coord(device_id, adb_path, "add_action_points")

def click_ap_max_limit_tip_confirm_button(device_id, adb_path):
    click_coord(device_id, adb_path, "ap_max_limit_confirm")

def click_use_ap_bottles_button(device_id, adb_path):
    click_coord(device_id, adb_path, "use_ap_bottles")

# roger / medical
def click_roger_menu(device_id, adb_path):
    click_coord(device_id, adb_path, "roger_menu")

def click_roger_military_tab(device_id, adb_path):
    click_coord(device_id, adb_path, "roger_military_tab")

def click_roger_military_medical_station_claim_heal_button(device_id, adb_path):
    click_coord(device_id, adb_path, "roger_medical_claim")

def click_medical_station_clear_button(device_id, adb_path):
    click_coord(device_id, adb_path, "medical_station_clear")

def click_medical_station_qty_input(device_id, adb_path):
    click_coord(device_id, adb_path, "medical_station_qty_input")

def click_medical_station_ok_button(device_id, adb_path):
    click_coord(device_id, adb_path, "medical_station_ok")

def click_medical_station_heal_help_button(device_id, adb_path):
    click_coord(device_id, adb_path, "medical_station_heal_help")

def click_city_food_button(device_id, adb_path):
    click_coord(device_id, adb_path, "city_food_button")

def click_items_auto_use_button(device_id, adb_path):
    click_coord(device_id, adb_path, "items_auto_use_button")

def click_items_iron_tab(device_id, adb_path):
    click_coord(device_id, adb_path, "items_iron_tab")

# close
def click_items_close_button(device_id, adb_path):
    click_coord(device_id, adb_path, "items_close")

def auto_use_rss(device_id, adb_path):
    """Usa recursos automaticamente quando estiverem baixos."""
    click_city_food_button(device_id, adb_path)
    sleep(2)
    click_items_auto_use_button(device_id, adb_path)
    sleep(2)
    click_items_iron_tab(device_id, adb_path)
    sleep(2)
    click_items_auto_use_button(device_id, adb_path)
    sleep(2)
    # emulator_api.press_back_esc(device_id, adb_path)
    click_items_close_button(device_id, adb_path)

def heal_troops(troops_qty, device_id, adb_path, additional_time=0):
    """Cura tropas feridas."""
    for _ in range(2):
        click_roger_menu(device_id, adb_path)
        sleep(3)
        click_roger_military_tab(device_id, adb_path)
        sleep(3)
        click_roger_military_medical_station_claim_heal_button(device_id, adb_path)
        sleep(3)
    click_medical_station_clear_button(device_id, adb_path)
    sleep(3)
    click_medical_station_qty_input(device_id, adb_path)
    sleep(3)
    # Insere a quantidade de tropas a curar
    emulator_api.send_text(device_id, adb_path, str(troops_qty))
    sleep(3)
    click_medical_station_ok_button(device_id, adb_path)
    sleep(3)
    for _ in range(2):
        click_medical_station_heal_help_button(device_id, adb_path)
        sleep(3)
    emulator_api.press_back_esc(device_id, adb_path)
    # click_items_close_button(device_id, adb_path)
    # Esse tempo deve ser configurado com tempo suficiente para a cura completar pois a tela fecha automaticamente
    sleep(7+additional_time)

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

# Ensure important high-level actions remain available
def kill_giganto(device_id, adb_path, giganto_level=1):
    """Executa uma sequência automatizada para atacar um Giganto."""
    click_search(device_id, adb_path)
    sleep(2)
    click_giganto(device_id, adb_path)
    sleep(1)
    for _ in range(5 - giganto_level):
        click_reduce_search_level(device_id, adb_path)
        sleep(1)
    click_second_search(device_id, adb_path)
    sleep(5)
    click_first_rally(device_id, adb_path)
    sleep(2)
    click_second_rally(device_id, adb_path)
    sleep(5)
    click_march(device_id, adb_path)
    sleep(2)
    for _ in range(3):
        click_items_ap_recharge_use_button(device_id, adb_path)
        sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    click_march(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)


def press_help_button(device_id, adb_path):
    """Clica no botão de ajuda/gangue e volta."""
    sleep(2)
    click_help_gang(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)


def get_gang_gifts(device_id, adb_path):
    """Clica no botão de presentes da gangue e dá claim all."""
    click_help_gang(device_id, adb_path)
    sleep(2)
    click_gang_gifts_tab(device_id, adb_path)
    sleep(2)
    click_gang_gifts_claimall_button(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)

if __name__ == "__main__":
    devices = emulator_api.list_devices(target='ldplayer')
    if devices:
        while True:
            for device in devices:
                print(f"Usando dispositivo {device['display_name']} ({device['id']}) [{device['type']}]")
                # kill_giganto(device["id"], device["adb_path"])
                # press_help_button(device["id"], device["adb_path"])
                # get_gang_gifts(device["id"], device["adb_path"])
                
                heal_troops(7000, device["id"], device["adb_path"])
                # click_medical_station_clear_button(device["id"], device["adb_path"])
                # emulator_api.send_text(device["id"], device["adb_path"], str(7000))
    else:
        print("Nenhum dispositivo conectado.")
