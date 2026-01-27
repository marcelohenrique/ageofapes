import subprocess
import time
import os
import re

ADB_DEFAULT = "adb"  # LDPlayer e genérico
ADB_BLUESTACKS = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
BLUESTACKS_CONF_PATH = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"

# # ==================================================================
# # Inicia o daemon na porta correta se ainda não estiver ativo
# # ==================================================================
# def start_adb_server(adb_path, server_port):
#     env = os.environ.copy()
#     # Testa servidor usando 'adb devices' (não mata nem interfere)
#     test_cmd = f'"{adb_path}" -P {server_port} devices'
#     result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, env=env)
#     # Se falhar, tenta iniciar servidor
#     if "cannot connect" in result.stderr or result.returncode != 0:
#         start_cmd = f'"{adb_path}" start-server -P {server_port}'
#         subprocess.run(start_cmd, shell=True, capture_output=True, text=True, env=env)

# ==================================================================
# Execução genérica de comandos ADB, isolando servidores
# ==================================================================
def run_adb_command(adb_path, cmd):
    env = os.environ.copy()
    # Porta isolada para cada adb
    if "BlueStacks_nxt" in adb_path:
        server_port = "5037"
        env["ADB_SERVER_SOCKET"] = f"tcp:127.0.0.1:{server_port}"
    else:
        # server_port = "5038"
        server_port = "5037"
        env["ADB_SERVER_SOCKET"] = f"tcp:127.0.0.1:{server_port}"
    # start_adb_server(adb_path, server_port)
    full_cmd = f'"{adb_path}" -P {server_port} {cmd}'
    # full_cmd = f'"{adb_path}" {cmd}'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, env=env)
    if result.stderr.strip():
        print(f"[ADB ERR] {result.stderr.strip()}")
    return result.stdout.strip()

# ==================================================================
# Descoberta BlueStacks (conf e fallback via HD-Adb)
# ==================================================================
def discover_bluestacks_instances():
    instances = {}
    print("=== Descobrindo instâncias BlueStacks ===")

    # # Verifica existência do arquivo bluestacks.conf
    # if not os.path.exists(BLUESTACKS_CONF_PATH):
    #     print(f"[DEBUG] Arquivo bluestacks.conf não encontrado em: {BLUESTACKS_CONF_PATH}")
    # else:
    #     try:
    #         insts_raw = discover_bluestacks_instances_from_conf(BLUESTACKS_CONF_PATH)
    #         # Adiciona info padrão que outros métodos do util usam
    #         instances = {}
    #         for info in insts_raw:
    #             instances[info["id"]] = {
    #                 "id": info["id"],
    #                 "display_name": info["display_name"],
    #                 "adb_path": ADB_BLUESTACKS,
    #                 "type": "BlueStacks",
    #                 "port": info["adb_port"]
    #             }
    #         return instances
    #     except Exception as e:
    #         print(f"[ERRO] Exceção ao ler bluestacks.conf: {e}")

    # Se nenhuma instância identificada via conf, tenta via comando adb devices
    if not instances:
        print("[DEBUG] Nenhuma instância detectada pelo conf bluestacks, tentando via adb devices...")
        result = run_adb_command(ADB_BLUESTACKS, "devices")
        print(f"[DEBUG] Resultado do comando 'adb devices':\n{result}")
        for line in result.splitlines():
            print(f"[DEBUG] Linha analisada: '{line}'")
            if "device" in line and ("127.0.0.1:" in line or "emulator-" in line):
                device_id = line.split()[0].strip()
                if ":" in device_id:
                    port = device_id.split(":")[1]
                else:
                    port = device_id.split("-")[-1]
                instances[device_id] = {
                    "id": device_id,
                    "display_name": f"BlueStacks-{port}",
                    "adb_path": ADB_BLUESTACKS,
                    "type": "BlueStacks",
                    "port": port
                }
                print(f"[DEBUG] Instância detectada via adb: {device_id} na porta {port}")

    print(f"[DEBUG] Total de instâncias BlueStacks detectadas: {len(instances)}")
    return instances

def discover_bluestacks_instances_from_conf(conf_path):
    with open(conf_path, "r", encoding="utf-8") as f:
        data = f.read()

    instance_re = re.compile(r'bst\.instance\.([^.=\n]+)\.display_name="([^"\n]*)"')
    port_re = re.compile(r'bst\.instance\.([^.=\n]+)\.status\.adb_port="(\d+)"')
    
    # Mapeia instância → display_name
    names = {m.group(1): m.group(2) for m in instance_re.finditer(data)}
    # Mapeia instância → porta
    ports = {m.group(1): m.group(2) for m in port_re.finditer(data)}

    print(f"[DEBUG] Instâncias encontradas no conf: {list(names.keys())}")
    print(f"[DEBUG] Atribuições display_name: {names}")
    print(f"[DEBUG] Atribuições adb_port: {ports}")

    result = []
    for instance, display_name in names.items():
        if instance in ports and display_name:
            adb_port = ports[instance]
            print(f"[DEBUG] Instância '{display_name}' ({instance}) porta {adb_port}")
            result.append({"display_name": display_name, "adb_port": adb_port, "id": f"127.0.0.1:{adb_port}"})
        else:
            print(f"[DEBUG] Instância incompleta (sem porta ou nome): {instance}")

    print(f"[DEBUG] Total instâncias válidas: {len(result)}")
    return result

