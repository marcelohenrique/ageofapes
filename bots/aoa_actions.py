from time import sleep
from emulator_api import press_back_esc, tap, list_devices

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
    tap(device_id, adb_path, x, y)

def click_giganto(device_id, adb_path):
    print("Clica no botão Giganto.")
    x, y = COORDS["giganto_search_button"]
    tap(device_id, adb_path, x, y)

def click_reduce_search_level(device_id, adb_path):
    print("Clica no botão para reduzir o nível de busca.")
    x, y = COORDS["reduce_search_level"]
    tap(device_id, adb_path, x, y)

def click_second_search(device_id, adb_path):
    print("Clica no segundo botão de busca.")
    x, y = COORDS["second_search_button"]
    tap(device_id, adb_path, x, y)

def click_small_mutants(device_id, adb_path):
    print("Clica no botão Small Mutants.")
    x, y = COORDS["small_mutants"]
    tap(device_id, adb_path, x, y)

def click_first_rally(device_id, adb_path):
    print("Clica no primeiro botão de rally.")
    x, y = COORDS["first_rally_button"]
    tap(device_id, adb_path, x, y)

def click_second_rally(device_id, adb_path):
    print("Clica no segundo botão de rally.")
    x, y = COORDS["second_rally_button"]
    tap(device_id, adb_path, x, y)

def click_march(device_id, adb_path):
    print("Clica no botão de marcha.")
    x, y = COORDS["march_button"]
    tap(device_id, adb_path, x, y)

def click_help_gang(device_id, adb_path):
    print("Clica no botão de ajuda/gangue.")
    x, y = (980, 670)
    tap(device_id, adb_path, x, y)

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
    press_back_esc(device_id, adb_path)

def press_help_button(device_id, adb_path):
    """Clica no botão de ajuda/gangue."""
    # press_back(device_id, adb_path)
    sleep(2)
    click_help_gang(device_id, adb_path)
    sleep(2)
    press_back_esc(device_id, adb_path)

if __name__ == "__main__":
    devices = list_devices()
    if devices:
        device = devices[0]
        print(f"Usando dispositivo {device['display_name']} ({device['id']}) [{device['type']}]")
        # kill_giganto(device["id"], device["adb_path"])
        press_help_button(device["id"], device["adb_path"])
    else:
        print("Nenhum dispositivo conectado.")
