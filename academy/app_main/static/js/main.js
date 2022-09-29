
//-------------------------------------------------------------------------
function click_image(input) {		//реакция на загрузку фотографии
	data = get_click_image(input);
	if(isErrorData(data))
		return;
	fr = new FileReader();	
	fr.onload = function () {		
		data["pic"] = Array.from(new Uint8Array(fr.result));
		sendPOST(data);
	};	
	fr.readAsArrayBuffer(input.files[0]);
}
function get_click_image(input) {
	tp = input.files[0].type;
	if(input.files[0].size <= Math.pow(2, 20) && (tp == "image/jpeg" || tp == "image/png")) 
		return {"type": tp.split("/")[1]}
	return {"error" : "Фото должно быть формата jpeg или png, размером не более 1 Мб"};
}
//-------------------------------------------------------------------------	
function click_change_info() {			//реакция на изменение данных
	data = get_click_change_info();
	if(isErrorData(data))
		return;
	sendPOST(data);
}
function get_click_change_info() {
	
	
	
	
	login = validation("reg_login");
	pass = validation("reg_password");
	pass2 = validation("reg_password_2");
	phone = validation("reg_phone");
	e_mail = validation("reg_e_mail");
	
	
	
	
	if(login != undefined) {
		if(login == "")
			return {"error": "Некорректный логин или его длина (8...20 символов)."};
		if(pass == "")
			return {"error": "Некорректный пароль или его длина (8...20 символов)."};	
		if(pass2 != undefined) {
			if(pass != pass2)
				return {"error": "Новые варианты паролей не совпадают."};	
		}
		return {"login": encodeInfo(login, pass)};			
	}
	if(phone != undefined) {
		phone = phone.split("-").join("");
		if(phone.length < 12)
			return {"error": "Ошибочный телефон. Допустимый формат: '+X-XXX-XXX-XX-XX'."};	
		if(e_mail == "")
			return {"error": "Явно ошибочная электронная почта."};		
		return {"phone": phone, "e_mail": e_mail};	
	}
	return {"error": "Ошибка валидации введенного текста."}

}

function validation(id){
	el = document.getElementById(id);
	if(! el)
		return undefined;
	mask = {
		"reg_login": "^[A-Za-z0-9]{8,20}$",
		"reg_password": "^[A-Za-z0-9]{8,20}$",
		"reg_password_2": "^[A-Za-z0-9]{8,20}$",
		"reg_phone": "^[+][0-9\-]{11,}$",
		"reg_e_mail": "^[0-9A-Za-z\._\-]+@[0-9A-Za-z._-]+[.][0-9A-Za-z._-]+$",
		"reg_date": "^[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}$"
	};
	str = el.value;
	console.log(str, mask[id], new RegExp(mask[id]));
	
	try {
		if(str.match(new RegExp(mask[id])))
			return str;
	}
	catch(err) {
		
	}
	return "";
}


//-------------------------------------------------------------------------	
function click_schedule() {		//реакция на установку расписания
	data = get_click_schedule();
	if(isErrorData(data))
		return;
	sendPOST(data);	
}

function click_edit_schedule() { //реакция на установку изменения расписания
	data = get_click_edit_schedule();
	if(isErrorData(data))
		return;
	sendPOST(data);
}


function get_click_schedule() {
	dt = getDate(validation("reg_date"));
	bg = getDate(document.getElementById("begin").innerHTML);
	ed = getDate(document.getElementById("end").innerHTML);
	if(!dt)
		return {"error": "Ошибка ввода данных. Формат даты: ДД.ММ.ГГГГ"};
	if(dt < bg || dt > ed)
		return {"error": "Ошибка ввода данных. Дата первого занятия вне срока обучения"};
	sel = document.getElementsByTagName("select")
	temp = {"times": [], "professor": []};
	for(i=0; i<sel.length; ++i)
		temp[sel[i].id].push(sel[i].value);
	if(temp["professor"]=="")
		return {"error": "Ошибка ввода данных. Не выбран преподаватель"};
	prof = Number(temp["professor"][0].split("_")[1]);	
	tm = new Array(temp["times"].length)
	am = 0;
	for(i=0; i<tm.length; ++i) {
		a = temp["times"][i].split("_");
		tm[Number(a[1])-1] = Number(a[2]);
		am += Number(a[2]);
	}
	if(am==0)
		return {"error": "Ошибка ввода данных. Не выбрано время занятий"};

	
	if(getLesson(dt, tm) == 0)
		return {"error": "Ошибка ввода данных. Не выбрано время первого занятия"};
	am = Number(document.getElementById("amount").innerHTML);	
	les = [];
	while(les.length != am) {
		d = getLesson(dt, tm);
		if(d != 0) 
			les.push([[dt.getFullYear(), dt.getMonth()+1, dt.getDate()].join("-"), d]);
		dt = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()+1);
	}
	if((new Date(les[les.length - 1][0])) > ed)
		return {"error": "Ошибка ввода данных. Дата последнего занятия вне срока обучения"};	
	return {
		"professor": prof,
		"lessons": les};
}



