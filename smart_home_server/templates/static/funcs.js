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
