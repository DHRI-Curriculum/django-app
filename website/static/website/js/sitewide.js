var top_menu = document.querySelector('#topNavbarToggleExternal');
var all_workshops = document.querySelector('#allWorkshops');
var all_installations = document.querySelector('#allInstallations');
var all_insights = document.querySelector('#allInsights');

var top_menu_collapse = () => { return bootstrap.Collapse.getInstance(top_menu); }
var all_workshops_collapse = () => { return bootstrap.Collapse.getInstance(all_workshops); }
var all_installations_collapse = () => { return bootstrap.Collapse.getInstance(all_installations); }
var all_insights_collapse = () => { return bootstrap.Collapse.getInstance(all_insights); }

try {
    if (top_menu_collapse() == null) {
        console.log('setting up new navbar element...')
        new bootstrap.Collapse(top_menu, {
            toggle: true
        });
    }
} catch (error) {
    console.log('cannot set up navbar element');
    console.log(error);
}

try {
    if (all_workshops_collapse() == null) {
        console.log('setting up new all workshops element...')
        new bootstrap.Collapse(all_workshops, {
            toggle: true
        });
    }
} catch (error) {
    console.log('cannot set up workshops element');
    console.log(error);
}

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


all_workshops_collapse().addEventListener('show.bs.collapse', () => {
    console.log('all workshops shown!');
    if (all_installations_collapse() != null) { all_installations_collapse().hide(); }
    if (all_insights_collapse() != null) { all_insights_collapse().hide(); }
});
all_installations().addEventListener('show.bs.collapse', () => {
    console.log('all installations shown!');
    if (all_workshops_collapse() != null) { all_workshops_collapse().hide(); }
    if (all_insights_collapse() != null) { all_insights_collapse().hide(); }
});
all_insights().addEventListener('show.bs.collapse', () => {
    console.log('all insights shown!');
    if (all_workshops_collapse() != null) { all_workshops_collapse().hide(); }
    if (all_installations_collapse() != null) { all_installations_collapse().hide(); }
});

top_menu_collapse().addEventListener('hide.bs.collapse', () => {
    if (all_workshops_collapse() != null) { all_workshops_collapse().hide(); }
    if (all_installations_collapse() != null) { all_installations_collapse().hide(); }
    if (all_insights_collapse() != null) { all_insights_collapse().hide(); }

    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
} );

top_menu_collapse().addEventListener('show.bs.collapse', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
} );