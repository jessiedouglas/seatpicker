import webapp2
import jinja2

from utils import rendering_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('home.html')
        vars_dict = {
            'nav_bar': rendering_util.get_nav_bar()
        }
        self.response.out.write(template.render(vars_dict))
