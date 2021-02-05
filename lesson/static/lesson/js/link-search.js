document.querySelectorAll("#lesson-content a").forEach((link) => {
    if (link.href.includes("#")) {
        if (link.href.split('#')[0] === document.location.href) {
            // found a link to the document itself... do nothing
        } else {
            // potentially an external file... link it up with a target=_blank
            link.target = '_blank';
        }
    } else if (link.href.includes("/static/website/images/")) {
        // found a link to an image... do nothing
    } else {
        // external link... link it up with a target=_blank
        link.target = '_blank';
    }
});
