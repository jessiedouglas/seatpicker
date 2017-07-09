import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from models import student

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class SeatingHandler(webapp2.RequestHandler):
    def get(self):
        students = student.Student.query().fetch()
        if self.request.get("generate") == "true":
            students = self._generate_seating(students)
            
        template = env.get_template('seating.html')
        vars_dict = {
            "msg": None,
            "students": students,
        }
        self.response.out.write(template.render(vars_dict))
    
    def _generate_seating(self, students):
        students.reverse()
        return students