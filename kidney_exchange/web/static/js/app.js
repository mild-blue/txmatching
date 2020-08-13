document.addEventListener('DOMContentLoaded', function () {
    if(window.innerWidth > 1200) {
        scrollWatcher();
    }

    initColors();
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

function initColors() {
    const colorMap = new Map();
    const maxScore = 27;
    const increment = 1.0 / (maxScore - 1);

    for (let i = 0; i <= maxScore; i++) {
        const colorObject = bezierInterpolation(increment * i);
        colorMap.set(i, `rgb(${colorObject.r}, ${colorObject.g}, ${colorObject.b})`);
    }

    const rounds = document.querySelectorAll('[data-js-selector="set-score-gradient"]');

    for(let round of rounds) {
        const score = Number(round.getAttribute('data-score'));
        const color = colorMap.get(score);
        if(color) {
            round.setAttribute('style', `border-right: 20px solid ${color}`);
        }
    }
}

function bezierInterpolation(x) {
    const firstColor = {r: 226, g: 0, b: 26}; // minimum -- red
    const secondColor = {r: 0, g: 128, b: 0}; // maximum -- green
    const y = 1 - x;

    const vR = y * firstColor.r + x * secondColor.r;
    const vG = y * firstColor.g + x * secondColor.g;
    const vB = y * firstColor.b + x * secondColor.b;

    return { r: Math.trunc(vR), g: Math.trunc(vG), b: Math.trunc(vB) };
}