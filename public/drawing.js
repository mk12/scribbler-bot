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
		}
	}
}

// Connecting two given points.
function connect(a, b, c, d) {
	context.beginPath();
	context.moveTo(a,b)
	context.lineTo(c,d);
	context.strokeStyle = 'black';
	context.stroke();
}

// Draws an object on a canvas.
function draw() {
	context.clearRect(0, 0, canvas.width, canvas.height);
	for (var i = 0; i < points.length; i++) {
		var x = points[i].x;
		var y = points[i].y;
		if (i < points.length - 1) {
			var next_x = points[i+1].x;
			var next_y = points[i+1].y;
			connect(next_x, next_y, x, y);
		}
		context.fillStyle = (i == 0) ? 'red' : 'black';
		context.beginPath();
		context.arc(x, y, radius, 0, Math.PI * 2);
		context.fill();
	}
}

// Returns the square of the distance between the points (x1,y1) and (x2,y2).
function distanceSquared(x1, y1, x2, y2) {
	return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
}

// Check if the position where mouse is clicked contains a dot
function thereIsPoint(pos){
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
}

// Erasing the work on the canvas.
function clearCanvas() {
	addAction({kind: 'clear'});
	generatePoints();
	draw();
	setButtonStates();
}

// Undo the move user made.
function undoCanvas() {
	if (actionIndex == 0) {
		return;
	}
	actionIndex--;
	generatePoints();
	draw();
	setButtonStates();
}

function redoCanvas() {
	if (actionIndex == actions.length) {
		return;
	}
	actionIndex++;
	generatePoints();
	draw();
	setButtonStates();
}

// Converts a client mouse position to canvas coordinates.
function canvasPosition(pos) {
	return {
		x: pos.clientX - canvas.offsetLeft,
		y: pos.clientY - canvas.offsetTop
	};
}

function onMouseDown(pos) {
	var p = canvasPosition(pos);
	if (!thereIsPoint (pos)) {
		addAction({kind: 'point', x: p.x, y: p.y});
		generatePoints();
		draw();
		setButtonStates();
	} else if (thereIsPoint (pos) ){
		allow = true;
	}
}

function onMouseUp(pos) {
	var p = canvasPosition(pos);
	if (allow) {
		addAction({kind: 'move', i: index, x: p.x, y: p.y});
		generatePoints();
		draw();
		setButtonStates();
	}
	allow = false;
}

function onMouseMove(pos) {
	var p = canvasPosition(pos);
	if (allow) {
		points[index].x = p.x;
		points[index].y = p.y;
		draw();
	}
}
