var next = {% if page_obj.has_next %}{{ page_obj.next_page_number }}{% else %}0{% endif %}
var prev = {% if page_obj.has_previous %}{{ page_obj.previous_page_number }}{% else %}0{% endif %}

const go_next = function() {
    if (next != 0) { location.assign("?page=" + next); } else { console.error('no next page'); }
}

const go_prev = function() {
    if (prev != 0) { location.assign("?page=" + prev); } else { console.error('no prev page'); }
}
window.addEventListener("keydown", function (event) {
    if (event.defaultPrevented) {
    return; // Do nothing if the event was already processed
    }

    switch (event.key) {
        case "Left":
        case "ArrowLeft":
            //console.log('left');
            go_prev();
            break;
        case "Right":
        case "ArrowRight":
            //console.log('right');
            go_next();
            break;
    }
});