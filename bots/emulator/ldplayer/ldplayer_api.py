import subprocess
import time
import shutil
import re

LDCONSOLE_PATH = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"

def check_ldplayer_running():
    """Check if LDPlayer is running."""
    # Implement logic to check if LDPlayer is running
    pass

def start_ldplayer_instance(instance_id):
    """Start a specific instance of LDPlayer."""
    # Implement logic to start a specific LDPlayer instance
    pass

def start_ldplayer_instance_by_name(instance_name):
    """Start a specific instance of LDPlayer."""
    # command = f'"C:\\LDPlayer\\LDPlayer9\\ldconsole.exe" launch --name {instance_name}'  # Adjust the path as necessary
    print(f"Starting emulator {instance_name}...")
    # subprocess.Popen(command, shell=True)
    subprocess.run([LDCONSOLE_PATH, "launch", "--name", instance_name])
    # time.sleep(5)  # Wait for the emulator to start

def _find_adb_executable():
    """Return path to adb executable (or 'adb' if not found explicitly)."""
    return shutil.which("adb") or "adb"

def _get_adb_serial_from_ldconsole(instance_name):
    """
    Try to extract the adb serial (host:port) for an LDPlayer instance using ldconsole list2 output.
    This is heuristic: ldconsole output formats can vary, so adjust parsing if needed.
    Returns the adb serial string (e.g. '127.0.0.1:5555') or None if not found.
    """
    try:
        proc = subprocess.run([LDCONSOLE_PATH, "list2"], capture_output=True, text=True, timeout=5)
    except Exception:
        return None

    out = proc.stdout or proc.stderr or ""
    # Look for a line that contains the instance name and an IP:PORT or port number
    for line in out.splitlines():
        if instance_name.lower() in line.lower():
            # try to find an IP:PORT first
            m = re.search(r'(\d{1,3}(?:\.\d{1,3}){3}:\d{2,5})', line)
            if m:
                return m.group(1)
            # fallback: find a port and assume localhost
            m = re.search(r'(:?\b)(\d{4,5})\b', line)
            if m:
                return f"127.0.0.1:{m.group(2)}"
    # fallback: search globally for any 127.0.0.1:PORT associated with name in entire output
    m = re.search(rf'{re.escape(instance_name)}.*?(\d{{1,3}}(?:\.\d{{1,3}}){{3}}:\d{{2,5}})', out, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1)
    return None

def is_instance_ready(instance_name=None, timeout=120, interval=2):
    """
    Verifica se a instância LDPlayer está pronta lendo a saída de `ldconsole list2`.

    A saída contém colunas: index, name, top_window_hwnd, bind_window_hwnd, status, pid, vbox_pid
    A função procura pela linha correspondente a `instance_name` e considera pronta quando
    a coluna `status` for '1'.

    Parâmetros:
    - instance_name: nome da instância LDPlayer (obrigatório)
    - timeout: tempo máximo em segundos para aguardar
    - interval: intervalo entre tentativas em segundos

    Retorna True se status == '1' dentro do timeout, False caso contrário.
    """
    if not instance_name:
        raise ValueError("instance_name é obrigatório para verificar readiness via ldconsole")

    start_time = time.time()
    end_time = start_time + timeout
    attempt = 0

    while time.time() < end_time:
        attempt += 1
        time_left = int(end_time - time.time())
        print(f"[is_instance_ready] attempt={attempt} instance='{instance_name}' time_left={time_left}s")
        try:
            proc = subprocess.run([LDCONSOLE_PATH, "list2"], capture_output=True, text=True, timeout=5)
            out = proc.stdout or proc.stderr or ""

            # print a short preview of the output for debugging
            preview = out.strip()[:1000]
            print(f"[is_instance_ready] ldconsole output preview (first 1000 chars):\n{preview}\n--- end preview ---")

            found = False
            for lineno, line in enumerate(out.splitlines(), start=1):
                raw = line.rstrip()
                if not raw:
                    continue
                # split em colunas por espaços em branco; nome geralmente fica na segunda coluna
                parts = re.split(r',', raw)
                print(f"[is_instance_ready] line {lineno}: parts={parts}")
                if len(parts) < 2:
                    continue
                # coluna 1 = index, 2 = name, 5 = status (0-based: parts[1], parts[4])
                name_col = parts[1]
                status_col = parts[4] if len(parts) > 4 else "0"

                # compara nomes (case-insensitive). permite correspondência parcial também.
                if instance_name.lower() == name_col.lower() or instance_name.lower() in name_col.lower():
                    print(f"[is_instance_ready] matched line {lineno}: name_col='{name_col}' status_col='{status_col}'")
                    found = True
                    if status_col == "1":
                        print(f"[is_instance_ready] instance '{instance_name}' ready=True")
                        return True
                    else:
                        print(f"[is_instance_ready] instance '{instance_name}' matched but not ready (status={status_col}); will continue waiting")
                        # stop scanning other lines this iteration and wait for next attempt
                        break

            if not found:
                print(f"[is_instance_ready] instance '{instance_name}' not found in ldconsole output (attempt {attempt})")

        except Exception as e:
            print(f"[is_instance_ready] exception on attempt {attempt}: {e}")

        time.sleep(interval)

    print(f"[is_instance_ready] timeout after {attempt} attempts; instance '{instance_name}' not ready")
    return False

