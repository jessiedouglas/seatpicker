import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from models import student

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class StudentHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('student.html')
        vars_dict = {
            "msg": None,
            "students": student.Student.query().fetch(),
        }
        self.response.out.write(template.render(vars_dict))
    
    def post(self):
        if self.request.get('_method') == 'delete':
            self.delete()
            return
        
        name = self.request.get('name')
        s = student.Student(name=name)
        all_students = student.Student.query().fetch()
        template = env.get_template('student.html')
        
        try:
            key = s.put()
        except Exception as e:
            msg = "oops... %s" % e
            logging.info(msg)
            vars_dict = {
                "msg": msg,
                "students": all_students,
            }
            self.response.out.write(template.render(vars_dict))
            return

        msg = "Successfully saved student %s!" % name
        logging.info(msg)
        all_students.append(key.get())
        vars_dict = {
            "msg": msg,
            "students": all_students,
        }
        logging.info(vars_dict["students"])
        self.response.out.write(template.render(vars_dict))
    
    def delete(self):
        urlsafe = self.request.get('key')
        key = ndb.Key(urlsafe=urlsafe)
        name = key.get().name
        key.delete()
        msg = "Deleted student %s." % name
        logging.info(msg)
        
        template = env.get_template('student.html')
        vars_dict = {
            "msg": msg,
            "students": student.Student.query().fetch(),
        }
        self.response.out.write(template.render(vars_dict))