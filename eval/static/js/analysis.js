/**
 * 
 * @author Roman Machala
 * @date 17.02.2025
 * @brief Simple script containing logic for rollout section in analysis
 *          each analysis section (PESQ, STOI, ...) is hidden, when clicked
 *          on the section is thenrolled out
 * 
 */
document.querySelectorAll(".metric-section-header").forEach(header => {
    header.addEventListener("click", function() {
        /* When clicked on header of one of analysis' section, next element is the section to be rolled out */
        let content = this.nextElementSibling;

        /* Whether the section is not rolled out -> roll it out, else hide it */
        if (content.style.maxHeight && content.style.maxHeight !== "0px") {
            content.style.maxHeight = "0px";
            content.style.padding = "0 10px";
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            content.style.padding = "10px";
        }
    });
});
