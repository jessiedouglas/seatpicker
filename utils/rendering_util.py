import jinja2

from google.appengine.api import users

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

def _get_nav_bar():
    user = users.get_current_user()
    if user:
        logout_url = users.create_logout_url('/')
        login_url = ""
    else:
        logout_url = ""
        login_url = users.create_login_url('/')

    template = env.get_template('nav.html')
    vars_dict = {
        "user": user,
        "logout_url": logout_url,
        "login_url": login_url,
    }
    return template.render(vars_dict)

def render_page(main_content, title=None):
    template = env.get_template('main_template.html')

    vars_dict = {
        'title': title if title else "Seating Generator",
        'nav': _get_nav_bar(),
        'main': main_content,
    }
    return template.render(vars_dict)
