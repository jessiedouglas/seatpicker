import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from models import student
from utils import rendering_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class StudentHandler(webapp2.RequestHandler):
    def _render(self, students, msg=None):
        template = env.get_template('student.html')
        vars_dict = {
            "nav_bar": rendering_util.get_nav_bar(),
            "msg": msg,
            "students": students,
        }
        self.response.out.write(template.render(vars_dict))

    def get(self):
        if not users.get_current_user():
            self.redirect('/')

        students = student.Student.query().fetch()
        self._render(students)

    def post(self):
        if not users.get_current_user():
            self.redirect('/')

        if self.request.get('_method') == 'delete':
            self.delete()
            return

        name = self.request.get('name')
        s = student.Student(name=name)
        all_students = student.Student.query().fetch()

        try:
            key = s.put()
        except Exception as e:
            msg = "oops... %s" % e
            logging.info(msg)
            self._render(all_students, msg=msg)
            return

        msg = "Successfully saved student %s!" % name
        logging.info(msg)
        all_students.append(key.get())
        self._render(all_students, msg=msg)

    def delete(self):
        urlsafe = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe)
        name = key.get().name
        key.delete()
        msg = "Deleted student %s." % name
        logging.info(msg)

        students = student.Student.query().fetch()
        self._render(students, msg=msg)
