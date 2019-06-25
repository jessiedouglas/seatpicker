from google.appengine.ext import ndb

class Student(ndb.Model):
    name = ndb.StringProperty()
    already_paired = ndb.KeyProperty(kind="Student", repeated=True)
    classroom = ndb.KeyProperty(kind="Classroom")
    # deprecated
    columns = ndb.FloatProperty(repeated=True)
