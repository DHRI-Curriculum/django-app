var top_menu = document.querySelector('#topNavbarToggleExternal');
var top_navbar = () => { return bootstrap.Collapse.getInstance(top_menu); }
var all_workshops = () => { return bootstrap.Collapse.getInstance(document.querySelector('#allWorkshops')); }
var all_installations = () => { return bootstrap.Collapse.getInstance(document.querySelector('#allInstallations')); }
var all_insights = () => { return bootstrap.Collapse.getInstance(document.querySelector('#allInsights')); }


/*
document.querySelector('[data-toggle=collapse][data-target="#topNavbarToggleExternal"]').addEventListener('click', (evt) => {
    console.log('click detected');
    console.log(evt)
    if (evt.target.dataset.target == '#topNavbarToggleExternal') {
        if (top_navbar() != null) {
            console.log('toggling navbar');
            top_navbar().toggle();
        } else {
            if (top_menu != null) {
                console.log('setting up new navbar element');
                new bootstrap.Collapse(top_menu, {
                    toggle: true
                });
            }
        }
    }
});
*/

top_menu.addEventListener('hide.bs.collapse', () => {
    if (all_workshops() != null) { all_workshops().hide(); }
    if (all_installations() != null) { all_installations().hide(); }
    if (all_insights() != null) { all_insights().hide(); }

    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
} );

top_menu.addEventListener('show.bs.collapse', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
} );

document.querySelector('#allWorkshops').addEventListener('show.bs.collapse', () => {
    if (all_installations() != null) { all_installations().hide(); }
    if (all_insights() != null) { all_insights().hide(); }
});
document.querySelector('#allInstallations').addEventListener('show.bs.collapse', () => {
    if (all_workshops() != null) { all_workshops().hide(); }
    if (all_insights() != null) { all_insights().hide(); }
});
document.querySelector('#allInsights').addEventListener('show.bs.collapse', () => {
    if (all_workshops() != null) { all_workshops().hide(); }
    if (all_installations() != null) { all_installations().hide(); }
});