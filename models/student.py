from google.appengine.ext import ndb

class Student(ndb.Model):
    name = ndb.StringProperty()