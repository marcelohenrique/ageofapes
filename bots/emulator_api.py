import subprocess
import time
import os
import re

import cv2
import numpy
# import subprocess
from subprocess import Popen, PIPE

ADB_DEFAULT = "adb"  # LDPlayer e genérico
ADB_BLUESTACKS = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
BLUESTACKS_CONF_PATH = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"

# New: controllable verbosity flag used by other modules
VERBOSE = True

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
    if VERBOSE:
        print(f"[ADB] TAP -> {cmd}")
    run_adb_command(adb_path, cmd)

def press_back_esc(device_id, adb_path):
    cmd = f'-s "{device_id}" shell input keyevent 4'
    # if VERBOSE:
    print(f"[ADB] BACK -> {cmd}")
    run_adb_command(adb_path, cmd)

def start_app(device_id, adb_path, package_name):
    cmd = f'-s "{device_id}" shell monkey -p {package_name} 1'
    if VERBOSE:
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
        if VERBOSE:
            print(f"[ADB] SEND CHAR -> {cmd_c}")
        run_adb_command(adb_path, cmd_c)
        time.sleep(per_char_sleep)

# def get_screen_size(device_id, adb_path):
#     """Retorna (width, height) do dispositivo via `adb shell wm size` ou None se não conseguir.

#     device_id: adb device id (ex: 'emulator-5554' ou '127.0.0.1:5555')
#     adb_path: caminho para adb a usar
#     """
#     try:
#         out = run_adb_command(adb_path, f'-s "{device_id}" shell wm size')
#         if not out:
#             return None
#         m = re.search(r'(\d+)x(\d+)', out)
#         if m:
#             return int(m.group(1)), int(m.group(2))
#     except Exception:
#         pass
#     return None

def get_screen_size(device_id, adb_path):
    """
    Pega dimensões da tela ATUAL corrigindo para orientação padrão (paisagem).
    Retorna SEMPRE (largura, altura) na orientação landscape.
    """
    # cmd = ["adb"]
    # if device_id:
    #     cmd.extend(["-s", device_id])
    # cmd.extend(["shell", "wm", "size"])
    
    try:
        # result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # output = result.stdout.strip()
        output = run_adb_command(adb_path, f'-s "{device_id}" shell wm size')
        
        # Pega Override size (prioridade)
        override_match = re.search(r'Override size:\s*(\d+)x(\d+)', output)
        if override_match:
            w, h = int(override_match.group(1)), int(override_match.group(2))
        else:
            # Fallback Physical
            physical_match = re.search(r'Physical size:\s*(\d+)x(\d+)', output)
            if not physical_match:
                raise ValueError("Não encontrou size na saída")
            w, h = int(physical_match.group(1)), int(physical_match.group(2))
        
        # CORREÇÃO DE ORIENTAÇÃO: garante landscape (largura >= altura)
        if w < h:
            w, h = h, w  # Swap se estiver em portrait
        
        return w, h
        
    except Exception as e:
        print(f"Erro: {e}")
        return None

