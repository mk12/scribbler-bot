// Copyright 2014 Mitchell Kember. Subject to the MIT License.

// Keep track of lines in the console.
var consoleLines = 0;
var scrolling = true;

// Adds a line of text to the console, and (optionally) scrolls down to it.
function addToConsole(text) {
	var console = document.getElementById('console');
	if (consoleLines > 0) {
		console.innerHTML += '\n';
	}
	console.innerHTML += " [" + consoleLines + "] " + text;
	if (scrolling) {
		console.scrollTop = console.scrollHeight;
	}
	consoleLines++;
}

// Clears the console and resets the counter.
function clearConsole() {
	var console = document.getElementById('console');
	console.innerHTML = "";
	consoleLines = 0;
}

// Enable or disable a button by its element ID.
function setEnabled(id, yes) {
	document.getElementById(id).className = yes? '' : 'disabled-button';
}

// Toggles the auto-scrolling whenever a new line is added to the console.
function btnFreeScroll() {
	btn = document.getElementById('btnfreescroll');
	if (scrolling) {
		btn.innerHTML = 'Scroll';
	} else {
		btn.innerHTML = 'Free';
	}
	scrolling = !scrolling;
}

// Keep track of the currently executing program.
var currentProgram = 'avoid';
var allPrograms = ['avoid', 'other'];

// Disables the specified program button and enables the rest.
function enableOtherPrograms(name) {
	setEnabled('btn' + name, false);
	for (var i = 0, len = allPrograms.length; i < len; i++) {
		if (allPrograms[i] != name) {
			setEnabled('btn' + allPrograms[i], true);
		}
	}
}

// Tells the server to switch programs. Disables the clicked button and enables
// the others (only one can be selected at a time).
function switchProgram(name) {
	if (name == currentProgram) {
		// This is impossible.
		return;
	}
	enableOtherPrograms(name);
	send('program:' + name);
}

// Keep track of the state of program execution.
var running = false;

// Sets the text of the start/stop button according to the action.
function setStartStop(start) {
	var btn = document.getElementById('btnstartstop');
	if (start) {
		btn.innerHTML = 'Start';
	} else {
		btn.innerHTML = 'Stop';
	}
}

// Tells the server to start/stop the program. Changes the text of the button
// and enables/disables the reset button accordingly.
function btnStartStop() {
	if (running) {
		setStartStop(true);
		running = false;
		send('control:stop');
	} else {
		setStartStop(false);
		setEnabled('btnreset', true);
		running = true;
		send('control:start');
	}
}

// Tells the server to stop and reset the program. Changes the text of the
// start/stop button and disables itself.
function btnReset() {
	setStartStop(true);
	setEnabled('btnreset', false);
	send('control:reset');
	running = false;
}

// Sends a message to the server and adds the response to the console.
function send(message) {
	post(message, function(text) {
		addToConsole(text);
	});
}

// Requests the latest status from the server, adds the response to the console,
// and repeats immediately. There is no delay because the server uses
// long-polling, so the connection will stay open until there is a new status.
function updateStatus() {
	post('long:status', function(text) {
		addToConsole(text);
		updateStatus();
	});
}

// Synchronizes the client state with the server.
function synchronize() {
	post('short:sync', function(text) {
		var vals = text.split(' ');
		var sProgram = vals[0];
		var sRunning = (vals[1] == 'True');
		if (currentProgram != sProgram) {
			enableOtherPrograms(sProgram);
		}
		if (running != sRunning) {
			setStartStop(!sRunning);
		}
		currentProgram = sProgram;
		running = sRunning;
	})
}

// Sends data to the server via a POST request. Calls the onreceive function
// with the response text as the argument when the request is completed.
function post(data, onreceive) {
	var r = new XMLHttpRequest();
	r.onreadystatechange = function() {
		if (r.readyState == 4 && r.status == 200) {
			onreceive(r.responseText);
		}
	}
	r.open('POST', '/', true);
	r.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	r.send(data);
}

window.onload = function() {
	synchronize();
	addToConsole('in sync with server');
	// Begin the long-polling.
	updateStatus();
}
