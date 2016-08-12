from hark.models import SQLModel


class NetworkInterface(SQLModel):
    table = 'network_interface'
    key = ['machine_id', 'kind']

    fields = ['machine_id', 'kind', 'addr']
