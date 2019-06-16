import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from models import classroom
from models import student
from models import seating_arrangement
from models import table
from utils import rendering_util
from utils import seating_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class AllSeatingHandler(webapp2.RequestHandler):
    UNOWNED_RESOURCE_ERROR = 'Sorry, the requested classroom does not belong to you.'

    def _render(self, c=None, seating_arrangements=[], msg=None):
        template = env.get_template('all_arrangements.html')
        vars_dict = {
            "msg": msg,
            "classroom": c,
            "classrooms": seating_util.get_classrooms(),
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

        seating_arrangements = []

        if c and c.user_id != current_user.user_id():
            self._render(msg=UNOWNED_RESOURCE_ERROR)

        if c:
            seating_arrangements = seating_util.get_seating_arrangements(c)

        self._render(c=c, seating_arrangements=seating_arrangements)
