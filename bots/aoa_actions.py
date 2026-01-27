from time import sleep
import emulator_api

# Coordenadas dos botões — ajuste conforme sua resolução ou emulador
COORDS = {
    "first_search_button": (60, 540),  # exemplo: botão de busca no topo
    "giganto_search_button": (480, 480),  # exemplo: botão Giganto Mutant
    "reduce_search_level": (83, 642),
    "second_search_button": (1104, 646),
    "first_rally_button": (998, 549),
    "second_rally_button": (996, 500),
    "march_button": (1096, 660),
    "small_mutants": (800, 500)  # exemplo: botão Small Mutants
}

def click_search(device_id, adb_path):
    print("Clica no botão de busca.")
    x, y = COORDS["first_search_button"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_giganto(device_id, adb_path):
    print("Clica no botão Giganto.")
    x, y = COORDS["giganto_search_button"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_reduce_search_level(device_id, adb_path):
    print("Clica no botão para reduzir o nível de busca.")
    x, y = COORDS["reduce_search_level"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_second_search(device_id, adb_path):
    print("Clica no segundo botão de busca.")
    x, y = COORDS["second_search_button"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_small_mutants(device_id, adb_path):
    print("Clica no botão Small Mutants.")
    x, y = COORDS["small_mutants"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_first_rally(device_id, adb_path):
    print("Clica no primeiro botão de rally.")
    x, y = COORDS["first_rally_button"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_second_rally(device_id, adb_path):
    print("Clica no segundo botão de rally.")
    x, y = COORDS["second_rally_button"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_march(device_id, adb_path):
    print("Clica no botão de marcha.")
    x, y = COORDS["march_button"]
    emulator_api.tap(device_id, adb_path, x, y)

def click_help_gang(device_id, adb_path):
    print("Clica no botão de ajuda/gangue.")
    x, y = (980, 670)
    emulator_api.tap(device_id, adb_path, x, y)

def click_items_ap_recharge_use_button(device_id, adb_path):
    print("Clica no botão de usar item de recarga de action points.")
    x, y = (1008, 299)  # exemplo: coordenadas do botão de usar item AP
    emulator_api.tap(device_id, adb_path, x, y)

def click_items_ap_recharge_2x_button(device_id, adb_path):
    print("Clica no botão de usar 2x item de recarga de action points.")
    x, y = (808, 299)  # exemplo: coordenadas do botão de usar 2x item AP
    emulator_api.tap(device_id, adb_path, x, y)

# def click_items_fechar_button(device_id, adb_path):
#     print("Clica no botão de fechar itens.")
#     x, y = (114, 110)  # exemplo: coordenadas do botão de fechar
#     emulator_api.tap(device_id, adb_path, x, y)

# Função principal compatível com monitor.py
def kill_giganto(device_id, adb_path):
    """Executa uma sequência automatizada para atacar um Giganto."""
    click_search(device_id, adb_path)
    sleep(2)
    click_giganto(device_id, adb_path)
    sleep(1)
    for _ in range(4):
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
    # click_items_ap_recharge_2x_button(device_id, adb_path)
    # sleep(2)
    # click_items_fechar_button(device_id, adb_path)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    click_march(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)

def press_help_button(device_id, adb_path):
    """Clica no botão de ajuda/gangue."""
    # press_back(device_id, adb_path)
    sleep(2)
    click_help_gang(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    # esc não está funcionando no kvk. vou aproveitar o click no player info porque é na mesma posição do botão voltar da tela da gangue
    # ps: muito provavelmente vou ter que ajustar/remover isso quando acabar o kvk.
    # ps2: talvez criar um modo kvk para rodar nesse modo sem o esc.
    # click_player_info(device_id, adb_path)
    # sleep(2)
    # click_items_close_button(device_id, adb_path)

def press_map_city_button(device_id, adb_path):
    """Clica no botão de mapa/cidade."""
    x, y = (69, 652)  # exemplo: coordenadas do botão de mapa/cidade
    emulator_api.tap(device_id, adb_path, x, y)

def get_gang_gifts(device_id, adb_path):
    """Clica no botão de presentes da gangue."""
    click_help_gang(device_id, adb_path)
    sleep(2)
    click_gang_gifts_tab(device_id, adb_path)
    sleep(2)
    click_gang_gifts_claimall_button(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)
    sleep(2)
    emulator_api.press_back_esc(device_id, adb_path)

def click_gang_gifts_claimall_button(device_id, adb_path):
    x, y = (970, 650) # coordenadas botão "claim all" gifts
    emulator_api.tap(device_id, adb_path, x, y)

def click_gang_gifts_tab(device_id, adb_path):
    x, y = (135, 536) # coordenadas botão gifts da gangue
    emulator_api.tap(device_id, adb_path, x, y)

def click_player_info(device_id, adb_path):
    x, y = (55, 50)  # coordenadas do botão de informações do jogador
    emulator_api.tap(device_id, adb_path, x, y)

def click_add_action_points_button(device_id, adb_path):
    x, y = (808, 478)  # exemplo: coordenadas do botão de adicionar action points
    emulator_api.tap(device_id, adb_path, x, y)

def click_ap_max_limit_tip_confirm_button(device_id, adb_path):
    x, y = (761, 437)  # exemplo: coordenadas do botão de confirmar limite máximo de action points
    emulator_api.tap(device_id, adb_path, x, y)

def click_use_ap_bottles_button(device_id, adb_path):
    x, y = (1006, 298)  # exemplo: coordenadas do botão de usar action point bottles
    emulator_api.tap(device_id, adb_path, x, y)

def click_roger_menu(device_id, adb_path):
    x, y = (257, 619)  # Roger menu
    emulator_api.tap(device_id, adb_path, x, y)

def click_roger_military_tab(device_id, adb_path):
    x, y = (50, 347)  # Military tab
    emulator_api.tap(device_id, adb_path, x, y)

def click_roger_military_medical_station_claim_heal_button(device_id, adb_path):
    x, y = (627, 501)  # Medical station claim button
    emulator_api.tap(device_id, adb_path, x, y)

def click_medical_station_clear_button(device_id, adb_path):
    x, y = (1082, 173)  # Medical station clear button
    # x, y = (1182, 173)  # Medical station clear button
    emulator_api.tap(device_id, adb_path, x, y)

def click_medical_station_qty_input(device_id, adb_path):
    x, y = (1079, 257)  # Medical station quantity input
    emulator_api.tap(device_id, adb_path, x, y)

def click_medical_station_ok_button(device_id, adb_path):
    x, y = (1199, 667)  # Medical station OK button
    emulator_api.tap(device_id, adb_path, x, y)

def click_medical_station_heal_help_button(device_id, adb_path):
    x, y = (1000, 602)  # Medical station heal button
    emulator_api.tap(device_id, adb_path, x, y)

def click_city_food_button(device_id, adb_path):
    x, y = (701, 25)  # City food button
    emulator_api.tap(device_id, adb_path, x, y)

def click_items_auto_use_button(device_id, adb_path):
    x, y = (1000, 299)  # Auto use button
    emulator_api.tap(device_id, adb_path, x, y)

def click_items_iron_tab(device_id, adb_path):
    x, y = (89, 310)  # Iron tab
    emulator_api.tap(device_id, adb_path, x, y)

# Aparentemente o close button das "pop ups" está sempre na mesma posição, ou muito próxima.
# Talvez refatorar no futuro para unificar com outros closes. (items, medical pod, player info etc)
def click_items_close_button(device_id, adb_path):
    x, y = (1115, 102)  # Close button
    emulator_api.tap(device_id, adb_path, x, y)

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
