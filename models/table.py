from google.appengine.ext import ndb

class Table(ndb.Model):
    students = ndb.KeyProperty(kind="Student", repeated=True)
