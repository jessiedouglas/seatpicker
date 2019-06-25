import webapp2
import functools
import jinja2
import logging
import random
import urllib

from google.appengine.ext import ndb
from google.appengine.api import users
from models import classroom
from models import student
from models import seating_arrangement
from models import table
from utils import rendering_util
from utils import seating_generator
from utils import seating_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

DEFAULT_TABLE_SIZE = 6


class SeatingHandler(webapp2.RequestHandler):
    UNOWNED_RESOURCE_ERROR = 'Sorry, the requested classroom does not belong to you.'

    def _render(self, is_saved=False, c=None, students_by_table=[],
            msg=None, default_table_size=DEFAULT_TABLE_SIZE, arrangement=None):
        template = env.get_template('seating.html')

        classrooms = seating_util.get_classrooms()
        classrooms = sorted(classrooms, key=lambda c: c.name)

        vars_dict = {
            "msg": msg,
            "classroom": c,
            "classrooms": classrooms,
            "day": arrangement.day if arrangement else self._get_next_day(c),
            "students_by_table": students_by_table,
            "num_students": self._get_num_students(students_by_table),
            "is_saved": is_saved,
            "keystring": ';'.join([
                ','.join([
                    s.key.urlsafe() if s else '' for s in t
                ]) for t in students_by_table if t
            ]),
            "default_table_size": default_table_size,
        }
        if arrangement:
            vars_dict['arrangement_key'] = arrangement.key.urlsafe()

        main_content = template.render(vars_dict)
        self.response.out.write(rendering_util.render_page(main_content))

    def get(self):
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return

        encoded_msg = self.request.get('msg')
        msg = urllib.unquote_plus(encoded_msg) if encoded_msg else None

        classroom_key = self.request.get('classroom')
        c = None
        if classroom_key:
            key = ndb.Key(urlsafe=classroom_key)
            c = key.get()

        if c and c.user_id != current_user.user_id():
            self._render(msg=UNOWNED_RESOURCE_ERROR)

        table_size = int(self.request.get(
            'table_size', default_value=DEFAULT_TABLE_SIZE))

        arrangement_key = self.request.get('arrangement')
        if arrangement_key:
            self._render_view_only(c, arrangement_key, table_size, msg)
        else:
            self._render_new_generation(c, table_size, msg)

    def post(self):
        if not users.get_current_user():
            self.redirect('/')
            return

        student_str = self.request.get("keystring")
        students_by_table = self._get_students_by_table(student_str)
        classroom_key = ndb.Key(urlsafe=self.request.get("classroom_id"))
        table_size = self.request.get(
            "table_size", default_value=DEFAULT_TABLE_SIZE)
        c = None
        if classroom_key:
            c = classroom_key.get()

        try:
            arrangement = self._save_arrangement(
                classroom_key, students_by_table)
        except Exception as e:
            msg = "Error... %s" % e
            logging.info(msg)
            params = {
                'classroom': classroom_key.urlsafe(),
                'table_size': table_size,
                'msg': msg
            }
            self.redirect('/seating?%s' % urllib.urlencode(params))

        msg = "Seating arrangement saved!"
        logging.info(msg)

        params = {
            'classroom': classroom_key.urlsafe(),
            'table_size': table_size,
            'msg': msg,
            'arrangement': arrangement.key.urlsafe()
        }
        self.redirect('/seating?%s' % urllib.urlencode(params))

    def _get_next_day(self, c):
        if not c:
            return None
        seating_arrangements = seating_util.get_seating_arrangements(c)
        if len(seating_arrangements) == 0:
            return 1
        return seating_arrangements[-1].day + 1

    def _get_num_students(self, students_by_table):
        '''Returns the sum of all non-None students in all tables'''
        return functools.reduce(
            lambda sum, table: sum + functools.reduce(
                                        lambda isum, s: isum + 1 if s else isum,
                                        table, 0),
             students_by_table, 0)

    def _seat_students(self, students, table_size):
        '''Returns a list of lists, each of which contains a table of
           students.
        '''
        counter = 0
        tables = []
        current_table = []
        for i, student in enumerate(students):
            current_table.append(student)
            if i % table_size == table_size - 1 or i == len(students) - 1:
                tables.append(current_table)
                current_table = []
        return tables

    def _render_view_only(self, c, arrangement_key, table_size, msg):
        arrangement = ndb.Key(urlsafe=arrangement_key).get()
        if arrangement:
            students_by_table = seating_util.seat_students(arrangement)
            self._render(is_saved=True, c=c,
                         students_by_table=students_by_table, msg=msg,
                         default_table_size=table_size, arrangement=arrangement)
        else:
            msg = "Unable to find seating arrangement. Maybe it was deleted?"
            self._render_new_generation(c, table_size, msg)

    def _render_new_generation(self, c, table_size, msg):
        students = []
        if c:
            students = student.Student.query().filter(
                student.Student.classroom==c.key).fetch()
            if len(students) > 0:
                students = seating_generator.SeatingGenerator(
                    students).generate_seating()
            else:
                msg = ("Can't generate seating: expected students, found none")
                logging.info(msg)

        self._render(c=c, default_table_size=table_size, msg=msg,
            students_by_table=self._seat_students(students, table_size))

    def _get_students_by_table(self, all_key_str):
        '''Parses the expected key string and returns all students in a list
        of lists, where the inner lists each represent a table of students.'''
        table_strings = all_key_str.split(';')
        tables = []
        for table_key_str in table_strings:
            students = [
                ndb.Key(urlsafe=k).get() if k != "" else None for k in table_key_str.split(",")
            ]
            tables.append(students)
        return tables

    def _save_arrangement(self, classroom_key, students_by_table):
        '''Creates and saves a new SeatingArrangement and set of Tables for
        the given arrangement. Also updates Students with their new pairings.'''
        if not classroom_key:
            raise Exception("Classroom not found")

        tables = [
            table.Table(students=[
                s.key for s in t if s
            ]) for t in students_by_table
        ]

        sa = seating_arrangement.SeatingArrangement(
            day=int(self.request.get("day")),
            tables=ndb.put_multi(tables),
            classroom=classroom_key
        )
        sa.put()
        ndb.put_multi(self._pair_students(students_by_table))

        return sa

    def _pair_students(self, students_by_table):
        '''Sets Student pairing data for all students based on the given
        arrangement. Returns a flattened list of students.'''
        student_list = []
        for table_students in students_by_table:
            for i in range(0, len(table_students), 2):
                student_a = table_students[i]
                student_b = (table_students[i + 1]
                             if i + 1 < len(table_students) else None)
                if student_a and student_b:
                    student_a.already_paired.append(student_b.key)
                    student_b.already_paired.append(student_a.key)
                if student_a:
                    student_list.append(student_a)
                if student_b:
                    student_list.append(student_b)

        return student_list
