var favorite_buttons = [...document.querySelectorAll('.favorited[data-favorite]')]

favorite = function(evt) {
    var workshop = evt.target.dataset.workshop;
    var url = evt.target.dataset.url;
    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Workshop": workshop
        },
        body: ''
    }).then(function(response) { return response.json(); }).then(function(data) {
        if (data.removed === true) {
            // console.log("Favorite " + data.workshop + "removed.");
            favorite_buttons.forEach(elem => {
                elem.style.backgroundColor = '#ffc24f45;';
                evt.target.style.backgroundColor = '#ffc24f45;';
                setTimeout(() => { elem.style.backgroundColor = ''; }, 3000);
                setTimeout(() => { evt.target.style.backgroundColor = ''; }, 3000);
                elem.dataset.favorite = false;
            })
        } else if (data.added === true) {
            // console.log("Favorite " + data.workshop + "added.");
            favorite_buttons.forEach(elem => {
                elem.style.backgroundColor = '#e0ffe06b';
                evt.target.style.backgroundColor = '#e0ffe06b;';
                setTimeout(() => { elem.style.backgroundColor = ''; }, 3000);
                setTimeout(() => { evt.target.style.backgroundColor = ''; }, 3000);
                elem.dataset.favorite = true;
            })
        } else if (data.error === 'user is not authenticated') {
            document.querySelector('#no-login').classList.remove('alert-warning');
            document.querySelector('#no-login').classList.add('alert-danger');
            document.querySelector('#no-login').innerHTML = `Note that you must be logged in to favorite workshops. Click to <a href="${window.LOGIN_URL}">login</a> or <a href="${window.REGISTER_URL}">create an account</a>.`;
        } else {
            console.error('Cannot interpret response data');
            console.error(data);
        }
    }).catch(function(ex) {
        console.error(ex);
    });
};

favorite_buttons.forEach(elem => {
    elem.addEventListener('click', evt => {
        favorite(evt);
    })
});