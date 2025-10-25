import time
from util import list_devices
from actions import kill_giganto

# Tempo de verificação de novos dispositivos (em segundos)
SCAN_INTERVAL = 5*60

# Tempo entre ações para cada dispositivo
ACTION_DELAY = 3

# Dicionário para rastrear dispositivos ativos e evitar repetição
active_devices = {}

def handle_new_device(device_id):
    print(f"[+] Novo dispositivo detectado: {device_id}")
    active_devices[device_id] = {"last_action": 0}

def perform_actions(device_id):
    print(f"[>] Executando ações em {device_id}")
    kill_giganto(device_id)
    time.sleep(ACTION_DELAY)

def main():
    print("Monitor de dispositivos ADB ativo. Pressione Ctrl+C para sair.\n")

    try:
        while True:
            # Verifica dispositivos conectados
            devices = list_devices()

            # Identifica novos dispositivos
            for dev in devices:
                device_id = dev["id"]
                if device_id not in active_devices:
                    handle_new_device(device_id)

            # Remove dispositivos desconectados
            for known_id in list(active_devices.keys()):
                if known_id not in devices:
                    print(f"[-] Dispositivo desconectado: {known_id}")
                    del active_devices[known_id]

            # Executa ações básicas para cada dispositivo ativo
            for device_id in active_devices:
                perform_actions(device_id)

            # Espera antes de nova varredura
            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        print("\nEncerrando monitor de dispositivos...")

if __name__ == "__main__":
    main()
