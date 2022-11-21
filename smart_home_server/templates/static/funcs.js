function sendData(url, data, httpMethod = 'POST'){
    fetch(url, {
    method: httpMethod,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
    })
    // TODO: deal with error case better
    .then(response => console.log(response.ok))
}

function formToObject(form){
    let formData = new FormData(form)

    var object = {};
    formData.forEach(function(value, key){
        object[key] = value;
    });
    return object
}
