document.addEventListener('DOMContentLoaded', function () {
    scrollWatcher();
})

function scrollWatcher() {
    const rightCol = document.querySelector('[data-js-selector="fix-top-on-scroll"]');

    if (!rightCol) return;

    const rightColTopPosition = rightCol.offsetParent.offsetTop;

    window.addEventListener('scroll', function () {
        const currentTop = window.scrollY;

        if (currentTop >= rightColTopPosition) {
            rightCol.classList.add('fixed');
        } else {
            rightCol.classList.remove('fixed');
        }
    })
}