import webapp2
import jinja2
import logging
import random

from google.appengine.ext import ndb
from google.appengine.api import users
from models import classroom
from models import student
from models import seating_arrangement
from utils import rendering_util
from utils import seating_generator

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


class SeatingHandler(webapp2.RequestHandler):
    UNOWNED_RESOURCE_ERROR = 'Sorry, the requested classroom does not belong to you.'

    def _render_one(self, is_saved=False, c=None, students=[], msg=None, day=None):
        template = env.get_template('seating.html')

        classrooms = self._get_classrooms()
        classrooms = sorted(classrooms, key=lambda c: c.name)

        vars_dict = {
            "msg": msg,
            "classroom": c,
            "classrooms": classrooms,
            "day": day if day else self._get_next_day(c),
            "students": students,
            "is_saved": is_saved,
            "keystring": ','.join([s.key.urlsafe() for s in students]),
        }
        main_content = template.render(vars_dict)
        self.response.out.write(rendering_util.render_page(main_content))

    def _render_all(self, c=None, seating_arrangements=[], msg=None):
        template = env.get_template('all_arrangements.html')
        vars_dict = {
            "msg": msg,
            "classroom": c,
            "classrooms": self._get_classrooms(),
            "seating_arrangements": seating_arrangements,
        }
        main_content = template.render(vars_dict)
        self.response.out.write(rendering_util.render_page(main_content))

    def get(self):
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return

        urlsafe = self.request.get("classroom")
        c = None
        if urlsafe:
            key = ndb.Key(urlsafe=urlsafe)
            c = key.get()

        if self.request.get("list") == "true":
            seating_arrangements = []

            if c and c.user_id != current_user.user_id():
                self._render_all(msg=UNOWNED_RESOURCE_ERROR)

            if c:
                seating_arrangements = self._get_seating_arrangements(c)

            self._render_all(c=c, seating_arrangements=seating_arrangements)
        else:
            if c and c.user_id != current_user.user_id():
                self._render_one(msg=UNOWNED_RESOURCE_ERROR)

            students = []
            if c:
                students = student.Student.query().filter(
                    student.Student.classroom==c.key).fetch()
                if len(students) == 30:
                    students = seating_generator.SeatingGenerator(
                        students).generate_seating()
                else:
                    msg = ("Can't generate seating: "
                           "expected 30 students, found %d" % len(students))
                    logging.info(msg)

            self._render_one(c=c, students=students)

    def post(self):
        if not users.get_current_user():
            self.redirect('/')
            return

        student_str = self.request.get("keystring")
        students = self._get_student_list(student_str)
        classroom_key = ndb.Key(urlsafe=self.request.get("classroom_id"))
        c = None
        if classroom_key:
            c = classroom_key.get()

        try:
            arrangement = self._save_arrangement(classroom_key, students)
        except Exception as e:
            msg = "Error... %s" % e
            logging.info(msg)
            self._render_one(c=c, students=students, msg=msg)
            return

        msg = "Seating arrangement saved!"
        logging.info(msg)

        self._render_one(
            is_saved=True, c=c, students=students, msg=msg, day=arrangement.day)

    def _get_next_day(self, c):
        if not c:
            return None
        seating_arrangements = self._get_seating_arrangements(c)
        if len(seating_arrangements) == 0:
            return 1
        return seating_arrangements[-1].day + 1

    def _get_seating_arrangements(self, c):
        query = seating_arrangement.SeatingArrangement.query()
        filtered = query.filter(
                seating_arrangement.SeatingArrangement.classroom==c.key)
        seating_arrangements = filtered.order(
            seating_arrangement.SeatingArrangement.day).fetch()
        return seating_arrangements

    def _get_classrooms(self):
        return classroom.Classroom.query().filter(
            classroom.Classroom.user_id==users.get_current_user().user_id()
        ).fetch()

    def _get_student_list(self, student_str):
        key_list = student_str.split(',')
        return [ndb.Key(urlsafe=k).get() for k in key_list]

    def _save_arrangement(self, classroom_key, student_list):
        if not classroom_key:
            raise Exception("Classroom not found")
        if not self._is_unique(student_list):
            raise Exception("Regenerate seating first!")
        for i in range(0, len(student_list), 2):
            student_a = student_list[i]
            student_b = student_list[i + 1]
            student_a.already_paired.append(student_b.key)
            student_b.already_paired.append(student_a.key)
            student_a.columns.append(self._get_column_score(i))
            student_b.columns.append(self._get_column_score(i + 1))

        sa = seating_arrangement.SeatingArrangement(
            day=int(self.request.get("day")),
            students=[s.key for s in student_list],
            classroom=classroom_key
        )
        sa.put()
        for student in student_list:
            student.put()

        return sa

    def _is_unique(self, student_list):
        seating_arrangements = seating_arrangement.SeatingArrangement.query().fetch()
        for sa in seating_arrangements:
            if student_list[0].key == sa.students[0] and student_list[1].key == sa.students[1]:
               return False

        return True

    def _get_column_score(self, i):
        if i in [0, 11, 12, 23]:
            return 5.0

        if i in [1, 10, 13, 22]:
            return 4.0

        if i in [2, 9, 14, 21, 24, 29]:
            return 3.0

        if i in [3, 8, 15, 20]:
            return 2.0

        if i in [4, 7, 16, 19, 25, 26, 27, 28]:
            return 1.0

        return 0.0
