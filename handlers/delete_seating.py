import webapp2
import jinja2
import logging
import urllib

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
        seating_key.delete()

        msg = 'Day %s seating arrangement deleted' % arrangement.day
        logging.info(msg)

        params = {
            'msg': msg,
            'classroom': classroom.key.urlsafe(),
        }
        if self.request.get('redirect_to') == 'seating':
            params['table_size'] = self.request.get('table_size')
            self.redirect('/seating?%s' % urllib.urlencode(params))
        else:
            self.redirect('/allseating?%s' % urllib.urlencode(params))
