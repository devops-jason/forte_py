import yaml
from yaml.loader import SafeLoader

import socket
import platform
import uuid

class ForteMessage():
    def __init__(self):
        self._data = {}
        self._data['source_hostname'] = socket.gethostname()
        self._data['source_system'] = platform.system()
        self._data['forte_uuid'] = str(uuid.uuid4())
        self._data['reply_uuid'] = ''
        self._data['forte_command'] = ''
        self._data['forte_variables'] = {}
        self._data['reply_data'] = {'output': ''}

    def set_reply_uuid(self, reply_uuid):
        ruuid = uuid.UUID(reply_uuid)
        self._data['reply_uuid'] = str(ruuid)

    def set_forte_command(self, command = 'ping'):
        self._data['forte_command'] = command

    def set_forte_variables(self, variables = {} ):
        if type(variables) is dict:
            self._data['forte_variables'] = variables
        else:
            print('forte_variables is not of type dict.')

    def load_yaml(self, yaml_message):
        if type(yaml_message) is str:
            self._data = yaml.load(yaml_message, Loader=SafeLoader)
        else:
            print('Unable to load yaml_message.')

    def dump_yaml(self):
        return yaml.dump(self._data)
    
    def get_forte_command(self):
        return self._data['forte_command']
    
    def get_forte_variables(self):
        return self._data['forte_variables']

    def get_forte_hostname(self):
        return self._data['source_hostname']

    def get_forte_uuid(self):
        return self._data['forte_uuid']

    def get_reply_uuid(self):
        return self._data['reply_uuid']

    def get_reply_data(self):
        return self._data['reply_data']
    
    def set_reply_data(self, data):
        self._data['reply_data']['output'] = data
    
 
    

