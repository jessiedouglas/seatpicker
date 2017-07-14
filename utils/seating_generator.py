import logging
import random

class Vertex(object):
    def __init__(self, student, possible_pairs):
        self.student = student
        self.id = student.key
        self.possible_pairs = possible_pairs
        random.shuffle(self.possible_pairs)
        self.pair = None


class SeatingGenerator(object):
    def __init__(self, students):
        # A map of students to possible pairs
        self.vertices = self._build_student_graph(students)
        random.shuffle(self.vertices)
        
        self.ids_to_vertices = {}
        for v in self.vertices:
            self.ids_to_vertices[v.id] = v
        # A map of vertices to whether they have been paired
        self.paired = {}
        
    def generate_seating(self):
        self._find_maximal_matching()
        
        # PASTED FOR DEBUGGING
        seen = {}
        pairs_list = []
        for v in self.vertices:
            if not seen.get(v.id, False):
                logging.warning([v.student.name, v.pair.student.name])
                pairs_list.extend([v.student, v.pair.student])
                seen[v.id] = True
                seen[v.pair.id] = True
                
        logging.warning("\n\n\n\n\n")
        # THAT STUFF WAS PASTED > YEAH
        
        unpaired = self._get_unpaired()
        for u in unpaired:
            # Some will get paired before we get to them
            if u.id not in self.paired:
                self._readjust_pairs(u)
        
        seen = {}
        pairs_list = []
        for v in self.vertices:
            if not seen.get(v.id, False):
                pairs_list.extend([v.student, v.pair.student])
                seen[v.id] = True
                seen[v.pair.id] = True
        
        if len(pairs_list) > 30:
            logging.warning(len(pairs_list))
            logging.warning([str(s.name) for s in pairs_list])
            raise Exception()
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
        return self._choose_student(a.possible_pairs)
 
    def _choose_student(self, students):
        rand_i = random.randint(0, len(students) - 1)
        s = students[rand_i]
        count = 1
        while self.paired.get(s, False) and count < len(students):
            rand_i += 1
            s = students[rand_i % len(students)]
            count += 1
         
        if count >= len(students):
            # All students were already paired
            return None

        return self.ids_to_vertices[s]
        
    def _get_unpaired(self):
        return [v for v in self.vertices if not self.paired.get(v.id, False)]
        
    def _readjust_pairs(self, a):
        # We want a to appear to have been paired
        self.paired[a.id] = True
        
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
        