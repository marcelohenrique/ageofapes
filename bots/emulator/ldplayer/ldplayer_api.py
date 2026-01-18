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

def is_instance_ready(instance_name=None, adb_serial=None, timeout=120, interval=2, adb_path=None):
    """
    Espera até que a instância do emulador esteja pronta (boot completo).
    Agora usa o device name (ex: 'emulator-5554') quando possível em vez do host:port.
    - instance_name: nome da instância no LDPlayer (ex: "Minion04"). Opcional se adb_serial fornecido.
    - adb_serial: serial do adb (ex: '127.0.0.1:5555'). Se fornecido, será usado para conectar, mas as verificações usarão
      o device name retornado por get_emulator_device_name() se disponível.
    - timeout: tempo máximo em segundos para aguardar.
    - interval: intervalo entre tentativas em segundos.
    - adb_path: caminho para adb (opcional). Se None, será procurado no PATH.
    Retorna True se pronto, False se timeout ou erro ao resolver serial/device name.
    """
    adb_path = adb_path or _find_adb_executable()

    # tenta resolver adb_serial a partir do nome da instância (ldconsole) se necessário
    if not adb_serial and instance_name:
        adb_serial = _get_adb_serial_from_ldconsole(instance_name)
        # se não conseguiu resolver o host:port, ainda tentaremos obter o device name diretamente
        # (por exemplo, se ldconsole não reporta host:port corretamente)
    
    # tenta obter o device name (emulator-XXXX) que aparece em `adb devices`
    device_name = None
    try:
        device_name = get_emulator_device_name(instance_name=instance_name, adb_serial=adb_serial, adb_path=adb_path, timeout=10, interval=1)
    except Exception:
        device_name = None

    # se não obteve nem adb_serial nem device_name, não é possível prosseguir
    if not adb_serial and not device_name:
        raise ValueError("É necessário fornecer adb_serial ou instance_name para determinar o dispositivo ADB.")

    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            # se temos adb_serial, garante conexão (silenciosa) para expor o device no `adb devices`
            if adb_serial:
                subprocess.run([adb_path, "connect", adb_serial], capture_output=True, text=True, timeout=5)

            # escolhe o identificador para as chamadas adb: prefere device_name (emulator-XXXX)
            target = device_name or adb_serial

            # Verifica propriedade sys.boot_completed usando o identificador escolhido
            proc = subprocess.run([adb_path, "-s", target, "shell", "getprop", "sys.boot_completed"],
                                  capture_output=True, text=True, timeout=5)
            output = (proc.stdout or "").strip()
            if output == "1":
                return True

            # Algumas ROMs podem usar init.svc.bootanim => verificar alternativa
            proc2 = subprocess.run([adb_path, "-s", target, "shell", "getprop", "init.svc.bootanim"],
                                   capture_output=True, text=True, timeout=5)
            if (proc2.stdout or "").strip() in ("stopped", "0"):
                return True

            # se ainda não temos device_name, tenta resolver novamente (pode aparecer após connect)
            if not device_name:
                try:
                    device_name = get_emulator_device_name(instance_name=instance_name, adb_serial=adb_serial, adb_path=adb_path, timeout=1, interval=0.5)
                    if device_name:
                        # atualiza target para próximas iterações
                        target = device_name
                except Exception:
                    pass

        except Exception:
            # ignora erros transitórios e tenta novamente até timeout
            pass

        time.sleep(interval)

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
    start_ldplayer_instance_by_name("Minion04")
    if is_instance_ready(instance_name="Minion04"):
        print("Emulator is ready!")
    # stop_all_ldplayer_instances()

    # print(_get_adb_serial_from_ldconsole("Minion04"))
    # print(get_emulator_device_name(instance_name="Minion04"))