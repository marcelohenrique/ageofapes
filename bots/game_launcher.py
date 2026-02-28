import time
import aoa_actions
import emulator_api
from emulator.ldplayer import ldplayer_api
import manage_adb_daemons

LDPLAYER_INSTANCES = ["Minion04", "Minion05", "Minion06"]

def start_emulators():
    print(f'[{time.strftime("%H:%M:%S")}] Starting LDPlayer ADB daemon...')
    manage_adb_daemons.start("ldplayer")
    for _instance_name in LDPLAYER_INSTANCES:
        print(f'[{_instance_name}] Starting LDPlayer instance...')
        ldplayer_api.start_ldplayer_instance_by_name(_instance_name)
        if ldplayer_api.is_instance_ready(instance_name=_instance_name):
            print(f"[{_instance_name}] Emulator is ready!")
    
    time.sleep(2)  # Wait a bit before listing devices

def start_game(devices):
    for device in devices:
        print(f"Dispositivo: {device['display_name']} ({device['id']}) [{device['type']}]")
        emulator_api.start_app(device['id'], device['adb_path'], 'com.tap4fun.ape.gplay')

    time.sleep(600)  # Wait a bit before performing actions

def run_aoa(devices):
    # Press back and help button multiple times to avoid popups
    for device in devices:
        for i in range(5):
            aoa_actions.press_help_button(device['id'], device['adb_path'])
            time.sleep(2)
            # emulator_api.press_back_esc(device['id'], device['adb_path'])
            # time.sleep(2)

    for device in devices:
        aoa_actions.press_map_city_button(device['id'], device['adb_path'])
        time.sleep(2)
    
    # Get gang gifts
    # get_gang_gifts(devices)

    # heal troops, if needed

    # run convoy missions

    # Gang donations, take care about resources needed

    # Use all stocked action points
    # for device in devices:
    #     aoa_actions.use_action_points(device['id'], device['adb_path'])
    
    # Figure out a way to develop gang research automatically

    # monitor.main()

def get_gang_gifts(devices):
    for device in devices:
        aoa_actions.get_gang_gifts(device['id'], device['adb_path'])
        time.sleep(1)

if __name__ == "__main__":
    # start_emulators()
    devices = emulator_api.list_devices(target='bluestacks')
    # start_game(devices)
    run_aoa(devices)