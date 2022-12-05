async function sendData(url, data, httpMethod, reload=false){
    return await fetch(url, {
        method: httpMethod,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then((response) => {
        if(!response.ok){
            window.alert(`Status: ${response.status}\n${response.statusText}`);
            return false;
        }

        if(reload){
            location.reload();
        }
        return true;
    })
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

    sendData(url, data, 'PATCH', reload=true);
}

function jobEnable(url, jobId, enable){
    var data = {'id': jobId, 'enable': enable};
    sendData(url, data, 'POST', reload=true);
}
function jobDelete(url, jobId){
    var data = {'id': jobId};
    sendData(url, data, 'DELETE', reload=true);
}
function processDoData(data, toSubmit){
    if(data.do == "press"){
        toSubmit.do = {type:"press", data:{channel: Number(data.pressChannel), value: Boolean(data.pressValue)}};
    }
    else if(data.do == "lcd"){
        toSubmit.do = {type:"lcd", data:{line1: data.lcdLine1, line2: data.lcdLine2, backlight: Boolean(data.lcdBacklight)}};
    }
    else{
        window.alert(`Error: Invalid Job Type: ${data.do}`);
        return false;
    }
    return true;
}

