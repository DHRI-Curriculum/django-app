var top_menu = document.querySelector('#topNavbarToggleExternal');
var all_workshops = document.querySelector('#allWorkshops');
var all_installations = document.querySelector('#allInstallations');
var all_insights = document.querySelector('#allInsights');

var top_menu_collapse = () => { return bootstrap.Collapse.getInstance(top_menu); }
var all_workshops_collapse = () => { return bootstrap.Collapse.getInstance(all_workshops); }
var all_installations_collapse = () => { return bootstrap.Collapse.getInstance(all_installations); }
var all_insights_collapse = () => { return bootstrap.Collapse.getInstance(all_insights); }

try {
    if (all_workshops_collapse() == null) {
        // console.log('setting up new all workshops element...')
        new bootstrap.Collapse(all_workshops, {
            toggle: false
        });
    }
} catch (error) {
    console.log('cannot set up workshops element');
    console.log(error);
}

try {
    if (all_installations_collapse() == null) {
        // console.log('setting up new all installations element...')
        new bootstrap.Collapse(all_installations, {
            toggle: false
        });
    }
} catch (error) {
    console.log('cannot set up installations element');
    console.log(error);
}

try {
    if (all_insights_collapse() == null) {
        // console.log('setting up new all insights element...')
        new bootstrap.Collapse(all_insights, {
            toggle: false
        });
    }
} catch (error) {
    console.log('cannot set up insights element');
    console.log(error);
}


all_workshops_collapse()._element.addEventListener('show.bs.collapse', () => {
    console.log('all workshops shown!');
    if (all_installations_collapse() != null) { all_installations_collapse().hide(); }
    if (all_insights_collapse() != null) { all_insights_collapse().hide(); }
});
all_installations_collapse()._element.addEventListener('show.bs.collapse', () => {
    console.log('all installations shown!');
    if (all_workshops_collapse() != null) { all_workshops_collapse().hide(); }
    if (all_insights_collapse() != null) { all_insights_collapse().hide(); }
});
all_insights_collapse()._element.addEventListener('show.bs.collapse', () => {
    console.log('all insights shown!');
    if (all_workshops_collapse() != null) { all_workshops_collapse().hide(); }
    if (all_installations_collapse() != null) { all_installations_collapse().hide(); }
});

try {
    if (top_menu_collapse() == null && top_menu != null) {
        // console.log('setting up new navbar element...')
        new bootstrap.Collapse(top_menu, {
            toggle: false
        });
    } else if (top_menu_collapse() == null && top_menu == null) {
        console.log('no interactivity with top menu on this page.')
    }
} catch (error) {
    console.log('cannot set up navbar element');
    console.log(error);
}

if (top_menu_collapse() != null) {
    top_menu_collapse()._element.addEventListener('hide.bs.collapse', () => {
        if (all_workshops_collapse() != null) { all_workshops_collapse().hide(); }
        if (all_installations_collapse() != null) { all_installations_collapse().hide(); }
        if (all_insights_collapse() != null) { all_insights_collapse().hide(); }

        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    } );

    top_menu_collapse()._element.addEventListener('show.bs.collapse', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    } );

    document.getElementById('secondaryMenu').addEventListener('click', evt => {
        if (evt.delegateTarget == undefined) {
            if (evt.target.tagName == 'A') {
                console.log('clicked an actual link..');
            } else {
                top_menu_collapse().toggle();
                evt.stopPropagation();
            }
        } else {
            console.log('clicked an actual thing...!');
        }
    }
    );

    document.getElementById('secondaryMenu').style.cursor = 'pointer';
} else {
    console.log('normal navbar interactivity not initiated because it is not collapsible.');

    document.getElementById('secondaryMenu').addEventListener('click', evt => {
        if (evt.delegateTarget == undefined) {
            if (evt.target.tagName == 'A') {
                console.log('clicked an actual link..');
            } else {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                evt.stopPropagation();
            }
        }
    });

    document.getElementById('secondaryMenu').style.cursor = 'pointer';
}

