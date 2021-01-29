
request_instructor = function(e) {
    var link = e.target;
    var url = link.dataset.url;
    var p = link.dataset.p;
    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: ''
    }).then(function(response) { return response.json();
    }).then(function(data) {
        link.innerHTML = "Instructor status requested";
        link.classList.add('disabled');
        //console.log(data);
    }).catch(function(ex) {
        console.error("Error:", ex);
    });
};

if (document.getElementById('instructor-request')) {
    document.getElementById('instructor-request').addEventListener('click', function(e) { request_instructor(e); });
}