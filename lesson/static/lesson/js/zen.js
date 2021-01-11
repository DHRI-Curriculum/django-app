let body = document.querySelector('body');

const zen_switch = function(e) {
    let inZen = [...body.classList].includes('zen');
    let zenButton = document.querySelector('#zen');

    if (inZen) {
        body.classList.remove('zen');
        document.cookie = "zen = off;";
    } else {
        body.classList.add('zen');
        document.cookie = "zen = on;";
    }
    e.stopPropagation();
}

var zen_cookie = 'auto-off';

try {
    var zen_cookie = document.cookie
                        .split('; ')
                        .find(row => row.startsWith('zen'))
                        .split('=')[1];
} catch(e) {
    // empty because we have already automatically specified zen_cookie above
}

const zen_button = document.getElementById('zen')

if (zen_cookie == "off" || zen_cookie == "auto-off") {
    body.classList.remove('zen')
} else if (zen_cookie == "on") {
    body.classList.add('zen')
}

document.getElementById('zen')
    .addEventListener('click', function(e) { zen_switch(e); });