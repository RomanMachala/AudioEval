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

// Event listener to return to existing analysis
document.querySelector("#analysis-exists").addEventListener("click", async function(event){
    // Hides container section and shows analysis section
    document.querySelector("#container").style.display = "none";
    document.querySelector(".analysis-section").style.display = "block";

    showModal("Uploading files...");

    try{
        let processResponse = await fetch('/process/', { method: 'POST' });
        let processResult = await processResponse.json();
        /* If endpoint resulted in OK, then display graphs and tables */
        if (processResponse.ok) {
            updateModalText("Processing files...");
            displayGraphs(processResult.generated_plots);
            displayTables(processResult.generated_plots.tables);
            console.log(processResult.generated_plots)
        } else {
            /* Else atleast present an error */
            alert("An error occured while trying to fetch graphs, please check your files and try again.");
            return;
        }
    } catch (error){
        console.log(error);
        alert("An error occured while trying to load previous analysis, please check your files and try again.");
        return;
    } finally{
        hideModal();
    }
});