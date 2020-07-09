console.log('here!')

const website_wide_nav = document.getElementById('website-wide-nav')
const website_wide_nav_ext = document.getElementById('navbarToggleExternalContent')
website_wide_nav
    .addEventListener('mouseenter', function () {
        var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            show: true
        })
    })
website_wide_nav
    .addEventListener('click', function () {
    var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            toggle: true
        })
    })
website_wide_nav
    .addEventListener('mouseexit', function () {
        var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            hide: true
        })
    });
/*
website_wide_nav_ext
    .addEventListener('mouseout', function () {
        var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            toggle: true
        })
    });
*/

/*
const body = document.getElementsByTagName('body')[0]
console.log(body);
body
    .addEventListener('mouseover', function (e) {
        console.log(e.target.id);
    }
    );
*/