var multiLink = [], singleLink = []
document.querySelectorAll('#main-content .card-body a').forEach(link => {
    otherLinks = [...document.querySelectorAll('#main-content .card-body a')].filter(d=>d !== link)
    otherIDs = otherLinks.map(d=>d.parentNode.parentNode.dataset.resourceId);
    if (otherIDs.includes(link.parentNode.parentNode.dataset.resourceId)) {
        console.log('there is another link in this card-body!');
        multiLink.push(link);
    } else {
        singleLink.push(link);
    }
})
singleLink.forEach(a => a.classList.add('stretched-link'));
