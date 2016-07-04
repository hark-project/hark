import hashlib

from hark.models import SQLModel
from hark.exceptions import InvalidMachineException

MEMORY_MINIMUM = 128


class Machine(SQLModel):
    table = 'machine'
    key = 'machine_id'

    fields = ['machine_id', 'name', 'driver', 'guest', 'memory_mb']
    required = ['machine_id', 'name', 'driver', 'guest', 'memory_mb']

    def validate(self):
        # Use parent validation first
        SQLModel.validate(self)

        if self['memory_mb'] < MEMORY_MINIMUM:
            raise InvalidMachineException("Machine cannot have <128mb memory")

    @classmethod
    def generate_id(cls, **kwargs):
        h = hashlib.sha256()
        for f in cls.fields:
            if f not in kwargs:
                continue
            h.update(f.encode('utf-8'))
            h.update(str(kwargs[f]).encode('utf-8'))
        return h.hexdigest()[:8]

    @classmethod
    def new(cls, **kwargs):
        if 'machine_id' in kwargs:
            raise InvalidMachineException(
                "Cannot specify machine_id for new machine")
        kwargs['machine_id'] = cls.generate_id(**kwargs)
        return cls(**kwargs)
