from __future__ import print_function
import json
import os
import click
import sh
from sh import xcrun
from pydash import py_

from simulatorcc import device_status
from simulatorcc.device_status import running_devices

fbsimctl = sh.Command(os.path.join(os.path.expanduser("~"),'git','github','FBSimulatorControl','release','fbsimctl'))


@click.group(chain=True)
def cli():
    pass


@cli.command()
@click.option('--device-id', '-id', required=False, help='deviceId')
@click.option('--device-type', '-t', required=False, help='device type (iPhone 5, iPhone 5s, etc.')
@click.option('--device-os', '-os', required=False, help='device os (iOS 9.2, iOS 9.3, etc.')
def start(device_id, device_type, device_os):

    simulators = get_simulators(device_type, device_os)
    for simulator in simulators:
        start_device(simulator['udid'])


def start_device(udid):
    try:
        print("starting up {}".format(udid))
        output = fbsimctl(udid, "boot")
        print(output)
        if output.exit_code == 0:
            device_status.add(udid)
        else:
            print(output.stderr)
            # exit(1)
    except sh.ErrorReturnCode_1 as ex:
        print(ex.stdout.decode('ascii'))
        # exit(1)


@cli.command()
@click.option('--all', '-a', is_flag=True, default=False, help='run in all devices in this context')
@click.option('--device-id', '-id', help='device id')
@click.option('--app_path', '-p', required=True, help='app file path')
def install(all, device_id, app_path):
    if all:
        for device_id in running_devices:
            print(xcrun.simctl('install', device_id, app_path))
    else:
        print(xcrun.simctl('install', device_id, app_path))


@cli.command()
@click.option('--all', '-a', is_flag=True, default=False, help='run in all devices in this context')
@click.option('--device-id', '-id', required=False, help='device id')
@click.option('--bundle_id', '-b', required=True, help='bundle identifier')
def uninstall(all, device_id, bundle_id):
    if all:
        for device_id in running_devices:
            print(xcrun.simctl('uninstall', device_id, bundle_id))
    else:
        print(xcrun.simctl('uninstall', device_id, bundle_id))



@cli.command()
@click.option('--all', '-a', is_flag=True, default=False, help='run in all devices in this context')
@click.option('--device-id', '-id', required=False, help='device id')
def shutdown(all, device_id):
    if all:
        print('shuttingdown all: {}'.format(running_devices))
        running_devices_tmp = list(running_devices)
        for device_id in running_devices_tmp:
            print(shutdown_device(device_id))
    else:
        print(shutdown_device(device_id))


def shutdown_device(udid):
    print("shutting down {}".format(udid))
    print(fbsimctl(udid, "shutdown"))
    device_status.remove(udid)

def get_simulators(name_filter='iPhone', os_filter='iOS'):
    output = xcrun.simctl('list', '-j')
    json_output = json.loads(output.stdout.decode('ascii'))

    devices = json_output['devices']
    device_list = []
    for os, list in devices.items():
        device_list.extend(py_.map(list, lambda element: py_.extend({}, element, {'os': os})))
    device_list = py_.filter(device_list, lambda x: os_filter in x['os'])
    device_list = py_.filter(device_list, lambda x: name_filter in x['name'])
    device_list = py_.filter(device_list, {'availability': '(available)'})
    return device_list


def is_booted(device_id):
    simulators = get_simulators()
    py_.filter(simulators, {'state': 'Booted', 'udid': device_id})


def is_shutdown(device_id):
    simulators = get_simulators()
    py_.filter(simulators, {'state': 'Shutdown', 'udid': device_id})


if __name__ == "__main__":
    cli()
