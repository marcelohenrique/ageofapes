import subprocess
import os

# Caminhos padrão
ADB_PATHS = {
    "default": "adb",
    "bluestacks": r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
}

# Selecione qual ADB usar: "default" ou "bluestacks"
CURRENT_ADB = os.getenv("ADB_MODE", "bluestacks")  # ou altere manualmente aqui

def get_adb_path():
    """Retorna o caminho configurado para o executável ADB."""
    adb_executable = ADB_PATHS.get(CURRENT_ADB, ADB_PATHS["default"])
    if not os.path.exists(adb_executable) and CURRENT_ADB != "default":
        print(f"Aviso: Caminho do ADB '{adb_executable}' não encontrado, usando ADB padrão.")
        return "adb"
    return adb_executable

def run_adb_command(cmd):
    adb_exec = get_adb_path()
    result = subprocess.run(f'"{adb_exec}" {cmd}', shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def list_devices():
    output = run_adb_command('devices')
    print(output)
    lines = output.splitlines()[1:]  # pular cabeçalho
    devices = [line.split()[0] for line in lines if 'device' in line]
    return devices

def tap(device, x, y):
    run_adb_command(f'-s {device} shell input tap {x} {y}')

def swipe(device, x1, y1, x2, y2, duration=500):
    run_adb_command(f'-s {device} shell input swipe {x1} {y1} {x2} {y2} {duration}')

def press_back(device):
    run_adb_command(f'-s {device} shell input keyevent 4')


if __name__ == "__main__":
    print("Iniciou")
    devices = list_devices()

    if not devices:
        print("Nenhum dispositivo conectado")
    else:
        print("Dispositivos detectados:")
        for device in devices:
            print(f" - {device}")