def get_orientation(device_id=None):
    cmd = ["adb", "-s", device_id, "shell", "dumpsys", "window", "|", "grep", "mRotation"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except:
        return None

# New: verifica se um pacote Android está rodando no dispositivo
def is_app_running(device_id, adb_path, package_name):
    """Retorna True se o app com package_name estiver rodando no dispositivo.

    Estratégia:
    - Tenta usar `pidof <package>` (disponível em muitos dispositivos modernos).
    - Se pidof não retornar, faz fallback para `ps | grep <package>`.

    Retorna: (bool) True se o processo foi encontrado, False caso contrário.
    """
    try:
        # Tenta pidof primeiro
        out = run_adb_command(adb_path, f'-s "{device_id}" shell pidof {package_name}')
        if out and out.strip():
            if VERBOSE:
                print(f"[ADB] is_app_running(pidof) -> {package_name}: {out.strip()}")
            return True

        # Fallback: ps | grep (o pipe é executado localmente, funciona para a verificação)
        out = run_adb_command(adb_path, f'-s "{device_id}" shell ps | findstr {package_name}')
        # use findstr no Windows local shell; se estiver em *nix, grep seria usado
        if out and package_name in out:
            if VERBOSE:
                print(f"[ADB] is_app_running(ps) -> {package_name}: {out.strip()}")
            return True

    except Exception as e:
        if VERBOSE:
            print(f"[ADB] is_app_running error: {e}")

    return False

def is_app_in_foreground(device_id, adb_path, package_name):
    """Retorna True se o app com package_name estiver visível em primeiro plano.

    Estratégia:
    - Consulta vários dumpsys (window, activity) que contém informações sobre a
      activity/focus atual. Alguns dispositivos usam diferentes chaves (mCurrentFocus,
      mFocusedApp, mResumedActivity, etc), por isso tentamos várias consultas.
    - Para compatibilidade com o ambiente Windows onde este script roda, usamos
      `findstr` como filtro local (mesma técnica usada em is_app_running).

    Observação: o comando `adb shell dumpsys ... | findstr ...` usa o pipe no
    lado do host; run_adb_command aceita essa construção.
    """
    probes = [
        # f'-s "{device_id}" shell dumpsys window windows | findstr mCurrentFocus',
        # f'-s "{device_id}" shell dumpsys window | findstr mCurrentFocus',
        f'-s "{device_id}" shell dumpsys activity activities | findstr mResumedActivity'
        # ,
        # f'-s "{device_id}" shell dumpsys activity activities | findstr mFocusedActivity',
        # f'-s "{device_id}" shell dumpsys activity top'
    ]

    try:
        for probe in probes:
            out = run_adb_command(adb_path, probe)
            if not out:
                continue
            if VERBOSE:
                print(f"[ADB] is_app_in_foreground probe -> {probe}\n    -> {out.strip()}")
            if package_name in out:
                if VERBOSE:
                    print(f"[ADB] is_app_in_foreground: foreground matches {package_name}")
                return True
    except Exception as e:
        if VERBOSE:
            print(f"[ADB] is_app_in_foreground error: {e}")

    return False

def swipe(device_id, adb_path, x1, y1, x2, y2, duration_ms=300):
    """Executa um swipe via ADB (coords absolutos). duration_ms em milissegundos."""
    cmd = f'-s "{device_id}" shell input swipe {x1} {y1} {x2} {y2} {duration_ms}'
    if VERBOSE:
        print(f"[ADB] SWIPE -> {cmd}")
    run_adb_command(adb_path, cmd)


def scroll_vertical(device_id, adb_path, direction='up', percent=0.5, duration_ms=300):
    """Rola a tela verticalmente.

    direction: 'up' ou 'down' (up = arrasta para cima, mostrando conteúdo abaixo)
    percent: quanto da altura deve ser percorrida (0.0-1.0)
    """
    if percent <= 0 or percent > 1:
        raise ValueError('percent deve estar entre 0 (excl) e 1 (inclusivo)')

    size = get_screen_size(device_id, adb_path)
    if not size:
        # fallback em caso de falha em obter tamanho
        print("[ADB] get_screen_size falhou, usando fallback 1280x720")
        w, h = 1280, 720
    else:
        w, h = size

    cx = w // 2
    mid = h // 2
    half = int(h * percent / 2)

    if direction == 'up':
        start_y = min(h - 10, mid + half)
        end_y = max(10, mid - half)
    elif direction == 'down':
        start_y = max(10, mid - half)
        end_y = min(h - 10, mid + half)
    else:
        raise ValueError("direction deve ser 'up' ou 'down'")

    print(f"[ADB] scroll_vertical direction={direction} percent={percent} from ({cx},{start_y}) to ({cx},{end_y}) duration={duration_ms}ms")
    swipe(device_id, adb_path, cx, start_y, cx, end_y, duration_ms)


def scroll_up(device_id, adb_path, percent=0.5, duration_ms=300):
    """Convenience: rola para cima (arrasta para cima, mostrando itens abaixo)."""
    scroll_vertical(device_id, adb_path, 'up', percent, duration_ms)


def scroll_down(device_id, adb_path, percent=0.5, duration_ms=300):
    """Convenience: rola para baixo (arrasta para baixo, mostrando itens acima)."""
    scroll_vertical(device_id, adb_path, 'down', percent, duration_ms)

def capturar_xywh(device_id, x, y, w, h):
    # Captura região específica para minimizar dados
    cmd = f'adb -s {device_id} exec-out screencap -p | convert - -crop {w}x{h}+{x}+{y} - regiao.png'
    Popen(cmd, shell=True).wait()  # Use ImageMagick para crop se instalado
    return cv2.imread('regiao.png', cv2.IMREAD_GRAYSCALE)

def capturar_xyxy(device_id, x1, y1, x2, y2):
    """
    Captura região definida por canto superior esquerdo (x1,y1) e inferior direito (x2,y2).
    Calcula largura e altura automaticamente.
    """
    x = min(x1, x2)  # Canto superior esquerdo
    y = min(y1, y2)

    w = abs(x2 - x1)
    h = abs(y2 - y1)
    return capturar_xywh(device_id, x, y, w, h)

def capturar_tela(device_id):
    """Captura tela inteira direto na RAM (rápido, sem disco)"""
    proc = Popen(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], 
                 stdout=PIPE, stderr=PIPE)
    imagem_bytes, erro = proc.communicate()
    
    if erro:
        print(f"Erro ADB: {erro.decode()}")
        return None

    nparr = numpy.frombuffer(imagem_bytes, numpy.uint8)
    # tela = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    tela = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if tela is None:
        print("Falha ao decodificar imagem!")
        return None
    
    return tela

