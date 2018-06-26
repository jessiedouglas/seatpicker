from google.appengine.ext import ndb

class SeatingArrangement(ndb.Model):
    day = ndb.IntegerProperty()
    students = ndb.KeyProperty(kind="Student", repeated=True)
    classroom = ndb.KeyProperty(kind="Classroom")
