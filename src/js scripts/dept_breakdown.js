/*
	dynamically insert content for dept.html
	By: Bill Shi
*/

// create html with a department's summary infomation
function createDepartmentSummary(dept_code) {
	let dept_info = dept_summary[dept_code];
	
	return $(`<li class='summary'>
	<p><b>${dept_info['departmentName']}&nbsp;(${dept_code})</b></p>
	<table>
		<tr>
			<td>Online Sections:</td>
			<td>${dept_info['onlineSections'].toLocaleString()}</td>
			<td>In Person Sections:</td>
			<td>${dept_info['inPersonSections'].toLocaleString()}</td>
		</tr>
		<tr>
			<td>Online Seats:</td>
			<td>${dept_info['onlineSeats'].toLocaleString()}</td>
			<td>In Person Seats:</td>
			<td>${dept_info['inPersonSeats'].toLocaleString()}</td>
		</tr>
	</table>
	</li>
	<hr>`);
}


// run when webpage html elements are loaded
$(document).ready(function () {
	
	// set footer text
	$('#footer').text(`2020. Ethan Schaffer, Bill Shi. Last updated ${last_updated}`);
	
	// add html for each department's summary
	for (dept_code in dept_summary) {
		$('#summary-list').append(createDepartmentSummary(dept_code));
	}
})