def stop_ldplayer_instance(instance_id):
    """Stop a specific instance of LDPlayer."""
    # Implement logic to stop a specific LDPlayer instance
    pass

def stop_all_ldplayer_instances():
    """Stop all running LDPlayer instances."""
    subprocess.run([LDCONSOLE_PATH, "quitall"])
    pass

def get_running_instances():
    """Get a list of currently running LDPlayer instances."""
    # Implement logic to retrieve running instances
    pass

def launch_ldplayer_instances(num_instances):
    """Launch the specified number of LDPlayer instances."""
    for i in range(num_instances):
        start_ldplayer_instance(i)  # Adjust as necessary for instance management

def shutdown_ldplayer_instances():
    """Shutdown all running LDPlayer instances."""
    instances = get_running_instances()
    for instance in instances:
        stop_ldplayer_instance(instance)

def get_emulator_device_name(instance_name=None, adb_serial=None, adb_path=None, timeout=30, interval=1):
    """
    Tenta retornar o device name exibido por `adb devices` (ex: 'emulator-5554') para a instância LDPlayer.
    Estrategia:
     - resolve adb_serial via ldconsole (se instance_name fornecido);
     - conecta via adb ao host:port;
     - consulta propriedades comuns que costumam conter o serial do emulador (ro.serialno, ro.boot.serialno);
     - se não encontrar, tenta varrer `adb devices` e comparar propriedades que possam identificar o mesmo dispositivo.
    Retorna string do device (ex: 'emulator-5554') ou None se não conseguiu resolver.
    """
    adb_path = adb_path or _find_adb_executable()

    if not adb_serial and instance_name:
        adb_serial = _get_adb_serial_from_ldconsole(instance_name)
        if not adb_serial:
            return None

    if not adb_serial:
        raise ValueError("É necessário fornecer adb_serial ou instance_name.")

    # tenta conectar (silencioso)
    try:
        subprocess.run([adb_path, "connect", adb_serial], capture_output=True, text=True, timeout=5)
    except Exception:
        pass

    end = time.time() + timeout
    while time.time() < end:
        try:
            # tenta propriedades que normalmente armazenam o nome/serial do emulador
            for prop in ("ro.serialno", "ro.boot.serialno", "ro.build.display.id"):
                proc = subprocess.run([adb_path, "-s", adb_serial, "shell", "getprop", prop],
                                      capture_output=True, text=True, timeout=5)
                val = (proc.stdout or "").strip()
                if val and val.startswith("emulator-"):
                    return val

            # fallback: alguns emuladores expõem 'ro.product.name' ou 'ro.product.device'
            for prop in ("ro.product.name", "ro.product.device", "ro.product.model"):
                proc = subprocess.run([adb_path, "-s", adb_serial, "shell", "getprop", prop],
                                      capture_output=True, text=True, timeout=5)
                val = (proc.stdout or "").strip()
                if val and val.startswith("emulator-"):
                    return val

            # fallback mais genérico: varre lista de dispositivos do adb e tenta correlacionar
            proc = subprocess.run([adb_path, "devices"], capture_output=True, text=True, timeout=5)
            out = proc.stdout or ""
            for line in out.splitlines():
                m = re.match(r"^(emulator-\d+)\s+device\b", line)
                if m:
                    candidate = m.group(1)
                    # tenta verificar se esse candidate responde e está 'relacionado' com nosso adb_serial
                    # por exemplo, lê uma propriedade simples para validar que responde
                    try:
                        p2 = subprocess.run([adb_path, "-s", candidate, "shell", "getprop", "ro.serialno"],
                                            capture_output=True, text=True, timeout=3)
                        if p2.returncode == 0:
                            # se respondeu, assume que é o nome desejado
                            return candidate
                    except Exception:
                        pass
        except Exception:
            pass

        time.sleep(interval)

    return None

if __name__ == "__main__":
    # start_ldplayer_instance_by_name("Minion04")
    if is_instance_ready(instance_name="Minion04"):
        print("Emulator is ready!")
    # stop_all_ldplayer_instances()

    # print(_get_adb_serial_from_ldconsole("Minion04"))
    # print(get_emulator_device_name(instance_name="Minion04"))