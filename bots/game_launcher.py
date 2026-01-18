import emulator_api
from emulator.ldplayer import ldplayer_api
import manage_adb_daemons


if __name__ == "__main__":
    _ldplayer_instances = ["Minion04"] #, "Minion05", "Minion06"]
    print('Starting LDPlayer ADB daemon...')
    manage_adb_daemons.start("ldplayer")
    for _instance_name in _ldplayer_instances:
        print(f'[{_instance_name}] Starting LDPlayer instance...')
        ldplayer_api.start_ldplayer_instance_by_name(_instance_name)
        if ldplayer_api.is_instance_ready(instance_name=_instance_name):
            print(f"[{_instance_name}] Emulator is ready!")
            _device_name = ldplayer_api.get_emulator_device_name(instance_name=_instance_name)
            print(f"[{_instance_name}] Launching Age of Apes game...")
            emulator_api.start_app(_device_name, 'adb', 'com.tap4fun.ape.gplay')