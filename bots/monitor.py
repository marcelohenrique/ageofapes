import time
import sys
import game_launcher
import emulator_api
import aoa_actions

SCAN_INTERVAL = 5 # 5*60  # segundos entre varreduras do ADB
ACTION_DELAY = 2   # segundos entre ações nos dispositivos

# New: enable verbose/debug output (shows low-level ADB click logs)
DEBUG = False

WHITELIST_IDS = { # Preencha com os deviceids que quer isolar
    ''
    # , 'emulator-5560' # FarmerApe05
    # , 'emulator-5558' # FarmerApe08
    # , ''
    # bluestacks
    # , 'emulator-5554' # minion01
    # , 'emulator-5564' # minion02
}

# Dispositivos podem ter modos diferentes — mapeie aqui por device id (adb id)
# Suporte de modos: 'farm' (mata giganto), 'heal' (cura tropas), 'help_only' (aperta ajuda), 'idle'
DEVICE_MODES = {
    # Exemplos:
    # 'emulator-5554': 'farm',
    # 'emulator-5564': 'heal',
    '192.168.1.179:5555': 'heal' # meu smartphone
    , 'emulator-5568': 'heal' # meu smartphone em LDPlayer
}
DEFAULT_DEVICE_MODE = 'farm'  # modo padrão para dispositivos não mapeados

DONT_KILL_GIGANTO_ID_LIST = {
    ''
    # , 'emulator-5554'  # FarmerApe04
    # , 'emulator-5554'  # FarmerApe05
    # , 'emulator-5554'  # FarmerApe06
    # , 'emulator-5554'  # FarmerApe07
    # , 'emulator-5554'  # FarmerApe08
    # bluestacks
    # , 'emulator-5554' # minion01
    # , 'emulator-5564' # minion02
    # , '127.0.0.1:5556' # minion03
}

KILL_GIGANTO = False

active_devices = {}

def handle_new_device(device):
    print(f"[+] Novo dispositivo detectado: {device['display_name']} ({device['id']}) [{device['type']}]")
    active_devices[device['id']] = device
    # Tenta obter resolução do dispositivo e configurar escala específica para ele
    try:
        width, height = emulator_api.get_screen_size(device['id'], device['adb_path'])
        aoa_actions.configure_display(device_id=device['id'], width=width, height=height)
    except Exception as e:
        print(f"[!] Não foi possível configurar a escala para {device['display_name']} ({device['id']}): {e}")

def handle_disconnect(device_id):
    device = active_devices.pop(device_id, None)
    if device:
        print(f"[-] Dispositivo desconectado: {device['display_name']} ({device_id}) [{device['type']}]")

def get_device_mode(device):
    """Retorna o modo para o dispositivo (por id)."""
    return DEVICE_MODES.get(device.get('id'), DEFAULT_DEVICE_MODE)

