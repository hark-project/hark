import collections
import json
from hark.exceptions import (
    ModelInvalidException,
)


class BaseModel(collections.OrderedDict):

    required = []

    def json(self, indent=None):
        return json.dumps(self, indent=indent)

    def validate(self):
        if not hasattr(self, 'fields'):
            raise ModelInvalidException(self, 'Missing fields definition')

        missing = [
            k for k in self.required
            if k not in self
        ]

        if len(missing):
            raise ModelInvalidException(
                self, "Missing required fields: %s" % missing)


class SQLModel(BaseModel):
    """
    A model that can be persisted to and read from the database.
    """

    @classmethod
    def from_sql_row(cls, row):
        """
        Construct an instance of this model from an SQL row.

        Assumes that the select query used the ordering of fields in the model
        definition.
        """
        keyed = collections.OrderedDict()
        for i, k in enumerate(cls.fields):
            keyed[k] = row[i]

        ins = cls(**keyed)
        ins.validate()
        return ins

    def validate(self):
        BaseModel.validate(self)
        for attr in ['table', 'key']:
            if not hasattr(self, attr):
                raise ModelInvalidException(
                    self, "Missing '%s' attribute" % attr)
