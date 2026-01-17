import time
import sys
from emulator_api import list_devices
from aoa_actions import kill_giganto, press_help_button  # ← importa a função que realiza a ação

SCAN_INTERVAL = 5 # 5*60  # segundos entre varreduras do ADB
ACTION_DELAY = 2   # segundos entre ações nos dispositivos

WHITELIST_IDS = { # Preencha com os deviceids que quer isolar
    ''
    # , 'emulator-5560' # FarmerApe05
    # , 'emulator-5558' # FarmerApe08
    # , ''
    # bluestacks
    # , 'emulator-5554' # minion01
    # , 'emulator-5564' # minion02
}

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

def handle_disconnect(device_id):
    device = active_devices.pop(device_id, None)
    if device:
        print(f"[-] Dispositivo desconectado: {device['display_name']} ({device_id}) [{device['type']}]")

def perform_actions(device):
    """Executa a ação kill_giganto no dispositivo detectado."""
    adb_path = device["adb_path"]
    display_name = device["display_name"]
    device_id = device["id"]

    print(f"[>] Executando kill_giganto em {display_name} ({device_id}) [{device['type']}]")
    try:
        if KILL_GIGANTO or ( device_id not in DONT_KILL_GIGANTO_ID_LIST ):
            kill_giganto(device_id, adb_path)  # passa ID e caminho do adb (compatível com util.py)
        press_help_button(device_id, adb_path)
    except Exception as e:
        print(f"[!] Erro ao executar kill_giganto em {display_name}: {e}")

    time.sleep(ACTION_DELAY)

def main():
    print("Monitor de dispositivos ADB ativo. Pressione Ctrl+C para sair.\n")

    # Lê parâmetro opcional: 'bluestacks' ou 'ldplayer'
    target = None
    if len(sys.argv) >= 2:
        t = sys.argv[1].lower()
        if t in ("bluestacks", "ldplayer"):
            target = t
        else:
            print("Uso: monitor.py [bluestacks|ldplayer]")
            sys.exit(1)

    try:
        help_button_interval = 1  # Intervalo para pressionar o botão de ajuda
        while True:
            start = time.time()
            devices = list_devices(target)  # passa o filtro aqui
            current_ids = [d["id"] for d in devices]

            for dev in devices:
                if dev["id"] not in active_devices:
                    handle_new_device(dev)

            for d_id in list(active_devices.keys()):
                if d_id not in current_ids:
                    handle_disconnect(d_id)

            for dev in active_devices.values():
                if dev['id'] not in WHITELIST_IDS:
                    perform_actions(dev)

            duration = time.time() - start
            sleep_time = max(0, SCAN_INTERVAL - duration)
            # time.sleep(sleep_time)
            end_wait = time.time() + sleep_time
            while time.time() < end_wait:
                for dev in active_devices.values():
                    if dev['id'] not in WHITELIST_IDS:
                        press_help_button(dev['id'], dev['adb_path'])
                        time.sleep(help_button_interval)


    except KeyboardInterrupt:
        print("\nEncerrando monitor de dispositivos...")

if __name__ == "__main__":
    main()
