// Copyright 2014 Justin Kim and Mitchell Kember. Subject to the MIT License.

// Global Variables
var points = [];
var actions = [];
var actionIndex = 0;
var radius = 5;
var clickRadius = 15;
var canvas, context;
var index;
var allow = false;
var delMode = false;

// Sets up the canvas and context global variables.
function setupCanvas() {
	canvas = document.getElementById('canvas');
	context = canvas.getContext('2d');
	fixRetina();
	setButtonStates();
}

// Makes the canvas look nice on Retina displays.
function fixRetina() {
	var scaleFactor = backingScale(context);
	if (scaleFactor > 1) {
		canvas.width = canvas.width * scaleFactor;
		canvas.height = canvas.height * scaleFactor;
		context = canvas.getContext('2d');
		context.scale(scaleFactor, scaleFactor);
	}
}

// Taken from https://developer.apple.com/library/safari/documentation/
// audiovideo/conceptual/html-canvas-guide/SettingUptheCanvas/
// SettingUptheCanvas.html
function backingScale(context) {
	if ('devicePixelRatio' in window && window.devicePixelRatio > 1) {
		return window.devicePixelRatio;
	}
	return 1;
}

function addEventListeners() {
	canvas.addEventListener('mousedown', onMouseDown, false);
	canvas.addEventListener('mouseup', onMouseUp, false);
	canvas.addEventListener('mousemove', onMouseMove, false);
}

function removeEventListeners() {
	canvas.removeEventListener('mousedown', onMouseDown);
	canvas.removeEventListener('mouseup', onMouseUp);
	canvas.removeEventListener('mousemove', onMouseMove);
}

// Returns true if there are enough points to send.
function enoughPoints() {
	return points.length > 1;
}

// Returns a converted points array with the origin in the bottom-left.
function convertPoints() {
	return points.map(function(p) {
		return {x: p.x, y: canvas.style.height - p.y};
	});
}

// Adds an action to action array to keep track of user's input.
function addAction(a) {
	// To forget about undone actions when a new action is performed.
	while (actions.length > actionIndex) {
		actions.pop();
	}
	actions.push(a);
	actionIndex++;
}

// Regenerates points, draws them, and updates the button states.
function render() {
	generatePoints();
	draw();
	setButtonStates();
}

// Performs an action and then renders the app.
function perform(a) {
	addAction(a);
	render();
}

// Perform a task: connecting dots, dragging dots, or clear.
function generatePoints() {
	points = [];
	for (var i = 0; i < actionIndex; i++) {
		var a = actions[i];
		if (a.kind == 'point') {
			points.push({x: a.x, y: a.y})
		} else if (a.kind == 'move') {
			points[a.i].x = a.x;
			points[a.i].y = a.y;
		} else if (a.kind == 'clear') {
			points = [];
		} else if (a.kind == 'del') {
			points.splice(a.i, 1);
		}
	}
}

// Draws a dot centred at p, optionally filled with red (otherwise black).
function drawDot(p, fillRed) {
	context.fillStyle = fillRed? 'red' : 'black';
	context.beginPath();
	context.arc(p.x, p.y, radius, 0, Math.PI * 2);
	context.fill();
}

// Connecting two given points.
function drawLine(p1, p2) {
	context.beginPath();
	context.moveTo(p1.x, p1.y)
	context.lineTo(p2.x, p2.y);
	context.strokeStyle = 'black';
	context.stroke();
}

// Draws an object on a canvas.
function draw() {
	context.clearRect(0, 0, canvas.width, canvas.height);
	for (var i = 0; i < points.length; i++) {
		if (i < points.length - 1) {
			drawLine(points[i], points[i+1]);
		}
		drawDot(points[i], i == 0);
	}
}

// Returns the square of the distance between the points (x1,y1) and (x2,y2).
function distanceSquared(x1, y1, x2, y2) {
	return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
}

// Check if the position where mouse is clicked contains a dot
function isPointAt(pos){
	index = 0;
	var p = canvasPosition(pos);
	var rad = clickRadius * clickRadius;
	while (index < points.length) {
		var point = points[index];
		if (distanceSquared(p.x, p.y, point.x, point.y) < rad)
			return true;
		index++;
	}
	return false;
}

// Sets the enabled/disabled state of the undo and redo buttons.
function setButtonStates() {
	setEnabled('btnd-undo', actionIndex != 0);
	setEnabled('btnd-redo', actionIndex < actions.length);
	setEnabled('btnd-clear', points.length > 0);
	setActive('btnd-del', delMode);
}

// Clears all points from the canvas.
function clearCanvas() {
	perform({kind: 'clear'});
}

// Undos the user's most recent action.
function undoCanvas() {
	if (actionIndex == 0)
		return;
	actionIndex--;
	render();
}

function redoCanvas() {
	if (actionIndex == actions.length)
		return;
	actionIndex++;
	render();
}

// Converts a client mouse position to canvas coordinates.
function canvasPosition(pos) {
	return {
		x: pos.clientX - canvas.offsetLeft,
		y: pos.clientY - canvas.offsetTop
	};
}

function onMouseDown(pos) {
	if (!isPointAt(pos)) {
		if (!delMode) {
			var p = canvasPosition(pos);
			perform({kind: 'point', x: p.x, y: p.y});
		}
	} else if (isPointAt(pos)){
		if (delMode) {
			perform({kind: 'del', i: index});
		} else {
			allow = true;
		}
	}
}

function onMouseUp(pos) {
	if (!allow || delMode)
		return;
	var p = canvasPosition(pos);
	perform({kind: 'move', i: index, x: p.x, y: p.y});
	allow = false;
}

function onMouseMove(pos) {
	if (!allow || delMode)
		return;
	var p = canvasPosition(pos);
	points[index].x = p.x;
	points[index].y = p.y;
	draw();
}

// Toggles the point adding/deleting function.
function toggleDelete() {
	delMode = !delMode;
	setActive('btnd-del', delMode);
}
