const workshop_nav = document.getElementById('workshop-navbar')
const workshop_navbar_items = document.getElementById('workshop_navbar_items')
const workshop_navbar_toggle_button = document.getElementById('workshop-navbar-toggle')

isHidden = function(el) {
    var style = window.getComputedStyle(el);
    return (style.display === 'none')
}

workshop_nav
    .addEventListener('click', function (e) {
        if (e.target.id == 'meta-btn') {
            // do nothing
        } else if (e.target.id == "workshop-navbar-toggle") {
            // do nothing
        } else {
            if (isHidden(workshop_navbar_toggle_button) != true) {
                var bsCollapse = new bootstrap.Collapse(workshop_navbar_items, {
                    toggle: true
                });
                e.preventDefault();
            };
        };
    })