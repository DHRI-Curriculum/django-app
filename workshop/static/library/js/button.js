function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// How to get csrf token: const csrftoken = getCookie('csrftoken');


load_more = function(e) {
    var link = e.target;
    var page = parseInt(link.dataset.page);
    var url = link.dataset.url;
    var div = link.dataset.div;
    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Page": page
        },
        body: ''
    }).then(function(response) { return response.json();
    }).then(function(data) {
        if (data.has_next) {
            page += 1;
            link.dataset.page = page;
        } else {
            link.style.display = "none";
        }

        document.getElementById(div).innerHTML += data.html;
    }).catch(function(ex) {
        console.log("Error:", ex);
    });
};

document.getElementById('loadMoreProjects').addEventListener('click', function(e) { load_more(e); });
document.getElementById('loadMoreReadings').addEventListener('click', function(e) { load_more(e); });
document.getElementById('loadMoreTutorials').addEventListener('click', function(e) { load_more(e); });
document.getElementById('loadMoreResources').addEventListener('click', function(e) { load_more(e); });
