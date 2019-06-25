import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


class DeleteSeatingHandler(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return

        seating_key = ndb.Key(urlsafe=self.request.get('arrangement'))
        if not seating_key:
            logging.warning('Could not find requested seating arrangement')
            return

        arrangement = seating_key.get()
        classroom = arrangement.classroom.get()
        logging.info('Deleting Day %s seating arrangement for class %s',
                     arrangement.day, classroom.name)
        seating_key.delete()
        self.redirect('/allseating?classroom=%s' % classroom.key.urlsafe())
