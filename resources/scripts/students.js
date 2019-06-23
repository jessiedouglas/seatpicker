const Student = {};

Student.EMPTY_STUDENT_LIST_TEXT_ = 'No students found!';

Student.main = function() {
  const addStudentButton = document.querySelector('#addStudent');
  if (addStudentButton) {
    addStudentButton.addEventListener('click', (event) => {
      event.preventDefault();
      const nameEl = document.querySelector('#studentName');
      const classroom_id = document.querySelector('#classroom-id').innerText;
      Student.saveStudent_(nameEl.value, classroom_id).then((response) => {
        return response.json();
      }).then(Student.appendStudent_);
    });
  }

  const students = document.querySelector('#students');
  if (students) {
    students.addEventListener('click', (event) => {
      if (event.target.parentElement.classList.contains('delete-button')) {
        event.preventDefault();
        const parent = event.target.parentElement.parentElement;
        Student.deleteStudent_(
          Student.getStudentIdToDelete_(parent)).then(() => {
          parent.remove();
        });
      }
    });
  }
}

Student.saveStudent_ = function(name, classroom_id) {
  if (!name) return Promise.reject();

  const options = {
    method: 'POST',
    credentials: 'same-origin'
  }
  const request = new Request(
    '/student?name=' + name + '&classroom_id=' + classroom_id, options);
  return fetch(request);
}

Student.appendStudent_ = function(student) {
  const studentContent = '<p class="student-name">' + student.name + '</p>' +
    '<p class="student-id" hidden>' + student.id + '</p>' +
    '<p class="expander"></p>' +
    '<button ' +
        'class="delete-button mdl-button mdl-js-button mdl-js-ripple-effect">' +
        '<i class="material-icons">delete</i>' +
    '</button>';
  const studentEl = document.createElement('div');
  studentEl.innerHTML = studentContent;
  const students = document.getElementById('students');
  if (students.innerText.includes(Student.EMPTY_STUDENT_LIST_TEXT_)) {
    students.innerText = '';
  }
  studentEl.classList.add('student');
  students.insertAdjacentElement('beforeend', studentEl);
  const nameInput = document.querySelector('#studentName');
  nameInput.value = "";
}

Student.getStudentIdToDelete_ = function(parent) {
  const idEl = parent.querySelector('.student-id');
  return idEl ? idEl.innerText : null;
}

Student.deleteStudent_ = function(studentID) {
  if (!studentID) return Promise.reject();

  const options = {
    method: 'POST',
    credentials: 'same-origin'
  }
  const request = new Request(
    '/student?id=' + studentID + '&_method=delete', options);
  return fetch(request);
}
