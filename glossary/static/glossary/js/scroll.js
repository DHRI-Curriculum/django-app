[...document.querySelectorAll('[data-scroll]')].forEach(elem => {
    elem.addEventListener('click', (evt) => {
        _elem = document.querySelector('[name='+elem.dataset.scroll+']');
        _top = _elem.offsetTop - 50;
        _elem.focus();
        window.scroll({
            top: _top,
            behavior: 'smooth'
        });
        evt.preventDefault();
    });
})