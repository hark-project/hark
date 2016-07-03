import os
import sqlite3
from typing import Any, Dict, List

from hark.exceptions import (
        InvalidQueryConstraint,
        DuplicateModelException
)
from hark.models import (
    SQLModel
)


def hark_schema():
    schemaFile = 'schema.sql'
    dir = os.path.dirname(__file__)
    p = os.path.join(dir, schemaFile)
    with open(p, 'r') as f:
        return f.read()


class DAL(object):
    """
    An sqlite3 database connection which is capable of mapping rows to
    model instances and vice versa.
    """

    def __init__(self, path):
        self.path = path
        self._connect()

    def _connect(self):
        if os.path.exists(self.path):
            initialized = True
        else:
            initialized = False

        self._db = sqlite3.connect(self.path)

        if not initialized:
            self._setup()

    def _format_constraints(self, constraints: Dict[str, Any]) -> List[str]:
        formatted = []

        for k, v in constraints.items():
            if isinstance(v, int):
                s = "%s = %d" % (k, v)
                formatted.append(s)
            elif isinstance(v, str):
                s = "%s = '%s'" % (k, v)
                formatted.append(s)
            else:
                raise InvalidQueryConstraint("Unsupported value: %s" % v)

        return formatted

    def _read_query(self, cls, constraints=None) -> str:
        tmpl = "SELECT %s FROM %s%s;"
        fields = ", ".join(cls.fields)
        if constraints is not None:
            formatted = self._format_constraints(constraints)
            cons_str = ' WHERE ' + " AND ".join(formatted)
        else:
            cons_str = ''

        return tmpl % (fields, cls.table, cons_str)

    def _insert_query(self, model: SQLModel) -> str:
        tmpl = "INSERT INTO {} ({}) VALUES ({});"

        fields = []
        bindings = []
        placeholders = []

        for k in model.fields:
            fields.append(k)
            bindings.append(model[k])
            placeholders.append("?")

        query = tmpl.format(
            model.table,
            ", ".join(fields),
            ", ".join(placeholders),
        )
        return (query, bindings)

    def _setup(self) -> None:
        "Set up the schema"
        self._db.execute(hark_schema())
        self._db.commit()

    def create(self, ins: SQLModel) -> None:
        "Insert a model instance"
        query, bindings = self._insert_query(ins)
        try:
            self._db.execute(query, bindings)
            self._db.commit()
        except sqlite3.IntegrityError as e:
            raise DuplicateModelException(ins)

    def read(
            self, cls,
            constraints: Dict[str, Any]=None) -> List[SQLModel]:
        """
        Given a class and a set of constraints that should uniquely
        identify a row in the database, create an instance of this
        class.
        """
        qr = self._read_query(cls, constraints=constraints)
        cur = self._db.execute(qr)

        return [cls.from_sql_row(row) for row in cur]


class InMemoryDAL(DAL):
    def __init__(self):
        return DAL.__init__(self, ":memory:")
