import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from models import student
from models import classroom
from utils import rendering_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class ClassroomHandler(webapp2.RequestHandler):
    def _render(self, classrooms, c=None, students=[], msg=None):
        template = env.get_template('classroom.html')
        vars_dict = {
            "nav_bar": rendering_util.get_nav_bar(),
            "msg": msg,
            "classroom": c,
            "classrooms": classrooms,
            "students": students
        }
        self.response.out.write(template.render(vars_dict))

    def get(self):
        if not users.get_current_user():
            self.redirect('/')

        classrooms = classroom.Classroom.query().fetch()
        urlsafe = self.request.get("classroom")
        if urlsafe:
            classroom_id = mdb.Key(urlsafe = urlsafe)
            c = classroom_id.get()
            students = student.Student.query().filter(
                student.Student.classroom==classroom_id).fetch()
            self._render(classrooms, c=c, students=students)
        else:
            self._render(classrooms)


    def post(self):
        if not users.get_current_user():
            self.redirect('/')

        if self.request.get('_method') == 'delete':
            self.delete()
            return

        classrooms = classroom.Classroom.query().fetch()

        name = self.request.get('name')
        c = classroom.Classroom(name=name)

        try:
            key = c.put()
        except Exception as e:
            msg = "oops... %s" % e
            logging.info(msg)
            self._render(classrooms, msg=msg)
            return

        msg = "Successfully saved class %s!" % name

        self._render(classrooms, c=c, msg=msg)

    def delete(self):
        urlsafe = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe)
        name = key.get().name
        key.delete()
        msg = "Deleted class %s." % name
        logging.info(msg)

        classrooms = classroom.Classroom.query().fetch()
        self._render(classrooms, msg=msg)
