from hark.models import SQLModel


class Config(SQLModel):
    """
    A model for an arbitrary config value that is stored to the database.
    """

    table = 'config'
    key = ['name', 'value']

    fields = ['name', 'value']
    required = ['name', 'value']