def perform_actions(device, loop_iter=0):
    """Despacha ações diferentes dependendo do modo do dispositivo.
       Recebe loop_iter para fins de log.
    """
    adb_path = device["adb_path"]
    display_name = device["display_name"]
    device_id = device["id"]

    # Constants used to select the march
    giganto_level = 5  # Nível do Giganto a ser eliminado
    delegation = True  # Usar delegação
    hasBus = False   # Não usar ônibus
    presetMarch = None # Preset de marcha (1 a 6) ou None para escolher manualmente
    USE_MAIN_MARCH = 1  # Usar a marcha principal
    USE_FIRST_DELEGATION_FIRST_MARCH = 3  # Usar a primeira marcha da primeira delegação
    USE_FIRST_DELEGATION_SECOND_MARCH = 4  # Usar a segunda marcha da primeira delegação
    USE_SECOND_DELEGATION_FIRST_MARCH = 5  # Usar a primeira marcha da segunda delegação
    USE_SECOND_DELEGATION_SECOND_MARCH = 6  # Usar a segunda marcha da segunda delegação

    _isKvk = False # Nos KvKs o back button não funciona.

    mode = get_device_mode(device)

    print(f"[>] Loop {loop_iter} em {display_name} ({device_id}) [{device['type']}] - modo: {mode}")
    try:
        # FARM: comportamento anterior (kill giganto, delegações, etc.)
        if mode == 'farm':
            if KILL_GIGANTO or (device_id not in DONT_KILL_GIGANTO_ID_LIST):
                width, height = emulator_api.get_screen_size(device_id, adb_path)
                # Configura display para este device (agora usando device_id)
                aoa_actions.configure_display(device_id=device_id, width=width, height=height)

            _kill_giganto(device_id, adb_path, giganto_level=giganto_level, isDelegation=delegation, hasBus=hasBus, selectedMarch=USE_MAIN_MARCH, presetMarch=presetMarch, isKvk=_isKvk)
            # aoa_actions.kill_small_mutants(device_id, adb_path)
            
            _kill_giganto(device_id, adb_path, giganto_level=giganto_level, isDelegation=delegation, hasBus=hasBus, selectedMarch=USE_FIRST_DELEGATION_FIRST_MARCH, presetMarch=presetMarch, isKvk=_isKvk)
            _kill_giganto(device_id, adb_path, giganto_level=giganto_level, isDelegation=delegation, hasBus=hasBus, selectedMarch=USE_SECOND_DELEGATION_FIRST_MARCH, presetMarch=presetMarch, isKvk=_isKvk)
            
            _kill_giganto(device_id, adb_path, giganto_level=giganto_level, isDelegation=delegation, hasBus=hasBus, selectedMarch=USE_FIRST_DELEGATION_SECOND_MARCH, presetMarch=presetMarch, isKvk=_isKvk)
            _kill_giganto(device_id, adb_path, giganto_level=giganto_level, isDelegation=delegation, hasBus=hasBus, selectedMarch=USE_SECOND_DELEGATION_SECOND_MARCH, presetMarch=presetMarch, isKvk=_isKvk)



        # HEAL: focar em curar tropas no hospital
        elif mode == 'heal':
            # Ajuste o valor de cura conforme necessário (ex.: 1500)
            try:
                print(f"[>] Executando cura em {display_name} ({device_id})")
                aoa_actions.heal_troops(7000, device_id, adb_path)
            except AttributeError:
                print(f"[!] Função heal_troops não encontrada em aoa_actions para {display_name}")
            # também podemos pressionar help para manter o jogo ativo
            aoa_actions.press_help_button(device_id, adb_path)

        aoa_actions.press_help_button(device_id, adb_path)
        aoa_actions.press_top_left_back_button(device_id, adb_path)

    except Exception as e:
        print(f"[!] Erro ao executar ações ({mode}) em {display_name}: {e}")

    time.sleep(ACTION_DELAY)

def _kill_giganto(device_id, adb_path, giganto_level, isDelegation, hasBus, selectedMarch, presetMarch=None, isKvk=False):
    march_name_map = {
        1: 'Main march',
        2: 'Bus',
        3: 'First delegation - first march',
        4: 'First delegation - second march',
        5: 'Second delegation - first march',
        6: 'Second delegation - second march'
    }

    # Choose which march to use here (change variable below to rotate executions)
    # selectedMarch = USE_MAIN_MARCH
    march_name = march_name_map.get(selectedMarch, f'March: #{selectedMarch}')
    print(f"[>] Executando kill_giganto ({march_name})")
    # call kill_giganto with the selected march
    aoa_actions.kill_giganto(device_id, adb_path, giganto_level=giganto_level, delegation=isDelegation, hasBus=hasBus, selectedMarch=selectedMarch, presetMarch=presetMarch, isKvk=isKvk)
    
    aoa_actions.press_top_left_back_button(device_id, adb_path)
    time.sleep(2)
    aoa_actions.press_top_left_back_button(device_id, adb_path)
    time.sleep(2)

def _check_game_loaded(dev):
    while not _check_screen_element(dev, "map_button"):
        print(f"[!] O jogo ainda não carregou completamente em {dev['display_name']} ({dev['id']}). Aguardando mais 30 segundos... [{time.strftime('%H:%M:%S')}]")
        time.sleep(30)

        if _check_screen_element_and_click(dev, "retry_button") or _check_screen_element_and_click(dev, "server_maintenance_confirm_button"):
            print(f"[!] Server error or under maintenance. Trying to restart the game in {dev['display_name']} ({dev['id']})... [{time.strftime('%H:%M:%S')}]")
            time.sleep(2)
            game_launcher.run_aoa([dev])  # Roda as ações do AOA após reiniciar o app

        if _check_screen_element_and_click(dev, "gang_summon_button"):
            time.sleep(2)
            emulator_api.press_back_esc(dev['id'], dev['adb_path'])
        
        _check_screen_element_and_click(dev, "overlord_button")
    time.sleep(30)  # Espera um pouco mais para garantir que o jogo esteja estável

