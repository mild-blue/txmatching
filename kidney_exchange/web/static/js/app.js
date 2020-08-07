document.addEventListener('DOMContentLoaded', function () {
    if(window.innerWidth > 1200) {
        scrollWatcher();
    }
})

function scrollWatcher() {
    const rightCol = document.querySelector('[data-js-selector="fix-top-on-scroll"]');

    if (!rightCol) return;

    const rightColTopPosition = rightCol.offsetParent.offsetTop;

    window.addEventListener('scroll', function () {
        const currentTop = window.pageYOffset;

        if (currentTop >= rightColTopPosition) {
            rightCol.classList.add('fixed');
        } else {
            rightCol.classList.remove('fixed');
        }
    })
}

// IE fix
const tables = document.querySelectorAll('[data-js-selector="set-table-height"]');
for(let t of tables) {
    const height = t.offsetHeight;
    if(height) {
        t.style.height = height + 'px';
    }
}