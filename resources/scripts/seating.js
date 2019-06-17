const SeatingConstants = {
	dragContainers: [],
	initializing: true,
};

const main = () => {
	seatStudentsInitial();

	const layoutDropdown = document.querySelector(".table-size-select");
	console.log(layoutDropdown);
	layoutDropdown.addEventListener("change", rearrangeTables);

	const saveButton = document.getElementById("save");
	saveButton.addEventListener("click", saveArrangement);

	const dragContainers = Array.from(
		document.getElementsByClassName("container"));
	// Create some extra potential dragula containers in case we need some extras
	// during reseating.
	const initialNumContainers = dragContainers.length;
	for (let i = 0; i < initialNumContainers; i++) {
		dragContainers.push(createPairElement());
	}

	dragula(dragContainers, {
	  direction: 'horizontal',
	  revertOnSpill: true,
	});
	SeatingConstants.dragContainers = dragContainers;
	SeatingConstants.initializing = false;
}

const seatStudentsInitial = () => {
	const tableSize = getTableSize();
	const studentsByTable = [];
	for (let table of document.querySelectorAll("#room .table")) {
		const students = Array.from(table.children);
		studentsByTable.push(students);
	}
	clearRoom();
	const room = document.getElementById("room");
	let table, tableEl, pair;
	for (let i = 0; i < studentsByTable.length; i++) {
		tableEl = createTableElement();
		table = studentsByTable[i];
		for (let j = 0; j < table.length; j += 2) {
			pair = createPairElement();
			pair.appendChild(table[j]);
			pair.appendChild(j + 1 < table.length ? table[j + 1] : createEmptyStudentElement());
			tableEl.appendChild(pair);
		}
		// Fill out the rest of the table with empty seats
		if (tableEl.children.length < tableSize / 2) {
			let difference = (tableSize / 2) - tableEl.children.length;
			while (difference > 0) {
				pair = createPairElement();
				pair.appendChild(createEmptyStudentElement());
				pair.appendChild(createEmptyStudentElement());
				tableEl.appendChild(pair);
				difference -= 2;
			}
		}
		room.appendChild(tableEl);
	}
}

const reseatStudents = (tableSize) => {
	const studentEls = getStudentElements();

	clearRoom();
	const room = document.getElementById("room");
	const numTables = Math.ceil(studentEls.length / tableSize);
	let table, pair;
	for (let i = 0; i < numTables; i++) {
		table = createTableElement();
		for (let j = 0; j < tableSize; j += 2) {
			pair = getEmptyPairElement();
			const nextStudentIndex = tableSize * i + j;
			const student1 = nextStudentIndex < studentEls.length ?
					studentEls[nextStudentIndex] : createEmptyStudentElement();
			const student2 = nextStudentIndex + 1 < studentEls.length ?
					studentEls[nextStudentIndex + 1] : createEmptyStudentElement();
			pair.appendChild(student1);
			pair.appendChild(student2);
			table.appendChild(pair);
		}
		room.appendChild(table);
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
	if (!SeatingConstants.initializing) {
		throw new Error(
			'Error: Tried to create a new pair element after dragula done ' +
			'initializing. Use getEmptyPairElement instead.');
	}
	const pair = document.createElement("div");
	pair.classList.add("pair");
	pair.classList.add("container");
	return pair;
}

const getEmptyPairElement = () => {
	for (let pair of SeatingConstants.dragContainers) {
		if (pair.innerHTML === "" || pair.innerHTML == null) {
			return pair;
		}
	}
}

const createEmptyStudentElement = () => {
	const student = document.createElement("div");
	student.classList.add("student");
	student.classList.add("empty");
	return student;
}

const rearrangeTables = (e) => {
	console.log('here');
	const tableSize = +e.target.value;
	if (tableSize === 0 || isNaN(tableSize)) {
		return;
	}
	resetTableSizeInForm(tableSize);
	reseatStudents(tableSize);
}

const resetTableSizeInForm = (tableSize) => {
	const inputs = document.getElementsByName("table_size");
	[].forEach.call(inputs, (input) => input.value = tableSize);
}

const clearRoom = () => {
	const room = document.getElementById("room");
	room.innerHTML = "";
	for (let pair of SeatingConstants.dragContainers) {
		pair.innerHTML = "";
	}
}

const getTableSize = () => {
	return +document.getElementsByName("table_size")[0].value;
}

const saveArrangement = (e) => {
	e.preventDefault();
	const tables = Array.from(document.getElementsByClassName("table"));
	const tableSize = getTableSize();
	const keysByTable = [];
	let keys;
	for (let table of tables) {
		keys = [];
		students = Array.from(table.getElementsByClassName("student"));
		if (students.length !== tableSize) {
			alert('You have a table with the wrong number of students. Please ' +
						'readjust and try again.');
			return;
		}
		students.forEach((student) => {
			keys.push(student.id ? student.id : "");
		});
		keysByTable.push(keys);
	}
	const keyStringEl = document.getElementsByName("keystring")[0];
	// [["a", "b"], ["c", "d"]] --> "a,b;c,d"
	keyStringEl.value = keysByTable.map(keys => keys.join(",")).join(";");

	e.target.parentElement.parentElement.submit();
}