function get_click_edit_schedule() {
	dt = getDate(validation("reg_date"));
	if(!dt)
		return {"error": "Ошибка ввода данных. Формат даты: ДД.ММ.ГГГГ"};
	tm = document.getElementById("times").value;
	prof = document.getElementById("professor").value;
	if(prof == "")
		return {"error": "Ошибка ввода данных. Не выбран преподаватель"};
	tm = Number(tm.split("_")[1]);
	prof = Number(prof.split("_")[1]);	
	return {
		"professor": prof,
		"lesson": [[dt.getFullYear(), dt.getMonth()+1, dt.getDate()].join("-"), tm]};
}
function getLesson(dt, tm) {
	d = dt.getDay();
	if(d == 0) d = 7;
	return tm[d-1];	
}

function getDate(str) {
	var dt = str.split(".")
	if(dt.length != 3)
		return null;
	for(i=0; i<3; ++i) {
		dt[i] = Number(dt[i]);
		if(dt[i]==NaN)
			return null;		
	}
	temp = new Date(dt[2], dt[1]-1, dt[0])
	if(temp.getFullYear() != dt[2] || temp.getMonth()+1 != dt[1] || temp.getDate() != dt[0])
		return null;
	return temp;
}


//-------------------------------------------------------------------------	
function isNavigationKey(k) {
	return (k == 8 || k == 46 || k == 37 || k == 39) 
}
	
function key_down_text(event) {
	if(isNavigationKey(event.keyCode)) 
		return; 	
	mask = {
		"reg_login": "^[0-9A-Za-z]$",
		"reg_password": "^[0-9A-Za-z]$",
		"reg_password_2": "^[0-9A-Za-z]$",
		"reg_phone": "^[0-9\-\+]$",
		"reg_e_mail": "^[0-9A-Za-z.@_-]$",
		"reg_date": "^[0-9.]$"
	};
	try {
		event.returnValue = event.key.match(new RegExp(mask[event.target.id]));
	}
	catch(err) {
		event.returnValue = false;
	}
}
function encodeInfo(lg, pw) {
	a = [lg.substring(0, 5), lg.substring(5), pw.substring(0, 3), pw.substring(3)];	
	return a[0]+a[3]+a[2]+a[1];
}
//-------------------------------------------------------------------------
function click_registration(q) {	//реакция на регистрацию
	if (q.id == "login")
		data = {"login": getCookie("login")};			
	else
		data = get_click_change_info(); 	
	if(isErrorData(data))
		return;	
	sendPOST(data);		
}
//---------------------------------------------------
function click_sort(param) {	
	arr = new Array(document.getElementsByClassName("rows").length)
	for(i=0; i<arr.length; ++i) {
		n = document.getElementById("n"+i);
		m = Number(document.getElementById("m"+i).innerHTML);
		arr[i] = [n.getElementsByTagName("a")[0].innerHTML, m, n.innerHTML]; 		
	}
	if(param == 'fio')
		arr.sort((a, b)=>(a[0].localeCompare(b[0])));
	else
		arr.sort((a, b)=>(a[1] > b[1] ? -1:1));
	for(i=0; i<arr.length; ++i) {
		document.getElementById("n"+i).innerHTML = arr[i][2];
		document.getElementById("m"+i).innerHTML = arr[i][1].toFixed(2);
	}
}
//---------------------------------------------------
function click_arrow(q) {
	path = document.location.pathname.split("/");
	el = path[path.length - 1];
	y = Number(el.substring(0, 4));
	m = Number(el.substring(4));
	switch(q.id) {
		case "yeaLeft":
			--y;
		break;
		case "yeaRight":
			++y;
		break;
		case "monLeft":
			--m;
			if(m == 0){
				--y;
				m = 12;
			}				
		break;
		case "monRight":
			++m;
			if(m == 13) {
				++y;
				m = 1;
			}
	}
	m = String(m);
	if(m.length == 1)
		m = "0" + m;
	path[path.length - 1] = String(y) + m;
	document.location.href = path.join("/");
}

