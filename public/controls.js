// Copyright 2014 Mitchell Kember. Subject to the MIT License.

// How often to synchronize with the server (ms).
var syncInterval = 10000;

// Timeout for AJAX requests (ms).
var ajaxTimeout = 30000;

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

// Returns true if the button is enabled and false otherwise.
function isEnabled(id) {
	return document.getElementById(id).className != 'disabled-button';
}

// Enable or disable a button by its element ID.
function setEnabled(id, yes) {
	document.getElementById(id).className = yes? '' : 'disabled-button';
}

// Toggles the auto-scrolling whenever a new line is added to the console.
function btnFreeScroll() {
	btn = document.getElementById('btnc-freescroll');
	if (scrolling) {
		btn.innerHTML = 'Scroll';
	} else {
		btn.innerHTML = 'Free';
	}
	scrolling = !scrolling;
}

// Keep track of the currently executing program.
var currentProgram = 'tracie';
var allPrograms = ['avoid', 'tracie'];

// Disables the specified program button and enables the rest.
function enableOtherPrograms(name) {
	setEnabled('btnc-' + name, false);
	for (var i = 0, len = allPrograms.length; i < len; i++) {
		if (allPrograms[i] != name) {
			setEnabled('btnc-' + allPrograms[i], true);
		}
	}
}

// Tells the server to switch programs. Disables the clicked button and enables
// the others (only one can be selected at a time).
function switchProgram(name) {
	if (name == currentProgram) {
		return;
	}
	enableOtherPrograms(name);
	setStartStop(true);
	setEnabled('btnc-reset', false);
	send('program:' + name);
	currentProgram = name;
}

// Keep track of the state of program execution.
var running = false;

// Sets the text of the start/stop button according to the action.
function setStartStop(start) {
	var btn = document.getElementById('btnc-startstop');
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
		setEnabled('btnc-reset', true);
		running = true;
		send('control:start');
	}
}

// Tells the server to stop and reset the program. Changes the text of the
// start/stop button and disables itself.
function btnReset() {
	if (isEnabled('btnc-reset')) {
		setStartStop(true);
		setEnabled('btnc-reset', false);
		send('control:reset');
		running = false;
	}
}

// Changes the value of a parameter in the program based on the text fields.
function setParameter() {
	var name = document.getElementById('c-param-name').value;
	var val = document.getElementById('c-param-value').value;
	send('set:' + name + '=' + val);
}

// Sends a message to the server and adds the response to the console.
function send(message) {
	post(message, function(text) {
		addToConsole(text);
		synchronize();
	}, function() {
		addToConsole(message + " timed out");
	});
}

// Requests the latest status from the server, adds the response to the console,
// and repeats immediately. There is no delay because the server uses
// long-polling, so the connection will stay open until there is a new status.
function updateStatus() {
	post('long:status', function(text) {
		addToConsole(text);
		updateStatus();
	}, function() {
		updateStatus();
	});
}

// Synchronizes the client state with the server.
function synchronize() {
	post('short:sync', function(text) {
		var vals = text.split(' ');
		var sProgram = vals[0];
		var sRunning = (vals[1] == 'True');
		var sCanReset = (vals[2] == 'True');
		enableOtherPrograms(sProgram);
		setStartStop(!sRunning);
		setEnabled('btnc-reset', sCanReset);
		currentProgram = sProgram;
		running = sRunning;
	}, function() {
		addToConsole("sync timed out");
	})
}

// Sends data to the server via a POST request. Calls the onreceive function
// with the response text as the argument when the request is completed.
function post(data, onreceive, ontimeout) {
	var r = new XMLHttpRequest();
	r.onreadystatechange = function() {
		if (r.readyState == 4 && r.status == 200) {
			onreceive(r.responseText);
		}
	};
	r.open('POST', '/', true);
	r.setRequestHeader('Content-type', 'application/json');
	r.timeout = ajaxTimeout;
	r.ontimeout = ontimeout;
	r.send(data);
}

// The currently active view, either the controls or the drawing view.
var activeView = 'controls';

// Sets the visibility of the element indicated by the given identifier.
function setVisible(id, visible) {
	document.getElementById(id).style.display = visible? 'block' : 'none';
}

// Toggles the currently visible view (the controls view or the drawing canvas).
function toggleView() {
	if (activeView == 'controls') {
		setVisible('controls', false);
		setVisible('drawing', true);
		activeView = 'drawing';
		addEventListeners();
	} else {
		setVisible('drawing', false);
		setVisible('controls', true);
		activeView = 'controls';
		removeEventListeners();
		send(JSON.stringify(points));
	}
}

window.onload = function() {
	synchronize();
	addToConsole("in sync with server");
	// Sync every so often.
	setInterval(synchronize, syncInterval);
	// Begin the long-polling.
	updateStatus();
	// Ensure that only one page is showing.
	setVisible('controls', true);
	setVisible('drawing', false);
	setupCanvas();
}
