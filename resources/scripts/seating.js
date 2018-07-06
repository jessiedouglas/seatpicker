function main() {
	var saveButton = document.getElementById("save");
	saveButton.onclick = saveArrangement;

	var c = document.getElementsByClassName("container");
	var containers = [];
	for (var i=0; i<c.length; i++) {
		containers.push(c[i]);
	}

	dragula(containers, {
	  direction: 'horizontal',
	  revertOnSpill: true,
	});
}

function saveArrangement(e) {
	e.preventDefault();
	var elName, table, students, keys = [];
	for (var i=0; i<5; i++) {
		elName = i.toString() + ".0";
		table = document.getElementsByName(elName)[0];
		students = table.children;
		for (var j=0; j<students.length; j++) {
			keys.push(students[j].id);
		}
	}
	var keyStringEl = document.getElementsByName("keystring")[0];
	keyStringEl.value = keys.join(",");
	e.target.parentElement.parentElement.submit();
}
