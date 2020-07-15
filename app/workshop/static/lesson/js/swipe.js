// Swipe Up / Down / Left / Right
var initialX = null;
var initialY = null;
 
function startTouch(e) {
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
        // sliding horizontally
        if (diffX > 0) {
            // swiped left
            console.log("swiped left = go forward");
            location.assign("?page=" + next);
        } else {
            // swiped right
            console.log("swiped right = go back");
            location.assign("?page=" + prev);
        }

        initialX = null;
        initialY = null;

        e.preventDefault();
    }
};

document.getElementById('lesson-content').addEventListener("touchstart", startTouch, false);
document.getElementById('lesson-content').addEventListener("touchmove", moveTouch, false);