function click_calendar(q) {
	info = JSON.parse(q.dataset.info)
	str = info["day"];
	if(info["weekend"] != "")
		str = "<span class='calendar_weekend'>" + str + ". " + info["weekend"] + "</span>";	
	try {
		str += "<br /><table>";
		for(el of info["events"]) {
			str += "<tr><td class='calendar_info'>&#x2713</td>"
			for(i=0; i<el.length; ++i)
				str += ("<td class='calendar_info'>" + el[i] + "</td>");
			str += "</tr>"		
		}
		str+= "</table>";
	}
	catch(err) {}
	document.getElementById("calender_info").innerHTML = str;
}	
//---------------------------------------------------
function click_go_person(q) {
	a = document.location.pathname.split("/");
	if(a[1] == "loginas") 
		a[1] = "work";
	else 
		a[a.length] = a[a.length-1];
	
	a[a.length - 1] = q.id;
	window.location.href = a.join("/");	
}
function click_abc(q) {
	
	el =q.id.split("_")[1];
	a = document.location.pathname.split("/");
	if(isNaN(Number(el))) 
		a[a.length - 2] = el;
	else
		a[a.length - 1] = el;
	window.location.href = a.join("/");
}
//---------------------------------------------------

function click_block(q) {
	data = get_click_block(q);
	if(isErrorData(data))
		return;
	sendPOST(data);
}
function get_click_block(q) {
	res = {"action": q};
	if(q == 2){
		el = document.getElementById("choice");
		if(el.value == "")
			return {"error": "Укажите место вакансии"};
			res["id"]=Number(el.value);	
	}	
	return res; 
}


//---------------------------------------------------
function getCookie(cook) {		//получить логин из cookie
	dt = document.cookie.split(";");
	for(i=0; i < dt.length; ++i) {
		temp = dt[i].trim().split("=");
		if(temp[0]==cook)
			return temp[1];
	}
	return "";
}

function sendPOST(data) {
	click_disabled();
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		response_go(temp);
	});
}
function createPOST(data, accept='text/html') {	//структура пост запроса
	csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
	res = { 
		method: 'POST',
		body: JSON.stringify(data), 				
		headers: {
			'X-CSRFToken': csrftoken,
			'Accept': accept,					
			'Content-Type': 'application/json'}			
		}
	return res;
}
function response_go(mes) {			//обработка ответа пост запроса
	temp = mes.split("\n")
	if(temp.length == 1)
		window.location.href = mes;
	else
		errorMessage(temp[1])
}
//-------------------------------------------------------------------------	
function isErrorData(data) {
	if(data["error"]) {
		errorMessage(data["error"]);
		return true;
	}
	return false;
}
function errorMessage(mes) {
	el = document.getElementById("bottom");
	el.innerHTML = "";
	temp = document.createElement("div");
	temp.classList.add("error_message");
	temp.innerHTML = mes;
	el.appendChild(temp);
}

function click_disabled() {
	disabledTag("input", true);
	disabledTag("select", true);
	errorMessage("Ждите ответ от сервера...");
}
function click_enabled() {
	disabledTag("input", false);
	disabledTag("select", false);
	document.getElementById("bottom").innerHTML = "Ответ от сервера получен.";
}
function disabledTag(tag, dis) {
	inp = document.getElementsByTagName(tag)
	for(i=0; i<inp.length; ++i)
		inp[i].disabled = dis;
}
//-------------------------------------------------------------------------	

function click_edit_marks() {				//реакция на изменение оценок
	data = get_click_edit_marks();
	if(isErrorData(data))
		return;
	sendPOST(data);
}

function get_click_edit_marks() {		
	sel = document.getElementsByTagName("select");
	data = []
	for(i=0; i<sel.length; ++i) {
		if(sel[i].value != "")
			data.push([Number(sel[i].id), Number(sel[i].value)]);	
	}
	if(data.length == 0) 
		return {"error": "Не поставлено ни одной оценки."};
	return  data;  
}

//-------------------------------------------------------------------------	






















