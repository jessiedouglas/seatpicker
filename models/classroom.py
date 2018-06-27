from google.appengine.ext import ndb

class Classroom(ndb.Model):
    name = ndb.StringProperty()
    user_id = ndb.StringProperty()
