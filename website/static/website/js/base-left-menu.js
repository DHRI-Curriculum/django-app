const left_menubar = document.querySelector('#left-menu-menubar');
const left_main = document.querySelector('#left-menu-main');
const toggle_menu_btn = document.querySelector('#toggle_menu');

const hide_menubar = () => {
    left_menubar.classList.add('d-none');
    left_menubar.classList.remove('d-block');
    left_main.classList.replace('col-md-9', 'col-md-12');
};

const show_menubar = () => {
    left_menubar.classList.remove('d-none');
    left_menubar.classList.add('d-block');
    left_main.classList.replace('col-md-12', 'col-md-9');
};

const toggle_menu = (e) => {
    if (left_menubar.classList.contains('d-none')) {
        e.target.innerHTML = '&laquo; Hide left-hand menu';
        show_menubar()
    } else {
        e.target.innerHTML = 'Show left-hand menu &raquo;';
        hide_menubar()
    }
}

toggle_menu_btn.addEventListener('click', (e) => toggle_menu(e) );