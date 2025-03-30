/**
 * 
 * @author Roman Machala
 * @date 13.02.2025
 * @brief Simple script containing logic for analysis/evaluation form selection
 *          Depending on which button is pressed a class is removed/added to a 
 *          element, based on this class the container is covering different
 *          element
 * 
 */

/**
 * Constants for buttons and overall container
 */
const evalButton        = document.getElementById("eval-button")
const analysisButton    = document.getElementById("analysis-button")
const container         = document.getElementById("container")

/**
 * If the analysis button is clicked, a new class is added to the container
 */
analysisButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

/**
 * If the evaluation button is clicked, a new class is removed to the container
 */
evalButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});
