import logging
import random

def sort_by_score(s):
    return s.score
    
def get_sort_function(a, ids_to_vertices):
    def _sort(b):
        b_vertex = ids_to_vertices[b]
        return abs(a.score - b_vertex.score)
        
    return _sort

def get_sort_function2(ids_to_vertices):
    def sort_pairs(pair):
        a = ids_to_vertices[pair[0].id]
        b = ids_to_vertices[pair[1].id]
        return max([a.score, b.score])


class Vertex(object):
    def __init__(self, student, possible_pairs):
        self.student = student
        self.id = student.key
        self.score = self._get_score(student.columns)
        self.possible_pairs = possible_pairs
        self.pair = None   
        
    def _get_score(self, scores):
        if len(scores) == 0:
            return 0.0
        return sum(scores) / len(scores)
        
    def sort_pairs(self, ids_to_vertices):
        # Sort possible pairs so that pairs with the smallest difference in score
        # come first in the list.
        random.shuffle(self.possible_pairs)
        sort_function = get_sort_function(self, ids_to_vertices)
        self.possible_pairs.sort(key=sort_function)
        

class SeatingGenerator(object):
    def __init__(self, students):
        # A map of students to possible pairs
        self.vertices = self._build_student_graph(students)
        random.shuffle(self.vertices)
        self.vertices.sort(key=sort_by_score)
        
        self.ids_to_vertices = {}
        for v in self.vertices:
            self.ids_to_vertices[v.id] = v
            
        for v in self.vertices:
            v.sort_pairs(self.ids_to_vertices)
        # A map of vertices to whether they have been paired
        self.paired = {}
        
    def generate_seating(self):
        self._find_maximal_matching()
        
        unpaired = self._get_unpaired()
        for u in unpaired:
            # Some will get paired before we get to them
            if u.id not in self.paired:
                self._readjust_pairs(u)
        
        seen = {}
        pairs_list = []
        for v in self.vertices:
            if not seen.get(v.id, False):
                pairs_list.append([v.student, v.pair.student])
                seen[v.id] = True
                seen[v.pair.id] = True
        pairs_list.sort(key=get_sort_function2(self.ids_to_vertices))
        pairs_list = self._seat_pairs_in_columns(pairs_list)

        logging.info([(s.name, self.ids_to_vertices[s.key].score) for s in pairs_list])

        return pairs_list
                
    def _build_student_graph(self, students):
        all_student_set = set([s.key for s in students])
        vertices = []
        for student in students:
            paired_set = set(student.already_paired)
            possible_pairs = list(all_student_set - paired_set - set([student.key]))
            vertices.append(Vertex(student, possible_pairs))
            
        return vertices

    def _find_maximal_matching(self) :
        for a in self.vertices:
            if not self.paired.get(a.id, False):
                b = self._choose_second_of_pair(a)
                if b is not None:
                    self._pair_students(a, b)
        
    def _choose_first_of_pair(self):
        return self._choose_student(self.vertices)
        
    def _choose_second_of_pair(self, a):
        pairs_as_vertices = [self.ids_to_vertices[s] for s in a.possible_pairs]
        return self._choose_student(pairs_as_vertices)
 
    def _choose_student(self, students):
        for s in students:
            if not self.paired.get(s.id, False):
                return s

        return None
        
    def _get_unpaired(self):
        return [v for v in self.vertices if not self.paired.get(v.id, False)]
        
    def _readjust_pairs(self, a):
        # We want a to appear to have been paired
        self.paired[a.id] = True
        
        logging.warning(len(self.vertices))
        logging.warning(self.paired)
        logging.warning(len(self.paired))
        b = self._choose_first_of_pair()
        
        # Find c and d paired, s.t. a can pair with c and b can pair with d
        # This should be guaranteed with our parameters
        c = None
        d = None
        for p in a.possible_pairs:
            c = self.ids_to_vertices[p]
            if c.pair.id in b.possible_pairs:
                d = self.ids_to_vertices[c.pair.id]
                break
                
        self._pair_students(a, c)
        self._pair_students(b, d)

    def _pair_students(self, a, b):
        self.paired[a.id] = True
        self.paired[b.id] = True
        a.pair = b
        b.pair = a
        
    def _seat_pairs_in_columns(self, pairs_list):
        seating = []
        for n in range(len(pairs_list)):
            if n % 6 == 2 or n % 6 == 3:
                seating.extend(pairs_list.pop())
            else:
                seating.extend(pairs_list[0])
                pairs_list = pairs_list[1:]
        
        return seating
        