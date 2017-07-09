import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from models import student

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class StudentHandler(webapp2.RequestHandler):
    def render(self, students, msg=None):
        template = env.get_template('student.html')
        vars_dict = {
            "msg": msg,
            "students": students,
        }
        self.response.out.write(template.render(vars_dict))
    
    def get(self):
        students = student.Student.query().fetch()
        self.render(students)
    
    def post(self):
        if self.request.get('_method') == 'delete':
            self.delete()
            return
        
        name = self.request.get('name')
        s = student.Student(name=name)
        all_students = student.Student.query().fetch()
        
        try:
            key = s.put()
        except Exception as e:
            msg = "oops... %s" % e
            logging.info(msg)
            self.render(all_students, msg=msg)
            return

        msg = "Successfully saved student %s!" % name
        logging.info(msg)
        all_students.append(key.get())
        self.render(all_students, msg=msg)
    
    def delete(self):
        urlsafe = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe)
        name = key.get().name
        key.delete()
        msg = "Deleted student %s." % name
        logging.info(msg)
        
        students = student.Student.query().fetch()
        self.render(students, msg=msg)