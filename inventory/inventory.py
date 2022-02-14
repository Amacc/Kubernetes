#!/usr/bin/env python3

'''
Custom dynamic inventory script for Ansible, in Python.
'''

import subprocess
import argparse
import json


class MutipassInventory(object):

    def __init__(self):

        self.inventory = \
            {
                'all': {
                    'children': [
                        'server',
                        'master',
                        'workers',
                        'helm',
                        'build'
                    ],
                    'vars': {
                        'ansible_user': 'ubuntu',
                        'ansible_ssh_private_key_file': '~/.ssh/id_rsa',
                        'example_variable': 'value'
                    }
                },
                '_meta': {
                    'hostvars': {
                        '54.83.174.103': {
                            'varnish_host_specific_var': 'foo'
                        },
                    },
                },
            }
        self.read_cli_args()
        self.instances = self.get_multipass_instances()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.multipass_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return empty inventory.
        else:
            self.inventory = self.empty_inventory()
        print(json.dumps(self.inventory))

    # Example inventory for testing.
    def multipass_inventory(self):
        hosts = {}
        for i in self.instances:
            hosts.update({i['name']: {'ansible_host': i['ipv4'][1]}})

        server = {}
        master = {}
        workers_temp = {'workers': {'hosts': []}}
        helm = {}
        build = {}

        if len(self.instances) > 1:
            for i in self.instances[0:1]:
                server.update({'server': {'hosts': [i['ipv4'][1]]}})
                master.update({'master': {'hosts': [i['ipv4'][1]]}})
                helm.update({'helm': {'hosts': [i['ipv4'][1]]}})
                build.update({'build': {'hosts': [i['ipv4'][1]]}})
            workers = workers_temp
            for i in self.instances[1:]:
                workers['workers']['hosts'].append(i['ipv4'][1])
        else:
            for i in self.instances[0:1]:
                master.update({i['name']: None})
            # The others become workers
            for i in self.instances[1:]:
                workers.update({i['name']: None})
            print('Designated first instance as control plane node.')

        # Fill inventory template with parsed values
        self.inventory.update(server)
        self.inventory.update(master)
        self.inventory.update(helm)
        self.inventory.update(build)
        self.inventory.update(workers)

        return self.inventory

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()

    def get_multipass_instances(self):
        try:
            # pipe multipass json list into dictionary
            result = subprocess.run(
                ['multipass', 'list', '--format', 'json'], stdout=subprocess.PIPE).stdout.decode('utf-8')
            result_dict = json.loads(result)
            # filter for k0s instances
            filtered_list = list(
                filter(lambda k: 'node-' in k['name'], result_dict['list']))
            return sorted(filtered_list, key=lambda x: x['name'])
        except Exception as e:
            print(e)


# Get the inventory.
MutipassInventory()
