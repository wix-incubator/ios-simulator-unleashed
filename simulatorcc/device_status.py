import json

UDID_FILE_NAME = 'udid.txt'


def load():
    try:
        with open(UDID_FILE_NAME) as json_file:
            json_data = json.load(json_file)
        return json_data
    except Exception:
            return []


def dump():
    with open(UDID_FILE_NAME, 'w') as outfile:
        json.dump(running_devices, outfile)


def add(udid):
    if udid not in running_devices:
        running_devices.append(udid)
        dump()


def remove(udid):
    if udid in running_devices:
        running_devices.remove(udid)
        dump()

running_devices = load()
