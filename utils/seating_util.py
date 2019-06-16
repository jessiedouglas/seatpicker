from google.appengine.api import users
from models import classroom
from models import seating_arrangement

def get_seating_arrangements(current_classroom):
    query = seating_arrangement.SeatingArrangement.query()
    filtered = query.filter(
            seating_arrangement.SeatingArrangement.classroom==current_classroom.key)
    seating_arrangements = filtered.order(
        seating_arrangement.SeatingArrangement.day).fetch()
    return seating_arrangements

def get_classrooms():
    return classroom.Classroom.query().filter(
        classroom.Classroom.user_id==users.get_current_user().user_id()
    ).fetch()
