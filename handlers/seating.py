import webapp2
import jinja2
import logging
import random

from google.appengine.ext import ndb
from models import student
from models import seating_arrangement
from utils import seating_generator

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class SeatingHandler(webapp2.RequestHandler):
    def render(self, students, msg=None):
        template = env.get_template('seating.html')
        vars_dict = {
            "msg": msg,
            "students": students,
            "keystring": ','.join([s.key.urlsafe() for s in students]),
        }
        self.response.out.write(template.render(vars_dict))
    
    def get(self):
        students = student.Student.query().fetch()
        students = seating_generator.SeatingGenerator(students).generate_seating()
            
        self.render(students)
    
    def post(self):
        student_str = self.request.get("keystring")
        students = self._get_student_list(student_str)
        try:
            self._save_arrangement(students)
        except Exception as e:
            msg = "Error... %s" % e
            logging.info(msg)
            self.render(students, msg=msg)
            return
        
        msg = "Seating arrangement saved!"
        logging.info(msg)
        self.render(students, msg=msg)
            
    def _get_student_list(self, student_str):
        key_list = student_str.split(',')
        return [ndb.Key(urlsafe=k).get() for k in key_list]

    def _save_arrangement(self, student_list):
        for i in range(0, len(student_list), 2):
            student_a = student_list[i]
            student_b = student_list[i + 1]
            student_a.already_paired.append(student_b.key)
            student_b.already_paired.append(student_a.key)
            
        sa = seating_arrangement.SeatingArrangement(
            day=int(self.request.get("day")),
            students=[s.key for s in student_list]
        )
        sa.put()
        for student in student_list:
            student.put()