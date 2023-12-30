async function sendData(url, data, httpMethod, reload=false){
    const response = await fetch(url, {
        method: httpMethod,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })

    if(!response.ok){
        const text = await response.text();
        window.alert(`Status: ${response.status} ${response.statusText}\n${text}`);
        return false;
    }

    if(reload){
        location.reload();
    }
    return true;
}

async function delay(s){
    return new Promise(res => setTimeout(res, 1000*s));
}

async function getData(url, data=null, httpMethod='GET'){
    var content = {
        method: httpMethod,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    };
    if(data !== null){
        content["body"] = JSON.stringify(data);
    }
    const response = await fetch(url, content)

    if(!response.ok){
        const text = await response.text();
        window.alert(`Status: ${response.status} ${response.statusText}\n${text}`);
        return null;
    }

    return await response.json();
}

function formToObject(form){
    let formData = new FormData(form)

    var object = {};
    formData.forEach(function(value, key){
        object[key] = value;
    });
    return object
}


function updateJobName(url, jobId, jobName){
    const newName = window.prompt("Edit Name:", jobName);

    if (newName == null || newName == undefined){
        return;
    }

    if(newName.length > 20){
        window.alert(`Name Too Long:\n  max length: 20 \n  current length: ${newName.length}`);
        updateJobName(url, jobId, newName);
        return;
    }

    var data = {'id': jobId, 'name': newName};

    return sendData(url, data, 'PATCH', reload=true);
}

function jobEnable(url, jobId, enable){
    var data = {'id': jobId, 'enable': enable};
    return sendData(url, data, 'POST', reload=true);
}
function jobDelete(url, jobId){
    var data = {'id': jobId};
    return sendData(url, data, 'DELETE', reload=true);
}
function processDoData(data, toSubmit){
    switch (data.do) {
        case "press":
            toSubmit.do = {type:"press", data:{id: data.pressRemote, channel: Number(data.pressChannel) - 1, value: Boolean(data.pressValue)}};
            break;
        case "lcd":
            toSubmit.do = {type:"lcd", data:{num: Boolean(data.lcdNum)}};
            if(data.lcdFmtEdit){
                toSubmit.do.data.fmt = data.lcdFmt;
            }
            if(data.lcdNameEdit){
                toSubmit.do.data.name = data.lcdName;
            }
            break;
        case "reboot":
            toSubmit.do = {type:"reboot", data:{}};
            break;
        case "update":
            toSubmit.do = {type:"update", data:{}};
            break;
        case "macro":
            toSubmit.do = {type:"macro", data:{id: data.macroIdDo}};
            break;
        case "delay":
            toSubmit.do = {type:"delay", data:{seconds: Number(data.delaySeconds), minutes: Number(data.delayMinutes), hours: Number(data.delayHours)}};
            break;
        default:
            window.alert(`Error: Invalid Job Type: ${data.do}`);
            return false;
    }
    return true;
}

function tempChangeButton(element, newText, time=1){
    const text = element.textContent;

    // double tap catch
    if(text == newText){
        return;
    }

    element.textContent = newText;
    delay(time).then(()=>{
        element.textContent = text;
    });
}

function hideUnhideJobForms(dropDown){
    // iterate over options in the drop down
    Array.from(dropDown.options).forEach((dropDownOption) => {
        // get all elements which match that option
        const form = document.getElementById("jobFormHideUnhide");
        const optionElements = form.querySelectorAll(`[id^='${dropDownOption.value}']`);

        // see if they match the current value
        if (dropDown.value === dropDownOption.value) {
            // if so, display them
            optionElements.forEach((element) => {element.style.display = "block"});
        } else {
            // else hide them
            optionElements.forEach((element) => {element.style.display = "none"});
        }
    })
}

function toggleDropDown(buttonId, elementId){
    const button = document.getElementById(buttonId);
    const element = document.getElementById(elementId);
    if(button.innerText == '⏷'){
        element.style.display = "block";
        button.innerText = '⏶'
    }else{
        element.style.display = "none";
        button.innerText = '⏷'
    }
}

