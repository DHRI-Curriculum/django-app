const website_wide_nav = document.getElementById('website-wide-nav')
const website_wide_nav_ext = document.getElementById('navbarToggleExternalContent')
website_wide_nav
.addEventListener('click', function (e) {
    if (e.target.id != 'meta-btn') {
        var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            toggle: true
        });
    };
})
/*
website_wide_nav
    .addEventListener('mouseenter', function () {
        var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            show: true
        })
    })
website_wide_nav
    .addEventListener('mouseexit', function () {
        var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext, {
            hide: true
        })
    });
*/
/*
document.addEventListener("DOMContentLoaded",function(){
    console.log('here!')
    var bsCollapse = new bootstrap.Collapse(website_wide_nav_ext).hide = true;
});
*/