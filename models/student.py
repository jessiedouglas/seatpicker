from google.appengine.ext import ndb

class Student(ndb.Model):
    name = ndb.StringProperty()
    already_paired = ndb.KeyProperty(kind="Student", repeated=True)
    rows = ndb.IntegerProperty(repeated=True)