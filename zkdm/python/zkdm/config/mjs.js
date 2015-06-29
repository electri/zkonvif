var xmlHttp = GetXmlHttpObject()

function space(word, length)
{
	var str="";
	var len = length - word.length;
	for (i = 0; i < len; i++)
	{
		str += " "
	}
	return  str 
}


function get_max_length(words)
{
	length = 0;
	for (i=0; i<words.length; i++)
	{
		if (words[i].length > length)
		{
			length = words[i].length
		}
	}
	return length
}

function get_ids(json_txt)
{
	jn = JSON.parse(json_txt);
	return Object.keys(jn);
}


function createInput(id, value)
{
	var input = document.createElement("INPUT")
	input.setAttribute("name", "config")
	input.setAttribute("class", "config")
	input.setAttribute("type", "text")
	input.setAttribute("id", id);
	input.setAttribute("value", value);
	return input
}

function insertInputWithLab(id, value, owner)
{
	var lab = document.createTextNode(id + ": ");
	var input = createInput(id, value);
	owner.appendChild(input);
	owner.insertBefore(lab, input);
}

function insertBr(owner)
{
	var br = document.createElement("BR");
	owner.appendChild(br);
}

function display(json_txt, span)
{
	jn = JSON.parse(json_txt);
	var raw_keys = Object.keys(jn)
	keys = raw_keys.sort()
	div = document.getElementById("config_div")
	for (i = 0; i < keys.length; i++)
	{
		insertInputWithLab(keys[i], jn[keys[i]], div);
		if ((i+1)%span == 0)
			insertBr(div);
	}
}

function GetXmlHttpObject() { var xmlHttp = null;
	try
	{
		xmlHttp = new XMLHttpRequest();	
	}
	catch (e)
	{
		try
		{
			xmlHttp = new ActiveXObject("Microsoft.XMLHTTP")
		}
		catch(e)
		{
			xmlHttp = new ActiveXObject("Msxml2.XMLHTTP")
		}
	}
	return xmlHttp
}

function get_json(owner)
{
	json = {}
	var kvs = owner.getElementsByClassName("config");
	var length = kvs.length;
	for (i=0; i < length; i++)
	{
		var k = kvs[i].id;
		var v = kvs[i].value;
		json[k] = v;
	}
	return json;
}

function get_json_txt()
{
	var	div = document.getElementById("config_div");
	jn = get_json(div);
	return JSON.stringify(jn)
}

function reset()
{
		xmlHttp.onreadystatechange = function()
{
	if(xmlHttp.readyState == 4)
	{
		txt = xmlHttp.responseText;
		alert(txt);
	}
}
	xmlHttp.open("GET", "reset", true);
	xmlHttp.send();
}

function save()
{
	var str = get_json_txt();
	xmlHttp.onreadystatechange = function()
{
	if(xmlHttp.readyState == 4)
	{
		txt = xmlHttp.responseText;
		alert(txt);
	}
}

	xmlHttp.open("PUT", "save", true);
	xmlHttp.send(str);
}

function get_cfg()
{
	xmlHttp.onreadystatechange = function()
{
	if (xmlHttp.readyState == 4)
	{
		txt = xmlHttp.responseText;
		display(txt, 1);
	}
}
	xmlHttp.open("GET", "get_cfg", true);
	xmlHttp.send();
}
