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
    const score = round.getAttribute('data-score');
    const colorObject = bezierInterpolation(score);
    const colorString = `rgb(${colorObject.r}, ${colorObject.g}, ${colorObject.b})`;
    round.setAttribute('style', `border-right: 20px solid ${colorString}`);
}

function bezierInterpolation(x) {
    const firstColor = {r: 226, g: 0, b: 26};
    const secondColor = {r: 226, g: 0, b: 26}; // todo
    const y = 1 - x;

    const vR = y * firstColor.r + x * secondColor.r;
    const vG = y * firstColor.g + x * secondColor.g;
    const vB = y * firstColor.b + x * secondColor.b;

    return { r: Math.trunc(vR), g: Math.trunc(vG), b: Math.trunc(vB) };
}