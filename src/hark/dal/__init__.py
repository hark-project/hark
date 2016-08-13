import os
import sqlite3

from hark.exceptions import (
    InvalidQueryConstraint,
    DuplicateModelException
)
import hark.log


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

    def _format_constraints(self, constraints):
        formatted = []

        for k, v in constraints.items():
            if isinstance(v, int):
                s = "%s = %d" % (k, v)
                formatted.append(s)
            elif isinstance(v, str):
                s = "%s = '%s'" % (k, v)
                formatted.append(s)
            elif v is None:
                s = "%s is null" % k
                formatted.append(s)
            else:
                raise InvalidQueryConstraint("Unsupported value: %s" % v)

        return formatted

    def _read_query(self, cls, constraints=None):
        tmpl = "SELECT %s FROM %s%s;"
        fields = ", ".join(cls.fields)
        if constraints is not None and len(constraints) > 0:
            formatted = self._format_constraints(constraints)
            cons_str = ' WHERE ' + " AND ".join(formatted)
        else:
            cons_str = ''

        return tmpl % (fields, cls.table, cons_str)

    def _insert_query(self, model):
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

    def _delete_query(self, ins):
        constraints = self._key_constraints(ins)

        return self._delete_where_query(ins.__class__, constraints)

    def _delete_where_query(self, cls, constraints):
        tmpl = "DELETE FROM %s WHERE %s;"

        formatted = self._format_constraints(constraints)
        cons_str = " AND ".join(formatted)

        return tmpl % (cls.table, cons_str)

    def _key_constraints(self, ins):
        """
        Given a model instance, return a constraints dictionary that should
        uniquely identify it in the database.
        """
        if isinstance(ins.key, str):
            keys = [ins.key]
        else:
            keys = ins.key

        return {k: ins[k] for k in keys}

    def _setup(self):
        "Set up the schema"
        hark.log.info("Setting up DB schema: %s", self.path)
        self._db.executescript(hark_schema())
        self._db.commit()

    def create(self, ins):
        "Insert a model instance"
        query, bindings = self._insert_query(ins)
        try:
            self._db.execute(query, bindings)
            self._db.commit()
        except sqlite3.IntegrityError as e:
            raise DuplicateModelException(ins)

    def read(self, cls, constraints=None):
        """
        Given a class and a set of constraints that should uniquely
        identify a row in the database, create an instance of this
        class.
        """
        qr = self._read_query(cls, constraints=constraints)
        cur = self._db.execute(qr)

        return [cls.from_sql_row(row) for row in cur]

    def delete(self, ins):
        """
        Delete an instance of a model from the DB.
        """
        qr = self._delete_query(ins)
        self._db.execute(qr)
        self._db.commit()

    def deleteWhere(self, cls, constraints):
        """
        Given a class and a set of constraints, delete rows from the table
        associated with this class.
        """
        qr = self._delete_where_query(cls, constraints)
        self._db.execute(qr)
        self._db.commit()


class InMemoryDAL(DAL):
    def __init__(self):
        return DAL.__init__(self, ":memory:")
