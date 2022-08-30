
//-------------------------------------------------------------------------
function click_image(input) {		//реакция на загрузку фотографии
	data = get_click_image(input);
	if(isErrorData(data))
		return;
	fr = new FileReader();
	click_disabled();
	fr.onload = function () {
		data["pic"] = Array.from(new Uint8Array(fr.result));
		fetch("", createPOST(data))
		.then(response => response.text())		
		.then(temp => {
			click_enabled();
			response_go(temp);
		});
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
function click_change_info(event) {			//реакция на изменение данных
	data = get_click_change_info();
	console.log(data);
	if(isErrorData(data))
		return;
	
	click_disabled();
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		response_go(temp);
		});
}
function get_click_change_info() {
	login = document.getElementById("reg_login");
	pass = document.getElementById("reg_password");
	pass2 = document.getElementById("reg_password_2");
	phone = document.getElementById("reg_phone");
	e_mail = document.getElementById("reg_e_mail");
	if(login) {		
		login = login.value;
		pass = pass.value;
		if(login.length < 8 || pass.length < 8 || login.length > 64 || pass.length > 64)
			return {"error": "Логин и пароль должны быть от 8-и до 64 символов."};
		if(pass2 && pass != pass2.value)
			return {"error": "Новые варианты паролей не совпадают."};	
		if(validation("reg_login", login) && validation("reg_password", pass))		
			return {"login": encodeInfo(login, pass)};
	}
	if(phone) {
		phone = phone.value.split("-").join("");
		e_mail = e_mail.value;
		temp = phone.split("+")
		if(phone.length < 12 || phone[0] != '+' || temp.length != 2) 	
			return {"error": "Ошибочный телефон. Допустимый формат: '+X-XXX-XXX-XX-XX'."};		
		temp = e_mail.split('@')
		if(e_mail.split(' ').length != 1 || temp.length != 2 || temp[1].split('.').length == 1)
			return {"error": "Явно ошибочная электронная почта."};
		if(validation("reg_phone", phone))	
			return {"phone": phone, "e_mail": e_mail};
	}
	return {"error": "Ошибка валидации введенного текста."}

}
//-------------------------------------------------------------------------	
function click_schedule() {		//реакция на установку расписания
	data = get_click_schedule();
	if(isErrorData(data))
		return;
	click_disabled();
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		response_go(temp);
		});
}
function get_click_schedule() {
	dt = getDate(document.getElementById("reg_date").value);
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
		"lessons": les,
	};
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

function validation(id, str){
	if(str == undefined)
		return false;
	mask = {
		"reg_login": "[A-Za-z0-9]",
		"reg_password": "[A-Za-z0-9]",
		"reg_password_2": "[A-Za-z0-9]",
		"reg_phone": "[0-9\-\+]",
		"reg_date": "[0-9.]"
	}
	mask = mask[id];
	if(mask) {
		temp = "^" + mask + "{" + str.length + "}$"
		try {
			return str.match(new RegExp(temp));
		}
		catch(err) {}
	}
	return true;	
}	
function key_down_text(event) {
	if(isNavigationKey(event.keyCode)) 
		return; 
	event.returnValue = validation(event.target.id, event.key)	
}
function encodeInfo(lg, pw) {
	a = [lg.substring(0, 5), lg.substring(5), pw.substring(0, 3), pw.substring(3)];	
	return a[0]+a[3]+a[2]+a[1];
}
//-------------------------------------------------------------------------
function click_registration(event) {	//реакция на регистрацию
	if (event.target.id == "login")
		data = {"login": getCookie("login")};			
	else
		data = get_click_change_info(); 	
	if(isErrorData(data))
		return;	
	click_disabled();	
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		response_go(temp);		
	}); 			
}

