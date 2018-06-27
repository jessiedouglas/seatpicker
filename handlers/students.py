import webapp2
import logging
import json

from google.appengine.ext import ndb
from google.appengine.api import users
from models import student


class StudentHandler(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
            self.redirect('/')
            return

        if self.request.get('_method') == 'delete':
            self.delete()
            return

        name = self.request.get('name')
        classroom_key = ndb.Key(urlsafe=self.request.get('classroom_id'))
        s = student.Student(name=name, classroom=classroom_key)

        try:
            key = s.put()
        except Exception as e:
            msg = "oops... %s" % e
            logging.info(msg)
            self._render(all_students, msg=msg)
            return

        msg = "Successfully saved student %s!" % name
        studentJson = json.dumps({
            'name': s.name,
            'id': s.key.urlsafe()
        })
        self.response.write(studentJson)

    def delete(self):
        urlsafe = self.request.get('id')
        key = ndb.Key(urlsafe=urlsafe)
        name = key.get().name
        key.delete()
        msg = "Deleted student %s." % name
        logging.info(msg)
