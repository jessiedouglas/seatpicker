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

        c = None
        urlsafe = self.request.get("id")
        if urlsafe:
            classroom_id = ndb.Key(urlsafe=urlsafe)
            c = classroom_id.get()

        if c:
            self._add_classroom_if_not_present(classrooms, c)
            students = student.Student.query().filter(
                student.Student.classroom==classroom_id).fetch()
            sorted(classrooms, key=lambda c: c.name)
            self._render(classrooms, c=c, students=students)
        else:
            msg = None
            if urlsafe and not c:
                msg = "Error: Classroom has been deleted."
            sorted(classrooms, key=lambda c: c.name)
            self._render(classrooms, msg=msg)

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

        self.redirect("/classroom?id=%s" % c.key.urlsafe())

    def delete(self):
        urlsafe = self.request.get('id')
        key = ndb.Key(urlsafe=urlsafe)
        students = student.Student.query().filter(
            student.Student.classroom==key).fetch()
        name = key.get().name
        key.delete()

        for s in students:
            s.key.delete()

        msg = "Deleted class %s." % name
        logging.info(msg)

        self.redirect("/classroom")

    def _add_classroom_if_not_present(self, all_classrooms, classroom):
        seen = {}
        for c in all_classrooms:
            seen[c.key] = True

        if not seen.get(classroom.key, False):
            all_classrooms.append(classroom)
