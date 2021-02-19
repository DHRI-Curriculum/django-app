// Swipe Up / Down / Left / Right
var initialX = null;
var initialY = null;

const go_next = function() {
    if (next != 0) { location.assign("?page=" + next); } else { console.info('no next page'); }
}

const go_prev = function() {
    if (prev != 0) { location.assign("?page=" + prev); } else { console.info('no prev page'); }
}

/*

// Touch functionality removed as it was too sensitive.

function startTouch(e) {
    //console.log(e);
    initialX = e.touches[0].clientX;
    initialY = e.touches[0].clientY;
};
 
function moveTouch(e) {
    if (initialX === null) { return; }
    if (initialY === null) { return; }

    var currentX = e.touches[0].clientX;
    var currentY = e.touches[0].clientY;

    var diffX = initialX - currentX;
    var diffY = initialY - currentY;

    if (Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX > 0) {
            // swiped left
            go_next();
        } else {
            // swiped right
            go_prev();
        }

        initialX = null;
        initialY = null;

        e.preventDefault();
    }
};

document.getElementById('lesson-content').addEventListener("touchstart", startTouch, false);
document.getElementById('lesson-content').addEventListener("touchmove", moveTouch, false);
*/
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