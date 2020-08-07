
approve = function(e) {
    var link = e.target;
    console.log(link);
    var url = '/learner/requests/';
    var tr = link.dataset.tr;
    var username = link.dataset.username;
    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            "Content-Type": "application/json",
            'Username': username
        },
        body: ''
    }).then(function(response) { return response.json();
    }).then(function(data) {
        link.innerHTML = "Approved";
        link.classList.add('disabled');
        tr = document.getElementById(tr);
        tr.style.display = 'none';
        console.log(data);
    }).catch(function(ex) {
        console.log("Error:", ex);
    });
};

Array.from(document.getElementsByClassName('approve')).forEach((el) => {
    el.addEventListener('click', function(e) { approve(e); });
});