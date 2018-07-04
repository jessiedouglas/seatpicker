import webapp2
import jinja2

from utils import rendering_util

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('home.html')
        main_content = template.render({})
        self.response.out.write(rendering_util.render_page(main_content))
