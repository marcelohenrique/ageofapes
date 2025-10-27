import subprocess
import os

def stop_adb_server(adb_path, server_port):
    """Para o daemon adb associando ao executável"""
    env = os.environ.copy()
    env["ADB_SERVER_SOCKET"] = f"tcp:127.0.0.1:{server_port}"

    # Comando para parar o servidor adb na porta/config especificada
    cmd = f'"{adb_path}" -P {server_port} kill-server'
    print(f"Parando servidor ADB: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)

    if result.returncode == 0:
        print(f"Servidor ADB {adb_path} parado com sucesso.")
    else:
        print(f"Falha ao parar servidor ADB {adb_path}.\n{result.stderr}")

def start_adb_server(adb_path, server_port):
    """Inicia o daemon adb se não estiver ativo"""
    env = os.environ.copy()
    env["ADB_SERVER_SOCKET"] = f"tcp:127.0.0.1:{server_port}"

    # Tenta matar antes para garantir reinício limpo
    # stop_adb_server(adb_path, server_port)

    # Depois inicia o servidor
    cmd = f'"{adb_path}" -P {server_port} start-server'
    print(f"Iniciando servidor ADB: {cmd}")
    subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    print(f"Servidor ADB iniciado na porta {server_port}")

# Exemplo de uso
if __name__ == "__main__":
    ADB_BLUESTACKS = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
    ADB_DEFAULT = "adb"

    stop_adb_server(ADB_BLUESTACKS, 5037)
    stop_adb_server(ADB_DEFAULT, 5038)

    start_adb_server(ADB_BLUESTACKS, 5037)
    start_adb_server(ADB_DEFAULT, 5038)