# ==================================================================
# Descoberta instâncias LDPlayer
# ==================================================================
def discover_ldplayer_instances():
    print("=== Descobrindo instâncias LDPlayer ===")
    instances = {}
    result = run_adb_command(ADB_DEFAULT, "devices")
    for line in result.splitlines():
        if "\tdevice" in line:
            device_id = line.split("\t")[0].strip()
            # Extrai 'porta' se device_id for no formato emulator-5554 ou 127.0.0.1:5555
            if ":" in device_id:
                port = device_id.split(":")[1]
            elif "-" in device_id:
                port = device_id.split("-")[1]
            else:
                port = device_id  # fallback para device_id
            instances[device_id] = {
                "id": device_id,
                "display_name": f"LDPlayer-{port}",
                "adb_path": ADB_DEFAULT,
                "type": "LDPlayer",
                "port": port
            }
    return instances


# ==================================================================
# Combina todos conectados para uso
# ==================================================================
def list_devices(target=None):
    """
    Combina dispositivos conectados.
    target: None|'bluestacks'|'ldplayer' - filtra descoberta conforme solicitado.
    """
    devices = {}
    if target == "bluestacks":
        bs = discover_bluestacks_instances()
        devices.update(bs)
    elif target == "ldplayer":
        ld = discover_ldplayer_instances()
        devices.update(ld)
    else:
        bs = discover_bluestacks_instances()
        devices.update(bs)
        ld = discover_ldplayer_instances()
        devices.update(ld)

    print("\nConectando apenas instâncias ainda não conectadas...")
    for device_id, info in devices.items():
        output = run_adb_command(info["adb_path"], f"connect {device_id}")
        print(f"  {info['display_name']:<20} (porta {info['port']}): {output}")
    print(f"\nTotal de dispositivos conectados: {len(devices)}")
    return list(devices.values())

# ==================================================================
# TAP e BACK genéricos usando o ADB correto
# ==================================================================
def tap(device_id, adb_path, x, y):
    cmd = f'-s "{device_id}" shell input tap {x} {y}'
    print(f"[ADB] TAP -> {cmd}")
    run_adb_command(adb_path, cmd)

def press_back_esc(device_id, adb_path):
    cmd = f'-s "{device_id}" shell input keyevent 4'
    print(f"[ADB] BACK -> {cmd}")
    run_adb_command(adb_path, cmd)

def start_app(device_id, adb_path, package_name):
    cmd = f'-s "{device_id}" shell monkey -p {package_name} 1'
    print(f"[ADB] START APP -> {cmd}")
    run_adb_command(adb_path, cmd)

def _escape_text_for_adb_input(text: str) -> str:
    # adb 'input text' requires spaces to be replaced with %s and '%' escaped as %25.
    # Also escape double quotes so they survive shell quoting.
    if text is None:
        return ""
    s = text.replace('%', '%25')
    s = s.replace(' ', '%s')
    s = s.replace('"', '\\"')
    return s


def send_text(device_id, adb_path, text, per_char_sleep=0.05):
    """Envia uma string para um campo de texto via ADB.

    Tenta usar `adb shell input text` (mais rápido). Se houver falha, faz fallback
    enviando a string caractere a caractere também via `input text` (uma a uma).

    - device_id: identificador exibido em `adb devices` (ex: 'emulator-5554' ou '127.0.0.1:5555')
    - adb_path: caminho para o executável adb a ser usado
    - text: texto a enviar
    - per_char_sleep: intervalo entre chars no fallback
    """
    if text is None:
        return

    # escaped = _escape_text_for_adb_input(text)
    # cmd = f'-s "{device_id}" shell input text "{escaped}"'
    # print(f"[ADB] SEND TEXT -> {cmd}")
    # out = run_adb_command(adb_path, cmd)

    # Se a saída indicar erro (adb pode imprimir mensagens de erro no stderr que já são mostradas
    # por run_adb_command), ou se a resposta não contiver nada útil, tentamos fallback por caracteres.
    # if out is None or out == "":
    # fallback: enviar por caracteres para contornar problemas com caracteres especiais
    for ch in text:
        esc_ch = _escape_text_for_adb_input(ch)
        cmd_c = f'-s "{device_id}" shell input text "{esc_ch}"'
        print(f"[ADB] SEND CHAR -> {cmd_c}")
        run_adb_command(adb_path, cmd_c)
        time.sleep(per_char_sleep)

if __name__ == "__main__":
    devices = list_devices()
    for device in devices:
        print(f"Dispositivo: {device['display_name']} ({device['id']}) [{device['type']}]")
        # start_app(device['id'], device['adb_path'], 'com.tap4fun.ape.gplay')
        press_back_esc(device['id'], device['adb_path'])
        # press_back_esc(device['id'], device['adb_path'])