import time
from actions import kill_giganto
from util import discover_bluestacks_instances, connect_all_known_ports, list_devices_with_ports

SCAN_INTERVAL = 5*60  # 5 minutes
ACTION_DELAY = 3

active_devices = {}

def handle_new_device(device):
    print(f"[+] Novo dispositivo detectado: {device['display_name']} ({device['id']})")
    active_devices[device['id']] = device

def handle_disconnect(device_id):
    print(f"[-] Dispositivo desconectado: {device_id}")
    del active_devices[device_id]

def perform_actions(device):
    # Exemplo de ação recorrente
    print(f"[>] Executando ações em {device['display_name']} - ID {device['id']}")
    kill_giganto(device['id'])
    time.sleep(ACTION_DELAY)

def main():
    print("Monitor de dispositivos ADB ativo. Pressione Ctrl+C para sair.\n")

    # Etapa inicial: detecta e conecta uma vez
    instances = discover_bluestacks_instances()
    connect_all_known_ports(instances)

    try:
        while True:
            devices = list_devices_with_ports(instances)

            # Detectar novos dispositivos
            for dev in devices:
                if dev["id"] not in active_devices:
                    handle_new_device(dev)

            # Detectar desconexões
            for d_id in list(active_devices.keys()):
                if not any(dev["id"] == d_id for dev in devices):
                    handle_disconnect(d_id)

            # Realizar ações em todos os conectados
            for dev in active_devices.values():
                perform_actions(dev)

            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        print("\nEncerrando monitor de dispositivos...")

if __name__ == "__main__":
    main()
