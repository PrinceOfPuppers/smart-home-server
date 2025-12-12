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
    var res = {}
    const elements = form.querySelectorAll('[name]');
    elements.forEach( element => {
        const name = element.name;
        let value = element.value;

        switch (element.type) {
          case 'number':
            value = value === '' ? null : Number(value);
            break;

          case 'checkbox':
            value = element.checked;
            break;

          case 'radio':
            if (!element.checked) return; // only store the checked one
            break;

          case 'date':
            value = value ? new Date(value) : null;
            break;
        }
        res[name] = value

    })
    return res
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
            toSubmit.do = {type:"lcd", data:{num: Number(data.lcdNum)}};
            if(data.lcdFmtEdit){
                toSubmit.do.data.fmt = data.lcdFmt;
            }
            if(data.lcdNameEdit){
                toSubmit.do.data.name = data.lcdName;
            }
            if(data.lcdBacklight!="same"){
                toSubmit.do.data.backlight = data.lcdBacklight;
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

function resizeSelectButton(sel) {
    // create temporary select to get needed size
    let tempOption = document.createElement('option');
    tempOption.textContent = sel.selectedOptions[0].textContent;

    let tempSelect = document.createElement('select');
    tempSelect.className = "selectButton";
    tempSelect.style.visibility = "hidden";
    tempSelect.style.position = "fixed"
    tempSelect.appendChild(tempOption);

    // set select to size
    sel.after(tempSelect);
    sel.style.width = `${+tempSelect.clientWidth + 4}px`;
    tempSelect.remove();
}

function setupSelectButtonResize(){
    Array.from(document.getElementsByClassName("selectButton")).forEach(
        (sel)=>{
            resizeSelectButton(sel); // inital load resize
            sel.addEventListener("change", (e) => {resizeSelectButton(e.target)}); // resize on change
        }
    );
}

function setupHideUnhideForm(dropDownId, hideUnhideSectionId){
    let ddid = "#" + dropDownId;
    hideUnhideForm(document.querySelector(ddid), hideUnhideSectionId);
    document.querySelector(ddid).addEventListener("change", function(dropDown) {hideUnhideForm(dropDown.target, hideUnhideSectionId)});
}

function hideUnhideForm(dropDown, hideUnhideSectionId){
    // iterate over options in the drop down
    Array.from(dropDown.options).forEach((dropDownOption) => {
        // get all elements which match that option
        const form = document.getElementById(hideUnhideSectionId);
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
