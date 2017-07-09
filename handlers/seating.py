import webapp2
import jinja2
import logging
import random

from google.appengine.ext import ndb
from models import student
from models import seating_arrangement

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
        if self.request.get("generate") == "true":
            students = self._generate_seating(students)
            
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
        
    def _generate_seating(self, students):
        # A map of students to possible pairs
        student_pair_map = self._build_student_graph(students)
        # A map of students to number of remaining available pairs
        student_pair_count_map = dict(
            (s.key, len(student_pair_map[s.key])) for s in students)
        # A map of students to whether or not they have been paired
        paired = {}
        pairs = {}
        
        while len(paired) < len(students):
            student_a = self._choose_student(
                self._get_next_student_list(student_pair_count_map), paired)
            student_b = self._choose_student(student_pair_map[student_a], paired)
            if student_b is None:
                # TODO: No pair exists! Triage
            pairs[student_a] = student_b
            pairs[student_b] = student_a
            del student_pair_count_map[student_a]
            del student_pair_count_map[student_b]
            self._decrease_pair_counts(
                student_a, student_pair_map, student_pair_count_map)
            self._decrease_pair_counts(
                student_a, student_pair_map, student_pair_count_map)
        
    def _build_student_graph(self, students):
        all_student_set = set([s.key for s in students])
        student_pair_map = {}
        for student in students:
            paired_set = set(student.already_paired)
            student_pair_map[student.key] = list(all_student_set - paired_set)
            logging.info(student_pair_map[student.key])
            
        return student_pair_map
        
    def _get_next_student_list(self, student_pair_count_map):
        # Choose a student who has the least number of pair options
        counts = student_pair_count_map.values()
        min_count = min(counts)
        return [s for s, v in student_pair_count_map.iteritems() if v == min_count]
        
    def _choose_student(self, students, paired):
        rand_i = random.randint(0, len(students) - 1)
        s = students[rand_i]
        count = 1
        while paired.get(s.key, False) and count < len(students):
            rand_i += 1
            s = students[rand_i % len(students)]
            count += 1
         
        if count >= len(students):
            # All students were already paired
            return None

        return s
        
    def _get_student_list(self, student_str):
        key_list = student_str.split(',')
        return [ndb.Key(urlsafe=k).get() for k in key_list]
        
    def _decrease_pair_counts(self, student, student_pair_map, student_pair_counts):
        for s in student_pair_map[student]:
            if student_pair_counts.has_key(s):
                student_pair_counts[s] -= 1
        
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