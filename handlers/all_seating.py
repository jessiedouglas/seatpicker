import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from models import classroom
from models import student
from models import table
from utils import rendering_util
from utils import seating_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class AllSeatingHandler(webapp2.RequestHandler):
    UNOWNED_RESOURCE_ERROR = 'Sorry, the requested classroom does not belong to you.'

    def _render(self, c=None, seating_arrangements=None,
                arrangement_key_to_tables=None, msg=None):
        template = env.get_template('all_arrangements.html')
        vars_dict = {
            "msg": msg,
            "classroom": c,
            "classrooms": seating_util.get_classrooms(),
            "seating_arrangements":
                seating_arrangements if seating_arrangements else [],
            "arrangement_key_to_tables":
                arrangement_key_to_tables if arrangement_key_to_tables else {},
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

        if c and c.user_id != current_user.user_id():
            self._render(msg=UNOWNED_RESOURCE_ERROR)

        seating_arrangements = (
            seating_util.get_seating_arrangements(c) if c else [])
        arrangement_key_to_tables = {
            a.key:self._get_tables_and_students(a) \
            for a in seating_arrangements
        }

        self._render(c=c, seating_arrangements=seating_arrangements,
                     arrangement_key_to_tables=arrangement_key_to_tables)

    def _get_tables_and_students(self, arrangement):
        '''Retrieves all tables and students for a given arrangement.'''
        tables = ndb.get_multi(arrangement.tables)
        all_students = ndb.get_multi([s for t in tables for s in t.students])
        keys_to_students = {s.key:s for s in all_students}
        return [[
                keys_to_students.get(key) for key in t.students
            ] for t in tables
        ]
