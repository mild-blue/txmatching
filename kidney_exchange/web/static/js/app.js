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

// Gradient generator

const rounds = document.querySelectorAll('[data-js-selector="set-score-gradient"]');
for(let round of rounds) {
    const score = Number(round.getAttribute('data-score'));
    if(score >= 0 && score <= 1) {
        const color = getGradientColor(score);
        if(color) {
            round.setAttribute('style', `border-right: 20px solid ${color}`);
        }
    }
}

function getGradientColor(score) {
    // generating colors in this gradient range: https://uigradients.com/#KyooPal
    const startColor = {r: 221, g: 62, b: 84}; // score = 0 -> red
    const endColor = {r: 107, g: 229, b: 113}; // score = 1 -> green

    let diffRed = endColor.r - startColor.r;
    let diffGreen = endColor.g - startColor.g;
    let diffBlue = endColor.b - startColor.b;

    diffRed = (diffRed * score) + startColor.r;
    diffGreen = (diffGreen * score) + startColor.g;
    diffBlue = (diffBlue * score) + startColor.b;

    return `rgb(${diffRed}, ${diffGreen}, ${diffBlue})`;
}