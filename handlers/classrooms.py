import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from models import student
from models import classroom
from models import seating_arrangement
from utils import rendering_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class ClassroomHandler(webapp2.RequestHandler):
    def _render(self, classrooms=[], c=None, students=[], msg=None):
        template = env.get_template('classroom.html')

        if len(classrooms) == 0:
            classrooms = self._get_classrooms()

        classrooms = sorted(classrooms, key=lambda c: c.name)

        vars_dict = {
            "msg": msg,
            "classroom": c,
            "classrooms": classrooms,
            "students": students
        }
        main_content = template.render(vars_dict)
        self.response.out.write(rendering_util.render_page(main_content))

    def get(self):
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return

        c = None
        urlsafe = self.request.get("id")
        if urlsafe:
            classroom_id = ndb.Key(urlsafe=urlsafe)
            c = classroom_id.get()

        if c and c.user_id != users.get_current_user().user_id():
            self._render(msg='Sorry, you do not own the requested classroom.')
            return

        if c:
            classrooms = self._get_classrooms()
            self._add_classroom_if_not_present(classrooms, c)
            students = student.Student.query().filter(
                student.Student.classroom==classroom_id).fetch()
            self._render(classrooms=classrooms, c=c, students=students)
        else:
            msg = None
            if urlsafe and not c:
                msg = "Error: Classroom has been deleted."
            self._render(msg=msg)

    def post(self):
        if not users.get_current_user():
            self.redirect('/')
            return

        if self.request.get('_method') == 'delete':
            self.delete()
            return

        name = self.request.get('name')
        c = classroom.Classroom(
            name=name, user_id=users.get_current_user().user_id())

        try:
            key = c.put()
        except Exception as e:
            msg = "oops... %s" % e
            logging.info(msg)
            self._render(msg=msg)
            return

        self.redirect("/classroom?id=%s" % c.key.urlsafe())

    def delete(self):
        urlsafe = self.request.get('id')
        key = ndb.Key(urlsafe=urlsafe)
        students = student.Student.query().filter(
            student.Student.classroom==key).fetch()
        seating_arrangements = (
            seating_arrangement.SeatingArrangement.query().filter(
                seating_arrangement.SeatingArrangement.classroom==key
            ).fetch())
        name = key.get().name
        key.delete()

        for s in students:
            s.key.delete()
        for sa in seating_arrangements:
            sa.key.delete()

        msg = "Deleted class %s." % name
        logging.info(msg)

        self.redirect("/classroom")

    def _get_classrooms(self):
        return classroom.Classroom.query().filter(
            classroom.Classroom.user_id==users.get_current_user().user_id()
        ).fetch()

    def _add_classroom_if_not_present(self, all_classrooms, classroom):
        seen = {}
        for c in all_classrooms:
            seen[c.key] = True

        if not seen.get(classroom.key, False):
            all_classrooms.append(classroom)
