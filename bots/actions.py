from time import sleep
from util import press_back, tap, list_devices

# Coordenadas dos botões — ajuste conforme sua resolução ou emulador
COORDS = {
    "first_search_button": (60, 540),       # exemplo: botão de busca no topo
    "giganto_search_button": (480, 480),     # exemplo: botão Giganto Mutant
    "reduce_search_level": (83, 642),
    "second_search_button": (1104, 646),
    "first_rally_button": (998, 549),
    "second_rally_button": (996, 500),
    "march_button": (1096, 660),
    "small_mutants": (800, 500)  # exemplo: botão Small Mutants
}

def click_search(device):
    print("Clica no botão de busca.")
    x, y = COORDS["first_search_button"]
    tap(device, x, y)

def click_giganto(device):
    print("Clica no botão Giganto.")
    x, y = COORDS["giganto_search_button"]
    tap(device, x, y)

def click_reduce_search_level(device):
    print("Clica no botão para reduzir o nível de busca.")
    x, y = COORDS["reduce_search_level"]
    tap(device, x, y)

def click_second_search(device):
    print("Clica no segundo botão de busca.")
    x, y = COORDS["second_search_button"]
    tap(device, x, y)

def click_small_mutants(device):
    print("Clica no botão Small Mutants.")
    x, y = COORDS["small_mutants"]
    tap(device, x, y)

# Exemplo de ação combinada (encadeada)
def ataque_mutantes(device):
    print("Executa uma sequência de ações comum.")
    click_search(device)
    click_giganto(device)
    click_small_mutants(device)

def click_first_rally(device):
    print("Clica no primeiro botão de rally.")
    x, y = COORDS["first_rally_button"]
    tap(device, x, y)

def click_second_rally(device):
    print("Clica no segundo botão de rally.")
    x, y = COORDS["second_rally_button"]
    tap(device, x, y)

def click_march(device):
    print("Clica no botão de marcha.")
    x, y = COORDS["march_button"]
    tap(device, x, y)

def kill_giganto(device):
    click_search(device)
    sleep(2)
    click_giganto(device)
    sleep(1)
    click_reduce_search_level(device)
    sleep(1)
    click_reduce_search_level(device)
    sleep(1)
    click_reduce_search_level(device)
    sleep(1)
    click_reduce_search_level(device)
    sleep(1)
    click_second_search(device)
    sleep(5)
    click_first_rally(device)
    sleep(2)
    click_second_rally(device)
    sleep(5)
    click_march(device)
    sleep(2)
    press_back(device)

if __name__ == "__main__":
    devices = list_devices()
    if devices:
        device = devices[0]
        print(f"Usando dispositivo {device}")
        # ataque_mutantes(device)
        kill_giganto(device)
    else:
        print("Nenhum dispositivo conectado.")
