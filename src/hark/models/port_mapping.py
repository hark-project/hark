from hark.models import SQLModel


class PortMapping(SQLModel):
    table = 'port_mapping'
    key = 'host_port'

    fields = ['host_port', 'guest_port', 'machine_id', 'name']
    required = ['host_port', 'guest_port', 'machine_id', 'name']

    def format_virtualbox(self):
        return '%s,tcp,127.0.0.1,%d,,%d' % (
            self['name'], self['host_port'], self['guest_port'])
