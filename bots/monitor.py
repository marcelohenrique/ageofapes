import time
from util import list_devices
from actions import kill_giganto  # ← importa a função que realiza a ação

SCAN_INTERVAL = 5*60  # segundos entre varreduras do ADB
ACTION_DELAY = 2   # segundos entre ações nos dispositivos

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
        kill_giganto(device_id, adb_path)  # passa ID e caminho do adb (compatível com util.py)
    except Exception as e:
        print(f"[!] Erro ao executar kill_giganto em {display_name}: {e}")

    time.sleep(ACTION_DELAY)

def main():
    print("Monitor de dispositivos ADB ativo. Pressione Ctrl+C para sair.\n")

    try:
        while True:
            start = time.time()
            devices = list_devices()
            current_ids = [d["id"] for d in devices]

            for dev in devices:
                if dev["id"] not in active_devices:
                    handle_new_device(dev)

            for d_id in list(active_devices.keys()):
                if d_id not in current_ids:
                    handle_disconnect(d_id)

            for dev in active_devices.values():
                perform_actions(dev)

            duration = time.time() - start
            sleep_time = max(0, SCAN_INTERVAL - duration)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nEncerrando monitor de dispositivos...")

if __name__ == "__main__":
    main()
