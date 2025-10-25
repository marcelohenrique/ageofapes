import subprocess
import time
import os
import re

# Caminho para o HD-Adb (BlueStacks)
ADB_BLUESTACKS = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"

# Caminho para o arquivo de configuração do BlueStacks 5
BLUESTACKS_CONF_PATH = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"


# =====================================================
# Execução ADB
# =====================================================

def run_adb_command(cmd):
    """Executa comando via HD-Adb do BlueStacks."""
    result = subprocess.run(f'"{ADB_BLUESTACKS}" {cmd}', shell=True, capture_output=True, text=True)
    return result.stdout.strip()


# =====================================================
# Descoberta e mapeamento de instâncias BlueStacks
# =====================================================

def discover_bluestacks_instances():
    """Lê o bluestacks.conf e descobre instâncias com porta e display_name."""
    instances = {}

    if not os.path.exists(BLUESTACKS_CONF_PATH):
        print(f"Aviso: {BLUESTACKS_CONF_PATH} não encontrado.")
        return instances

    print("=== Descobrindo instâncias BlueStacks ===")
    try:
        with open(BLUESTACKS_CONF_PATH, "r", encoding="utf-8") as conf:
            content = conf.read()

        # Encontrar todos os nomes internos e suas portas
        ports = re.findall(r'bst\.instance\.([^.]+)\.status\.adb_port="(\d+)"', content)
        # Encontrar display_names
        display_names = dict(re.findall(r'bst\.instance\.([^.]+)\.display_name="([^"]+)"', content))

        for inst_name, port in ports:
            port = int(port)
            display_name = display_names.get(inst_name, inst_name)
            instances[port] = {
                "internal_name": inst_name,
                "display_name": display_name,
            }
            print(f"  Descoberto: {display_name} (interno: {inst_name}) -> porta {port}")

    except Exception as e:
        print(f"Erro ao ler bluestacks.conf: {e}")

    return instances


# =====================================================
# Gerenciamento de conexões
# =====================================================

def disconnect_emulator_instances():
    """Remove conexões 'emulator-*' para limpar duplicados."""
    print("Limpando conexões locais 'emulator-*' duplicadas...")
    output = run_adb_command("devices")
    for line in output.splitlines():
        if line.startswith("emulator-"):
            dev = line.split()[0]
            subprocess.run(f'"{ADB_BLUESTACKS}" disconnect {dev}', shell=True, capture_output=True, text=True)
            print(f"Desconectado duplicado: {dev}")


def connect_all_known_ports(instance_mapping):
    """Conecta apenas instâncias não conectadas (ignora as autoanexadas pelo BlueStacks)."""
    print("\nConectando apenas instâncias ainda não conectadas...")

    # Lista de dispositivos já conectados
    output = run_adb_command("devices")
    connected_ids = [line.split()[0] for line in output.splitlines() if "device" in line]

    for port, info in instance_mapping.items():
        name = info["display_name"]
        port_str = f"127.0.0.1:{port}"
        emulator_match = f"emulator-{port - 1}"  # Relação típica porta 5555 <-> 5554

        # Evita reconectar se já conectado
        if any(port_str in dev or emulator_match in dev for dev in connected_ids):
            print(f"  {name:20} (porta {port}): já conectada (ignorada).")
            continue

        result = subprocess.run(f'"{ADB_BLUESTACKS}" connect {port_str}',
                                shell=True, capture_output=True, text=True)
        print(f"  {name:20} (porta {port}): {result.stdout.strip()}")


# =====================================================
# Listagem de dispositivos com metadados
# =====================================================

def list_devices_with_ports(instance_mapping):
    """Lista conexões ADB ativas e faz correspondência com nomes amigáveis."""
    output = run_adb_command("devices -l")
    lines = output.splitlines()[1:]
    devices = []

    for line in lines:
        if "device" not in line or "127.0.0.1" not in line:
            continue

        device_id = line.split()[0]
        port = int(device_id.split(":")[1])

        entry = instance_mapping.get(
            port,
            {"display_name": f"Desconhecido (porta {port})", "internal_name": ""}
        )

        devices.append({
            "id": device_id,
            "port": port,
            "display_name": entry["display_name"],
            "internal": entry["internal_name"],
        })

    return devices


def list_devices():
    """Executa fluxo completo: detectar -> conectar -> listar."""
    disconnect_emulator_instances()
    instances = discover_bluestacks_instances()
    connect_all_known_ports(instances)
    devices = list_devices_with_ports(instances)
    return devices


# =====================================================
# Ações ADB Genéricas
# =====================================================

def tap(device, x, y):
    run_adb_command(f'-s {device} shell input tap {x} {y}')


def swipe(device, x1, y1, x2, y2, duration=500):
    run_adb_command(f'-s {device} shell input swipe {x1} {y1} {x2} {y2} {duration}')


def press_back(device):
    run_adb_command(f'-s {device} shell input keyevent 4')


# =====================================================
# Execução direta
# =====================================================

if __name__ == "__main__":
    devices = list_devices()
    print("\n=== Dispositivos conectados ===")
    if not devices:
        print("Nenhum dispositivo conectado.\n")
    else:
        for d in devices:
            print(f"  {d['display_name']:20} | Porta: {d['port']} | ID: {d['id']}")
