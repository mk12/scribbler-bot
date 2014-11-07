// Copyright 2014 Justin Kim and Mitchell Kember. Subject to the MIT License.

// Global Variables
var points_x = [];
var points_y = [];
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
  addEventListeners();
};


// When mouse is clicked,
function addEventListeners() {
  canvas.addEventListener('mousedown', onMouseDown, false);
  canvas.addEventListener('mouseup', onMouseUp, false);
  canvas.addEventListener('mousemove', onMouseMove, false);
}

// When mouse is released.
function removeEventListeners() {
  canvas.removeEventListener('mousedown', onMouseDown);
  canvas.removeEventListener('mouseup', onMouseUp);
  canvas.removeEventListener('mousemove', onMouseMove);
}

// Adds an action to action array to keep track of user's input.
function addAction(a) {
  // To forget about undone actions when it is undone.
  while (actions.length > actionIndex) {
    actions.pop();
  }
  actions.push(a);
  actionIndex++;
}

// Perform a task; connecting dots, dragging dots, or clear.
function generatePoints() {
  points_x = [];
  points_y = [];
  for (var i = 0; i < actionIndex; i++) {
    var a = actions[i];
    if (a.kind == 'point') {
      points_x.push(a.x);
      points_y.push(a.y);
    } else if (a.kind == 'move') {
      points_x[a.i] = a.x;
      points_y[a.i] = a.y;
    } else if (a.kind == 'clear') {
      points_x = [];
      points_y = [];
    }
  }
}

// Connecting two given points
function connect(a,b,c,d) {
  context.moveTo (a,b)
  context.lineTo (c,d);
  context.strokeStyle = '#000';
  context.stroke ();
}

// Draws an object on a canvas.
function draw() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  var i;
  for (i = 0; i< points_x.length; i ++) {
    context.beginPath ();
    context.arc (points_x[i],points_y[i],radius, 0, Math.PI * 2);
    context.fill ();
    if (i > 0)
      connect (points_x [i-1], points_y [i-1], points_x[i], points_y[i]);
  }
}

// Returns the square of the distance between the points (x1,y1) and (x2,y2).
function distanceSquared(x1, y1, x2, y2) {
  return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
}

// Check if the position where mouse is clicked contains a dot
function thereIsPoint(pos){
    index = 0;
    var px = pos.clientX;
    var py = pos.clientY;
    var rad = clickRadius * clickRadius;
    while (index < points_x.length) {
        if (distanceSquared(px, py, points_x[index], points_y[index]) < rad)
            return true;
        index ++;
    }
    return false;
}

// Erasing the work on the canvas.
function clearCanvas() {
  addAction({kind: 'clear'});
  generatePoints();
  draw();
}

// Undo the move user made.
function undoCanvas() {
  if (actionIndex == 0) {
    return;
  }
  actionIndex--;
  generatePoints();
  draw();
}

function redoCanvas() {
  if (actionIndex == actions.length) {
    return;
  }
  actionIndex++;
  generatePoints();
  draw();
}

function onMouseDown(pos) {
  if (!thereIsPoint (pos)) {
   addAction({kind: 'point', x: pos.clientX, y: pos.clientY});
   generatePoints();
   draw();
  } else if (thereIsPoint (pos) ){
    allow = true;
  }

}

function onMouseUp(pos) {
  if (allow) {
    addAction({kind: 'move', i: index, x: pos.clientX, y: pos.clientY});
    generatePoints();
    draw();
  }
  allow = false;
  first = false;
}

function onMouseMove (pos){
  if (allow) {
    points_x[index] = pos.clientX;
    points_y[index] = pos.clientY;
    draw();
  }
}
