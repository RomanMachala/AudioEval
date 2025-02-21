
const evalButton        = document.getElementById("eval-button")
const analysisButton    = document.getElementById("analysis-button")
const container         = document.getElementById("container")

analysisButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

evalButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});
