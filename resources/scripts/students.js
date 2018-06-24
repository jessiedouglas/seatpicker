const Student = {};

Student.EMPTY_STUDENT_LIST_TEXT_ = 'No students found!';

Student.main = function() {
  const addStudentButton = document.querySelector('#addStudent');
  if (addStudentButton) {
    addStudentButton.addEventListener('click', (event) => {
      event.preventDefault();
      const nameEl = document.querySelector('#studentName');
      Student.saveStudent_(nameEl.value).then((response) => {
        return response.json();
      }).then(Student.appendStudent_);
    });
  }
}

Student.saveStudent_ = function(name) {
  if (!name) return Promise.reject();

  const options = {
    method: 'POST',
    credentials: 'same-origin'
  }
  const request = new Request('/student?name=' + name, options);
  return fetch(request);
}

Student.appendStudent_ = function(student) {
  const studentContent = '<p class="student_id" hidden>' + student.id + '</p>' +
    '<p class="student_id">' + student.name + '</p>' +
    '<a href="#">Delete</a>';
  const studentEl = document.createElement('div');
  studentEl.innerHTML = studentContent;
  const students = document.getElementById('students');
  if (students.innerText.includes(Student.EMPTY_STUDENT_LIST_TEXT_)) {
    students.innerText = '';
  }
  students.insertAdjacentElement('beforeend', studentEl);
}
