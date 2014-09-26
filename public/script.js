// Poll the server's staus every 100 ms.
var statusPollingInterval = 100;

// Sends data to the server via a POST request. Calls the onreceive function
// with the response text as the argument when the request is completed.
function post(data, onreceive) {
	var r = new XMLHttpRequest();
	r.onreadystatechange = function() {
		if (r.readyState == 4 && r.status == 200) {
			onreceive(r.responseText);
		}
	}
	r.open("POST", "/", true);
	r.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	r.send(data);
}

// Sets the contents of the status box.
function setStatus(text) {
	document.getElementById("status").innerHTML = text;
}

// Gets the robot's status from the server, updates the status line HTML, and
// schedules another update.
function updateStatus() {
	post("status", function(text) {
		setStatus(text);
		// setTimeout(updateStatus, statusPollingInterval);
	});
}

// Tells the server to stop the robot.
function stop() {
	post("stop", function(text) {
		setStatus(text);
	});
}
