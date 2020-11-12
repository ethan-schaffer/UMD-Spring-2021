// simple front end
// by Bill Shi and Ethan Schaffer

// preferable if catalog is not an array
catalog = catalog[0];

function emptySearchFieldInfo() {
	//console.log("Here!")
	let course_container = 	$(`<div class='course-container'>
								<h3>Enter the four character name of a department (like "BSCI") or the course code of a class (like "CMSC132") to get info!</h3>
								<ul></ul>
							</div>`);
	return course_container;
}

//
function createCourseContainer(course_code) {
	let course_info = catalog[course_code];
	
	let learning_mode_filter = $('#filter-learning-mode').val();
	
	// creates course container
	let course_container = 	$(`<div class='course-container'>
								<h3>${course_code +' '+ course_info['course-name']}</h3>
								<ul></ul>
							</div>`);
	let ul = course_container.find('ul');
	
	// adds infomation about class sections to ul
	let sections = course_info['sections'];
	for (section_code in sections) {
		
		// append sections according to learning_mode_filter
		if (learning_mode_filter == 'all' || 
			learning_mode_filter == sections[section_code]['learning-mode']) {
			
			// string describing lecture time
			let lecture_info = '<br>';
			if (sections[section_code]['lecture-time'] != null) {
				lecture_info = `Lecture Section:<br>${sections[section_code]['lecture-time']}`;
			}
			
			// string describing dicussion time
			let lab_info = '<br>';
			if (sections[section_code]['lab-time'] != null) { 
				lab_info = "Lab/Dicussion Section:<br>" + sections[section_code]['lab-time'];
			}
			
			// create section data html container
			let section = 	$(`<li>
								<table class="section_table">
									<tr>
										<td>Section:<br>${section_code}</td>
										<td>Total Seats:<br>${sections[section_code]['capacity']}</td>
										<td>Taught by:<br>${sections[section_code]['instructor']}</td>
										<td>${lecture_info}</td>
										<td>${lab_info}</td>
										<td>Learning Type:<br><mark>${sections[section_code]['learning-mode']}</mark></td>
										<td>Seats Open:<br>${sections[section_code]['open-seats']}</td>
									</tr>
								</table>
							</li>`);
						
			ul.append(section);
		}
		
	}
	
	// return no html if no sections pass the filter
	if (ul.children().length == 0) {
		return null;
	} else {
		return course_container;
	}
}

//
function executeSearch() {
	let user_input = $('#class-lookup').val().toUpperCase();
		
	// clears search results
	$('#search-return').empty();

	// display search hint when input box is empty
	if (user_input == ""){
		$('#search-return').append(emptySearchFieldInfo());
	}
	
	for (course in catalog) {
		
		// user input describes a course code
		if (user_input == course) {
			$('#search-return').append(createCourseContainer(course));
			return;
		}
		
		// user input describes a department code
		if (user_input == catalog[course]['department']) {
			$('#search-return').append(createCourseContainer(course));
		}
		
	}
	
	// display a message if no results is returned
	if ($('#search-return').children().length == 0) {
		$('#search-return').append(`<li style='border: 3px solid black;'>
										<h3>Sorry, we couldn't find what you were looking for.</h3>
									</li>`)
	}
}

// wait until html elements are ready and execute code within
$(document).ready(function () {
	
	$('#footer').text(`2020. Ethan Schaffer, Bill Shi. Last updated ${last_updated}`);
	$('#search-return').append(emptySearchFieldInfo());
	
	
	// create behavior for when text is entered in the input box
	$('#class-lookup').on('input', executeSearch);
	
	// create behavior with user changes the instruction filter
	$('#filter-learning-mode').on('change', executeSearch);

})