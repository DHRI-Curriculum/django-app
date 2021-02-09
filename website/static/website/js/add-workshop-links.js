// all_workshops = [{% for workshop in all_workshops %}'{{workshop.name}}',{% endfor %}]
document.querySelectorAll("[data-replace-workshop-links=true]").forEach((elem) => {
    console.info('Encountered element and will recplace workshop links.');
    elem.querySelectorAll("a").forEach((link) => {
        if (link.href.includes("github.com/DHRI-Curriculum/")) {
            finder = link.href.split("/")[link.href.split("/").length - 1];
            if (!finder.includes(".md")) {
                // it's a workshop if finder == any of the workshops
                if (window.all_workshops_slugs[finder] != undefined && window.all_workshops_slugs[finder] != '') {
                    link.href = window.all_workshops_slugs[finder];
                }
            }
        }
    });
});