//---------------------------------------------------
function click_arrow(event) {
	path = document.location.pathname.split("/");
	el = path[path.length - 1];
	y = Number(el.substring(0, 4));
	m = Number(el.substring(4));
	switch(event.target.id) {
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

function click_calendar(event) {
	info = JSON.parse(document.getElementById("h" + event.target.id).value);
	str = info["day"];
	if(info["weekend"] != "")
		str = "<span class='text_red'>" + str + ". " + info["weekend"] + "</span>";
	for(el of info["events"])
		str += ("<br />" + el);	
	document.getElementById("calender_info").innerHTML = str;
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


















/* function getChoicePerson(name, ex=""){
	data = {"event": name};
	dep = document.getElementById('app_department');
	if(dep) {
		data["dep"] = getID(dep.value);
		if(ex != "dep") {
			data["sta"] = getID(document.getElementById('app_status').value);
			data["emp"] = getID(document.getElementById('app_employee').value);
			if(ex == "OK")
				if(data["dep"]==0 || data["sta"]==0)
					data = {"error": "Отдел и должность должны быть указаны."} 
				else
					data["OK"] = getCookie("login");
		}
		//TODO проверки
	}
	return data
}	
	
	


function getPersonalInfo() {
	id = document.getElementById("app_select").value;
	ln = document.getElementById("reg_lastname").value;
	fn = document.getElementById("reg_firstname").value;
	pt = document.getElementById("reg_patronymic").value;
	bd = document.getElementById("reg_birthday").value.split(".").reverse();
	ph = document.getElementById("reg_phone").value.split("-").join('');
	em = document.getElementById("reg_e_mail").value;

	if(id=="")
		return {"error": "Выберете Вашу заявку."};
	if(ln.length == 0 || fn.length == 0)
		return {"error": "Фамилия и Имя должны быть не менее 1-го символа."};
	if(bd.length != 3)
		return {"error": "Ошибочная дата рождения. Формат даты: 'ДД.ММ.ГГГГ'."};
	temp = new Date(bd.join('-'));	
	if(temp.getDate() != Number(bd[2]) || temp.getMonth() != Number(bd[1])-1 || temp.getFullYear() != Number(bd[0]))
		return {"error": "Ошибочная дата рождения. Такой даты не бывает."};
	temp = (new Date()).getFullYear()- temp.getFullYear();	
	if(temp < 10 || temp > 90)
		return {"error": "Ошибочная дата рождения. Возрастные ограничения."};	
	if(ph.length < 12 || ph[0] != '+')
		return {"error": "Ошибочный телефон. Допустимый формат: '+X-XXX-XXX-XX-XX'."};	
	temp = em.split('@')
	if(em.split(' ').length != 1 || temp.length != 2 || temp[1].split('.').length == 1)
		return {"error": "Явно ошибочная электронная почта."};
	
	temp = (s => {
					if(s.length == 0) return "";
					s.toLowerCase();
					return s[0].toUpperCase() + s.substring(1);})
	
	return {
		//"person": document.location.href.split('/').pop(),
		"id": getID(id),
		"info": {
			"lastname": 	temp(ln),
			"firstname": 	temp(fn),
			"patronymic": 	temp(pt),
			"birthday":		bd.join('-'),
			"phone":		ph,
			"e_mail":		em
		}		
	}
}









function getID(id) {
	return Number(id.substring(3));
}









function saveData() {
	console.log("!save");
}
function loadData() {
	console.log("!load");
}
function getStudent() {
	console.log("getStudent");
}
function getEmployee() {
	console.log("getEmployee");
}



//-----------------------------------------------------------------

function click_personal_info(event) {
	data = getPersonalInfo();
	if(isErrorData(data))
		return;	
	click_disabled();
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		document.getElementById("center").innerHTML = temp;});
}

function click_registration(event) {
	if (event.target.id == "login")
		data = {"login": getCookie("login")};			
	else
		data = getLoginPassword();
	if(isErrorData(data))
		return;	
	click_disabled();	
	fetch("", createPOST(data, 'application/json'))
	.then(response => response.json())		
	.then(temp => {
		click_enabled();
		if(temp["href"]=="") 
			errorMessage("Ошибочные логин и пароль. Повторите.");			
		else
			if(temp["html"]=="")
				window.location.href = temp["href"];
			else
				document.getElementById("center").innerHTML = temp["html"];
	});			
}
function click_choice_delegation(event) {
	data = {"id": event.target.id, "login": getCookie("login")}
	click_disabled();
	fetch("", createPOST(data, 'application/json'))
	.then(response => response.json())		
	.then(temp => {
		click_enabled();
		window.location.href = temp["href"];
	});			
}



function click_administrator(name, ex="") {
	data = getChoicePerson(name, ex);
	if(isErrorData(data))
		return;	
	click_disabled();
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		document.getElementById("center").innerHTML = temp;});			
	
	

	
	
	
	
	
	
	
	fun = {
			"employee": getEmployee,
			"student": getStudent,
			"save": saveData,
			"load": loadData};
	fun[name](); 
	
}

 */
 
 
 
/* function click_person(event) {		//реакция на нажатие фамилии	
	data = {"id": event.target.id}
	click_disabled();	
	fetch("", createPOST(data))
	.then(response => response.text())		
	.then(temp => {
		click_enabled();
		window.location.href = temp;
	});			
} */