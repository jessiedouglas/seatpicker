import logging
import functools
import random
import sys


class Vertex(object):
    def __init__(self, student, possible_pairs):
        self.student = student
        self.id = student.key
        self.possible_pairs = possible_pairs
        self.pair = None


class SeatingGenerator(object):
    def __init__(self, students):
        # A map of students to possible pairs
        self.vertices = self._build_student_graph(students)
        random.shuffle(self.vertices)

        self.ids_to_vertices = {}
        for v in self.vertices:
            self.ids_to_vertices[v.id] = v

        self.average_num_pairs = self._calculate_average_num_pairs(students)
        self.min_num_pairs = self._calculate_min_num_pairs(students)
        # A map of vertices to whether they have been paired
        self.paired = {}

    def generate_seating(self):
        self._find_maximal_matching()

        unpaired = self._get_unpaired()
        for u in unpaired:
            # Some will get paired before we get to them
            if u.id not in self.paired:
                self._readjust_pairs(u)
        # If there are some remaining vertices that are unpaired, pair them
        # randomly. This should not happen unless we have exceeded N/2
        # arrangements, where N is the number of students.
        self._handle_remaining_unpaired()

        seen = {}
        pairs_list = []
        for v in self.vertices:
            if not seen.get(v.id, False):
                seen[v.id] = True
                if v.pair:
                    pair = [v.student, v.pair.student]
                    seen[v.pair.id] = True
                else:
                    pair = [v.student, None]
                pairs_list.append(pair)

        # Flatten the list
        return [s for pair in pairs_list for s in pair]

    def _build_student_graph(self, students):
        all_student_set = set([s.key for s in students])
        vertices = []
        for student in students:
            paired_set = set(student.already_paired)
            possible_pairs = list(
                all_student_set - paired_set - set([student.key]))
            vertices.append(Vertex(student, possible_pairs))

        return vertices

    def _calculate_average_num_pairs(self, students):
        total = functools.reduce(
                    lambda acc, s: acc + len(s.already_paired), students, 0)
        return total * 1.0 / len(students)

    def _calculate_min_num_pairs(self, students):
        return functools.reduce(
                lambda min, s: len(s.already_paired) \
                    if len(s.already_paired) < min else min,
                students,
                # Initiate with a very large number so that it's bigger than
                # len(s.already_paired) for any given student
                sys.maxsize)

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

        # Choose an unpaired vertex
        b = self._choose_first_of_pair()
        # If there are no unpaired vertices left (i.e., either because there is
        # an odd number or because we have run out of unique pairings), reset a
        # and return.
        if not b:
            self.paired[a.id] = False
            return

        # Find c and d paired, s.t. a has not yet paired with c and b has not
        # yet paired with d. This is guaranteed to exist for N/2 arrangements,
        # where N is the total number of vertices.
        c = None
        d = None
        for p_id in a.possible_pairs:
            c = self.ids_to_vertices[p_id]
            if c.pair.id in b.possible_pairs:
                d = self.ids_to_vertices[c.pair.id]
                break

        if c and d:
            self._pair_students(a, c)
            self._pair_students(b, d)

    def _handle_remaining_unpaired(self):
        # Randomly pair remaining unpaired students
        unpaired = self._get_unpaired()
        if len(unpaired) == 0:
            return
        random.shuffle(unpaired)
        # Need len(unpaired) - 1 so that we don't try to pair an odd number of
        # students
        for i in range(0, len(unpaired) - 1, 2):
            self._pair_students(unpaired[i], unpaired[i + 1])

        # We want to try to make sure the unpaired student isn't getting left
        # unpaired more than other students
        if not unpaired[-1].pair:
            self._readjust_singleton(unpaired[-1])

    def _readjust_singleton(self, singleton):
        # If all students have been paired the same number of times, or if this
        # student is not at least tied for least number of pairs, no need to
        # readjust.
        if self.min_num_pairs == self.average_num_pairs or \
           len(singleton.student.already_paired) != self.min_num_pairs:
            return

        other_student_keys = list(
            set([v.student.key for v in self.vertices]) - set([singleton.id]))
        other_students = [
            self.ids_to_vertices.get(key) for key in other_student_keys]
        # Sort students in order from most to least number of pairs
        other_students.sort(
            key=lambda v: len(v.student.already_paired), reverse=True)
        possible_pair_set = set(singleton.possible_pairs)

        for other in other_students:
            if other.pair and other.pair.id in possible_pair_set:
                self._pair_students(singleton, other.pair)
                self._unpair_student(other)
                return

    def _pair_students(self, a, b):
        self.paired[a.id] = True
        self.paired[b.id] = True
        a.pair = b
        b.pair = a

    def _unpair_student(self, student_vertex):
        student_vertex.pair = None
        self.paired[student_vertex.id] = False
