const left_menubar = document.querySelector('#left-menu-menubar');
const left_menu_wrapper = document.querySelector('#left-menu-wrapper');
const left_main = document.querySelector('#left-menu-main');
const toggle_menu_btn = document.querySelector('#toggle_menu');

const hide_menubar = () => {
    //console.log('hide!');

    //console.log('changing menu to delayed')
    left_menu_wrapper.classList.remove('delayed');
    left_menu_wrapper.classList.add('not-delayed');

    //console.log('move out menu')
    left_menu_wrapper.style.left = '-500px';

    //console.log('setting main to full')
    left_main.classList.remove('col-md-9');

    //console.log('changing main to delayed (for next transition)')
    left_main.classList.remove('not-delayed');
    left_main.classList.add('delayed');

    left_menu_wrapper.classList.remove('delayed');
};

const show_menubar = () => {
    //console.log('show!');

    //console.log('changing menu to not delayed')
    left_menu_wrapper.classList.remove('not-delayed');
    left_menu_wrapper.classList.add('delayed');

    //console.log('setting main to column')
    left_main.classList.add('col-md-9');

    //console.log('move in menu')
    left_menu_wrapper.style.left = '0px';

    //console.log('changing main to not delayed (for next transition)')
    left_main.classList.remove('delayed');
    left_main.classList.add('not-delayed');
};

const toggle_menu = (e) => {
    if (left_menu_wrapper.style.left == '-500px') {
        e.target.innerHTML = '&laquo; Hide selection menu';
        show_menubar()
    } else {
        e.target.innerHTML = 'Show selection menu &raquo;';
        hide_menubar()
    }
}

toggle_menu_btn.addEventListener('click', (e) => toggle_menu(e) );