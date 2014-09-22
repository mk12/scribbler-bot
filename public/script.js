function stop() {
	var r = new XMLHttpRequest();
	r.onreadystatechange = function() {
		if (r.readyState == 4 && r.status == 200) {
			document.getElementById("status").innerHTML = r.responseText;
		}
	}
	r.open("POST", "server.py", true);
	r.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	r.send("");
}
