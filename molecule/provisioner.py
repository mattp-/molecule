#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os

import jinja2

from molecule import ansible_playbook
from molecule import util


class Ansible(object):
    def __init__(self, config):
        """
        Sets up the Ansible provisioner requirements and returns None.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config
        self._setup()

    @property
    def default_options(self):
        d = {}
        if self._config.args.get('debug'):
            d['debug'] = True

        return d

    @property
    def name(self):
        return self._config.config['provisioner']['name']

    @property
    def options(self):
        return self._config.merge_dicts(
            self.default_options,
            self._config.config['provisioner']['options'])

    @property
    def inventory(self):
        return self._config.driver.inventory

    @property
    def inventory_file(self):
        return os.path.join(self._config.ephemeral_directory,
                            'ansible_inventory')

    @property
    def config_file(self):
        return os.path.join(self._config.ephemeral_directory, 'ansible.cfg')

    def converge(self, inventory, playbook):
        """
        TODO ... and returns None.

        :return: None
        """
        apb = ansible_playbook.AnsiblePlaybook(inventory, playbook,
                                               self._config)
        apb.execute()

    def write_inventory(self):
        self._verify_inventory()

        template = jinja2.Environment().from_string(
            self._get_inventory_template()).render(
                host_data=self.inventory,
                groups_data=self._config.platform_groups)
        with open(self.inventory_file, 'w') as f:
            f.write(template)

    def write_config(self):
        # self._verify_config()

        template = jinja2.Environment().from_string(self._get_config_template(
        )).render()
        with open(self.config_file, 'w') as f:
            f.write(template)

    def _setup(self):
        temp_directory = os.path.dirname(self.inventory_file)
        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)

    def _verify_inventory(self):
        if not self.inventory:
            msg = ("Instances missing from the 'platform' "
                   "section of molecule.yml.")
            util.print_error(msg)
            util.sysexit()

    def _get_inventory_template(self):
        return """
# Molecule managed

{% for k, v in host_data.iteritems() -%}
{{ k }} {{ v|join(' ') }}
{% endfor -%}

{% for k, v in groups_data.iteritems() %}
[{{ k }}]
{{ v|join('\n') }}
{% endfor -%}
""".strip()

    def _get_config_template(self):
        return """
# Molecule managed

[defaults]

roles_path = ../../../../
ansible_managed = Ansible managed: Do NOT edit this file manually!
retry_files_enabled = False
"""