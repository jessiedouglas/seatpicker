const main = () => {
	const defaultTableSize = 6;
	seatStudents(defaultTableSize);

	const layoutDropdown = document.querySelector(".seating-layout-select");
	layoutDropdown.addEventListener("change", rearrangeTables);

	const saveButton = document.getElementById("save");
	saveButton.addEventListener("click", saveArrangement);

	const c = document.getElementsByClassName("container");
	const containers = [];
	for (let i=0; i<c.length; i++) {
		containers.push(c[i]);
	}

	dragula(containers, {
	  direction: 'horizontal',
	  revertOnSpill: true,
	});
}

const seatStudents = (tableSize) => {
	const studentEls = getStudentElements();
	console.log(studentEls);

	const room = document.getElementById("room");
	room.innerHTML = "";
	const numTables = Math.ceil(studentEls.length / tableSize);
	let table, pair;
	for (let i = 0; i < numTables; i++) {
		table = createTableElement();
		for (let j = 0; j < tableSize; j += 2) {
			pair = createPairElement();
			const nextStudentIndex = tableSize * i + j;
			const student1 = nextStudentIndex < studentEls.length ?
					studentEls[nextStudentIndex] : createStudentElement();
			const student2 = nextStudentIndex + 1 < studentEls.length ?
					studentEls[nextStudentIndex + 1] : createStudentElement();
			pair.append(student1);
			pair.append(student2);
			table.append(pair);
		}
		room.append(table);
	}
}

/** Returns all student elements that actually contain student information. */
const getStudentElements = () => {
	const allStudentEls = Array.from(document.querySelectorAll("#room .student"));
	return allStudentEls.filter(el => el.id !== "");
}

const createTableElement = () => {
	const table = document.createElement("div");
	table.classList.add("table");
	return table;
}

const createPairElement = () => {
	const pair = document.createElement("div");
	pair.classList.add("pair");
	pair.classList.add("container");
	return pair;
}

const createStudentElement = () => {
	const student = document.createElement("div");
	student.classList.add("student");
	return student;
}

const rearrangeTables = (e) => {
	const tableSize = +e.target.value;
	console.log(tableSize);
	if (tableSize === 0 || isNaN(tableSize)) {
		return;
	}
	seatStudents(tableSize);
}

const saveArrangement = (e) => {
	e.preventDefault();
	let elName, table, students;
	const keys = [];
	for (let i=0; i<5; i++) {
		elName = i.toString() + ".0";
		table = document.getElementsByName(elName)[0];
		students = table.children;
		for (const j=0; j<students.length; j++) {
			keys.push(students[j].id);
		}
	}
	const keyStringEl = document.getElementsByName("keystring")[0];
	keyStringEl.value = keys.join(",");

	e.target.parentElement.parentElement.submit();
}
