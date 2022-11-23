function sendData(url, data, httpMethod, reload=false){
    fetch(url, {
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
        }

        if(reload){
            location.reload();
        }
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
