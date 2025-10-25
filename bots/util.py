import subprocess
import time
import os
import re

# Caminho para o HD-Adb (BlueStacks)
ADB_BLUESTACKS = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"

# Caminho para o arquivo de configuração do BlueStacks 5
BLUESTACKS_CONF_PATH = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"


# ===============================
# Funções utilitárias básicas
# ===============================

def run_adb_command(cmd):
    """Executa comandos via HD-Adb do BlueStacks."""
    result = subprocess.run(f'"{ADB_BLUESTACKS}" {cmd}', shell=True, capture_output=True, text=True)
    return result.stdout.strip()


# ===============================
# Gerenciamento de conexões
# ===============================

def discover_bluestacks_instances():
    """Lê o arquivo bluestacks.conf e descobre automaticamente as instâncias e portas ADB."""
    instances = {}

    if not os.path.exists(BLUESTACKS_CONF_PATH):
        print(f"Aviso: {BLUESTACKS_CONF_PATH} não encontrado.")
        return instances

    print("=== Descobrindo instâncias BlueStacks ===")
    try:
        with open(BLUESTACKS_CONF_PATH, "r", encoding="utf-8") as conf:
            content = conf.read()
        matches = re.findall(r'bst\.instance\.([^.]+)\.status\.adb_port="(\d+)"', content)
        for name, port in matches:
            port = int(port)
            instances[port] = name
            print(f"  Descoberto: {name} -> porta {port}")
    except Exception as e:
        print(f"Erro ao ler bluestacks.conf: {e}")

    return instances


def connect_all_known_ports(instance_mapping):
    """Conecta apenas instâncias ainda não conectadas (ignora as que já estão atachadas automaticamente pelo BlueStacks)."""
    print("\nConectando apenas instâncias ainda não conectadas...")

    # Obter lista atual de dispositivos conectados
    output = run_adb_command("devices")
    connected_ids = [line.split()[0] for line in output.splitlines() if "device" in line]

    for port, name in instance_mapping.items():
        port_str = f"127.0.0.1:{port}"
        emulator_id = f"emulator-{port - 1}"  # Relação comum 5555 <-> emulator-5554

        # Evita reconectar se a instância já estiver anexada via ADB automático
        if any(port_str in dev or emulator_id in dev for dev in connected_ids):
            print(f"  {name:20} (porta {port}): já conectada (ignorada).")
            continue

        result = subprocess.run(f'"{ADB_BLUESTACKS}" connect {port_str}',
                                shell=True, capture_output=True, text=True)
        print(f"  {name:20} (porta {port}): {result.stdout.strip()}")


def disconnect_emulator_instances():
    """Remove conexões locais emulator-* para evitar listagem duplicada."""
    print("Limpando conexões locais 'emulator-*' duplicadas...")
    output = run_adb_command("devices")
    for line in output.splitlines():
        if line.startswith("emulator-"):
            dev = line.split()[0]
            subprocess.run(f'"{ADB_BLUESTACKS}" disconnect {dev}', shell=True, capture_output=True, text=True)
            print(f"Desconectado duplicado: {dev}")


# ===============================
# Listagem e mapeamento
# ===============================

def list_devices_with_ports(instance_mapping):
    """Lista todas as conexões ADB ativas (ignorando duplicações emulator-*)."""
    output = run_adb_command("devices -l")
    lines = output.splitlines()[1:]
    devices = []

    for line in lines:
        if "device" not in line or "127.0.0.1" not in line:
            continue

        device_id = line.split()[0]
        port = int(device_id.split(":")[1])
        name = instance_mapping.get(port, f"Desconhecido (porta {port})")

        devices.append({
            "id": device_id,
            "port": port,
            "name": name
        })

    return devices


def list_devices():
    """Fluxo completo: descobre instâncias, limpa duplicados e conecta apenas o necessário."""
    disconnect_emulator_instances()
    instances = discover_bluestacks_instances()
    connect_all_known_ports(instances)
    devices = list_devices_with_ports(instances)
    return devices


# ===============================
# Ações ADB genéricas
# ===============================

def tap(device, x, y):
    """Simula toque na tela."""
    run_adb_command(f'-s {device} shell input tap {x} {y}')


def swipe(device, x1, y1, x2, y2, duration=500):
    """Simula gesto de deslizar."""
    run_adb_command(f'-s {device} shell input swipe {x1} {y1} {x2} {y2} {duration}')


def press_back(device):
    """Simula o botão VOLTAR (ESC)."""
    run_adb_command(f'-s {device} shell input keyevent 4')


# ===============================
# Execução direta
# ===============================

if __name__ == "__main__":
    devices = list_devices()
    print("\n=== Dispositivos conectados ===")
    if not devices:
        print("Nenhum dispositivo conectado.\n")
    else:
        for d in devices:
            print(f"  {d['name']:20} | ID: {d['id']:20} | Porta: {d['port']}")