def main():
    print("Monitor de dispositivos ADB ativo. Pressione Ctrl+C para sair.\n")

    # Lê parâmetros opcionais: 'bluestacks' ou 'ldplayer' e '--debug' para saída verbosa
    target = None
    debug = False
    if len(sys.argv) >= 2:
        for arg in sys.argv[1:]:
            a = arg.lower()
            if a in ("bluestacks", "ldplayer"):
                target = a
            elif a in ("--debug", "-d"):
                debug = True
            else:
                print("Uso: monitor.py [bluestacks|ldplayer] [--debug]")
                sys.exit(1)

    # Apply debug mode to modules
    if debug:
        aoa_actions.DEBUG = True
        emulator_api.VERBOSE = True
    else:
        aoa_actions.DEBUG = False
        emulator_api.VERBOSE = False

    try:
        help_button_interval = 1  # Intervalo para pressionar o botão de ajuda
        loop_iter = 0
        while True:
            loop_iter += 1
            print(f"\n--- Loop {loop_iter} - iniciando varredura ---")
            start = time.time()
            devices = emulator_api.list_devices(target)  # passa o filtro aqui
            current_ids = [d["id"] for d in devices]

            for dev in devices:
                if dev["id"] not in active_devices:
                    handle_new_device(dev)

            for d_id in list(active_devices.keys()):
                if d_id not in current_ids:
                    handle_disconnect(d_id)

            for dev in active_devices.values():
                if dev['id'] not in WHITELIST_IDS:
                    # if not emulator_api.is_app_running(dev['id'], dev['adb_path'], 'com.tap4fun.ape.gplay'):
                    if not emulator_api.is_app_in_foreground(dev['id'], dev['adb_path'], 'com.tap4fun.ape.gplay'):
                        print(f"[!] O jogo não está rodando em {dev['display_name']} ({dev['id']}). Reiniciando o app... [{time.strftime('%H:%M:%S')}]")
                        game_launcher.start_game([dev])  # Usa a função start_game para reiniciar o app
                        _check_game_loaded(dev)
                        game_launcher.run_aoa([dev])  # Roda as ações do AOA após reiniciar o app
                    else:
                        print(f"[>] O jogo está rodando normalmente em {dev['display_name']} ({dev['id']}).")

                        _check_screen_element_and_click(dev, "retry_button")
                        _check_screen_element_and_click(dev, "server_maintenance_confirm_button")
                        _check_screen_element_and_click(dev, "overlord_button")
                        _check_screen_element_and_click(dev, "gang_summon_button")

                    perform_actions(dev, loop_iter)

            duration = time.time() - start
            sleep_time = max(0, SCAN_INTERVAL - duration)
            # time.sleep(sleep_time)
            end_wait = time.time() + sleep_time
            while time.time() < end_wait:
                for dev in active_devices.values():
                    if dev['id'] not in WHITELIST_IDS:
                        aoa_actions.press_help_button(dev['id'], dev['adb_path'])
                        time.sleep(help_button_interval)


    except KeyboardInterrupt:
        print("\nEncerrando monitor de dispositivos...")

def _check_screen_element(device, element_name):
    _screen_element_xy_coords = aoa_actions.COORDS[element_name + '_xy']
    _screen_element_wh_coords = aoa_actions.COORDS[element_name + '_wh']
    _screen_element_coords = (*_screen_element_xy_coords, _screen_element_xy_coords[0]+_screen_element_wh_coords[0], _screen_element_xy_coords[1]+_screen_element_wh_coords[1])

    template_raw = emulator_api.capturar_retangulo(device['id'], *_screen_element_coords)
    match_found, locations = emulator_api.match_template(template_raw, f"{element_name}.png")

    return match_found

def _check_screen_element_and_click(device, element_name):
    if _check_screen_element(device, element_name):
        print(f"[!] Elemento '{element_name}' detectado em {device['display_name']} ({device['id']}). Clicando...")
        aoa_actions.click_coord(device['id'], device['adb_path'], element_name + "_click")
        # emulator_api.press_back_esc(device['id'], device['adb_path'])
        # _check_game_loaded(device)
        return True
    return False

if __name__ == "__main__":
    main()
