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
    def render_one(self, students, msg=None, day=None):
        template = env.get_template('seating.html')
        vars_dict = {
            "msg": msg,
            "day": day,
            "students": students,
            "keystring": ','.join([s.key.urlsafe() for s in students]),
        }
        self.response.out.write(template.render(vars_dict))
        
    def render_all(self, seating_arrangements, msg=None):
        template = env.get_template('all_arrangements.html')
        vars_dict = {
            "msg": msg,
            "seating_arrangements": seating_arrangements,
        }
        self.response.out.write(template.render(vars_dict))
    
    def get(self):
        if self.request.get("list") == "true":
            seating_arrangements = seating_arrangement.SeatingArrangement.query().fetch()
            seating_arrangements.sort(key=lambda sa: sa.day)
            self.render_all(seating_arrangements)
        else:
            students = student.Student.query().fetch()
            students = seating_generator.SeatingGenerator(students).generate_seating()
            
            self.render_one(students)
    
    def post(self):
        student_str = self.request.get("keystring")
        students = self._get_student_list(student_str)
        try:
            arrangement = self._save_arrangement(students)
        except Exception as e:
            msg = "Error... %s" % e
            logging.info(msg)
            self.render(students, msg=msg)
            return
        
        msg = "Seating arrangement saved!"
        logging.info(msg)
        self.render_one(students, msg=msg, day=arrangement.day)
            
    def _get_student_list(self, student_str):
        key_list = student_str.split(',')
        return [ndb.Key(urlsafe=k).get() for k in key_list]

    def _save_arrangement(self, student_list):
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
            students=[s.key for s in student_list]
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
        if i in [1, 12, 13, 24]:
            return 2.0
        
        if i in [2, 3, 10, 11, 14, 15, 22, 23, 25, 30]:
            return 1.0
            
        return 0.0