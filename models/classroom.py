from google.appengine.ext import ndb

class Classroom(ndb.Model):
    name = ndb.StringProperty()
    seating_arrangements = ndb.KeyProperty(kind="SeatingArrangement", repeated=True)
