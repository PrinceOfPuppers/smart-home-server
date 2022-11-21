function sendData(url, data, httpMethod = 'POST'){
    fetch(url, {
    method: httpMethod,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
    })
    .then(response => console.log(response.ok))
}