def capturar_retangulo(device_id, x1, y1, x2, y2):
    """Captura região: full tela -> crop em Python (sem ImageMagick)"""
    tela_full = capturar_tela(device_id)
    if tela_full is None:
        return None
    
    x, y = min(x1, x2), min(y1, y2)
    w, h = abs(x2 - x1), abs(y2 - y1)
    
    # Crop em Python (rápido!)
    regiao = tela_full[y:y+h, x:x+w]
    return regiao

def match_template(imagem_tela, template_path, threshold=0.8):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    # template = template_path
    # template = cv2.imread(template_path)
    resultado = cv2.matchTemplate(imagem_tela, template, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where(resultado >= threshold)
    if len(loc[0]) > 0:
        return True, loc  # Popup detectado, retorna posição para clicar
    return False, None

if __name__ == "__main__":
    _target = "ldplayer"
    # _target = "bluestacks"
    devices = list_devices(_target)
    for device in devices:
        print(f"Dispositivo: {device['display_name']} ({device['id']}) [{device['type']}]")
        # start_app(device['id'], device['adb_path'], 'com.tap4fun.ape.gplay')
        # press_back_esc(device['id'], device['adb_path'])
        # swipe(device['id'], device['adb_path'], 1228, 504, 1228, 175)
        # if is_app_running(device['id'], device['adb_path'], 'com.tap4fun.ape.gplay'):
        #     print(f"O jogo está rodando em {device['display_name']} ({device['id']}).")
        # else:
        #     print(f"O jogo NÃO está rodando em {device['display_name']} ({device['id']}).")
        
        # if is_app_in_foreground(device['id'], device['adb_path'], 'com.tap4fun.ape.gplay'):
        #     print(f"O jogo está em primeiro plano em {device['display_name']} ({device['id']}).")
        # else:
        #     print(f"O jogo NÃO está em primeiro plano em {device['display_name']} ({device['id']}).")

        # if device['id'] == '192.168.1.179:5555' or device['id'] == 'emulator-5568':
        if device['id'] == 'emulator-5570':
            print("Executando ações de cura para o smartphone...")
            # template_raw  = capturar_xywh(device['id'], 8, 600, 104, 700)
            # template_raw  = capturar_tela(device['id'])
            _medical_station_claim_button_coords = (565, 476, 684, 522)
            _retry_button_innitial_coords = (653, 378)
            _retry_button_coords = (*_retry_button_innitial_coords, _retry_button_innitial_coords[0]+214, _retry_button_innitial_coords[1]+83)

            _element_coords = _retry_button_coords
            template_raw  = capturar_retangulo(device['id'], *_element_coords)

            # Salva como template limpo (grayscale pra matching rápido)
            # template_raw = cv2.cvtColor(template_raw, cv2.COLOR_BGR2GRAY)
            # cv2.imwrite('medical_station_claim_button.png', template_raw)
            cv2.imwrite('retry_button.png', template_raw)
            print(f"Template 'retry_button.png' salvo! Use no detectar_popup. [{_element_coords}]")

            # match_found, locations = match_template(template_raw, 'medical_station_claim_button.png')

            # if match_found:
            #     print(f"Image match in {device['display_name']}! Locations: {locations}")

        # _orientation = get_orientation(device['id'])
        # print(f"Orientation for {device['display_name']}: {_orientation}")

        # print(f"Screen dimensions for {device['display_name']}: {get_screen_size(device['id'], device['adb_path'])}")