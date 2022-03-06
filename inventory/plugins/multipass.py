#!/usr/bin/env python3

'''
Custom dynamic inventory script for Ansible, in Python.
'''

from __future__ import absolute_import, division, print_function

import subprocess
import json
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

# TODO: ANSIBLE LOGGING= print('LOADING')
__metaclass__ = type

DOCUMENTATION = r"""
    name: multipass
    plugin_type: inventory
    short_description: Returns Ansible inventory from a multipass host.
    description: Returns Ansible inventory from a multipass host.
    author:
        - Adam Mcchesney (@amacc)
        - Chris Stinemetz (@chrisstinemetz)
    options:
        plugin:
            description: Name of the plugin
            required: true
            choices: ['multipass']
        multipass_server:
            description: Server that is hosting multipass
            default: ''
    extends_documentation_fragment:
    - constructed
"""

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "multipass"

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        # Dont really care as long as its valid by super!
        if super(InventoryModule, self).verify_file(path):
            return True
        return False

    def get_multipass_instances(self, target_host=None):
        try:
            # pipe multipass json list into dictionary
            # TODO: ANSIBLE LOGGING= print("Running Process on", target_host)
            ssh = ['ssh', target_host]
            multipass = ['multipass', 'list', '--format', 'json']
            process = ssh + multipass if target_host else multipass
            # TODO: ANSIBLE LOGGING= print("Running Process", *process)
            result = subprocess.run(process,stdout=subprocess.PIPE)
            return json.loads(result.stdout.decode('utf-8'))['list']
        except Exception as e:
            # TODO: ANSIBLE LOGGING= print(e)
            raise

    def parse(self, inventory, loader, path, cache=True):
        # TODO: ANSIBLE LOGGING= print('Begin Parse: ', inventory, loader, path, cache)

        super(InventoryModule, self).parse(inventory, loader, path, cache)
        config = self._read_config_data(path)
        # TODO: ANSIBLE LOGGING= print('Found Config: ',config)

        instances = self.get_multipass_instances(config['multipass_server'])
        # TODO: ANSIBLE LOGGING= print('Found Instances', instances)

        compose = config['compose']
        is_strict = config.get('strict', True)
        # TODO: ANSIBLE LOGGING= print('Found Instances', instances)

        for instance in instances:
            self.add_host(instance['name'], instance, is_strict, compose)


    def add_host(self, hostname, host_vars, is_strict, compose):
        ''' Adds the instance to the running inventory '''
        # TODO: ANSIBLE LOGGING= print("Adding Host", hostname, host_vars)
        self.inventory.add_host(hostname, group='all')

        for var_name, var_value in host_vars.items():
            self.inventory.set_variable(hostname, var_name, var_value)

        # Add variables created by the user's Jinja2 expressions to the host
        self._set_composite_vars(compose, host_vars, hostname, strict=is_strict
        )

        self._add_host_to_composed_groups(
            self.get_option('groups'),
            host_vars, hostname, strict=is_strict
        )
