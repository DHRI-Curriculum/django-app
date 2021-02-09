// all_workshops = [{% for workshop in all_workshops %}'{{workshop.name}}',{% endfor %}]
all_workshops_slugs = {
    {% for workshop in all_workshops %}'{{workshop.slug}}': '{% url 'workshop:frontmatter' workshop.slug %}',{% endfor %}
}
document.querySelectorAll("[data-replace-workshop-links=true]").forEach((elem) => {
    console.log(elem.dataset.replaceWorkshopLinks)
    elem.querySelectorAll("a").forEach((link) => {
        if (link.href.includes("github.com/DHRI-Curriculum/")) {
            finder = link.href.split("/")[link.href.split("/").length - 1];
            if (!finder.includes(".md")) {
                // it's a workshop if finder == any of the workshops
                if (all_workshops_slugs[finder] != undefined && all_workshops_slugs[finder] != '') {
                    link.href = all_workshops_slugs[finder];
                }
            }
        }
    });
});