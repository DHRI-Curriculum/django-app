const zen_off = '<svg width="2em" height="2em" viewBox="0 0 16 16" class="pr-1 zen-bi bi bi-toggle-off" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M11 4a4 4 0 0 1 0 8H8a4.992 4.992 0 0 0 2-4 4.992 4.992 0 0 0-2-4h3zm-6 8a4 4 0 1 1 0-8 4 4 0 0 1 0 8zM0 8a5 5 0 0 0 5 5h6a5 5 0 0 0 0-10H5a5 5 0 0 0-5 5z"/></svg> Zen mode'
const zen_on = '<svg width="2em" height="2em" viewBox="0 0 16 16" class="pr-1 zen-bi bi bi-toggle-on" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M5 3a5 5 0 0 0 0 10h6a5 5 0 0 0 0-10H5zm6 9a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/></svg> Zen mode'
var nav_elements = document.getElementsByClassName('zen-add');

const hide_class = function(classname) {
    var elements = document.getElementsByClassName(classname);
    for (var i = 0; i < elements.length; i++) {
        elements[i].classList.add('d-none');
    }
}

const show_class = function(classname){
    var elements = document.getElementsByClassName(classname);
    for (var i = 0; i < elements.length; i++) {
        elements[i].classList.remove('d-none');
    }
}

const zen_switch = function(e) {
    if (e.target.id != "zen") {
        button = e.target.parentElement;
    } else {
        button = e.target;
    }

    data = button.dataset;

    if (data.toggle == 'on') {
        button.innerHTML = zen_off;
        button.dataset.toggle = 'off';
        show_class('zen-hideaway');
        for (var i = 0; i < nav_elements.length; i++) {
            nav_elements[i].dataset.toggle = 'off';
        }
        document.cookie = "zen = off;";
    } else if (data.toggle == 'off') {
        button.innerHTML = zen_on;
        button.dataset.toggle = 'on';
        hide_class('zen-hideaway')
        document.cookie = "zen = on;";
    } else {
        console.log('Error:', e)
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
    show_class('zen-hideaway');
    zen_button.innerHTML = zen_off;
    zen_button.dataset.toggle = 'off';
} else if (zen_cookie == "on") {
    hide_class('zen-hideaway');
    zen_button.innerHTML = zen_on;
    zen_button.dataset.toggle = 'on';
}

document.getElementById('zen')
    .addEventListener('click', function(e) { zen_switch(e); });