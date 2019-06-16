from google.appengine.ext import ndb

class SeatingArrangement(ndb.Model):
    day = ndb.IntegerProperty()
    classroom = ndb.KeyProperty(kind="Classroom")
    tables = ndb.KeyProperty(kind="Table", repeated=True)
    # deprecated
    students = ndb.KeyProperty(kind="Student", repeated=True)
