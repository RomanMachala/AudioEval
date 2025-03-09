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

    let uploadStatus = document.getElementById("upload-status");

    // Fetches results
    let processResponse = await fetch('/process/', { method: 'POST' });
    let processResult = await processResponse.json();
    /* If endpoint resulted in OK, then display graphs */
    if (processResponse.ok) {
        uploadStatus.innerText = "Analysis complete!";
        displayGraphs(processResult.generated_plots);
        console.log(processResult.generated_plots)
    } else {
        /* Else atleast present an error */
        uploadStatus.innerText = "Error generating graphs.";
    }

    let tablesResponse = await fetch('/get_tables/', { method: 'POST' });
    let tablesResult = await tablesResponse.json();
    /* If endpoint resulted in OK, then display graphs */
    if (tablesResponse.ok) {
        uploadStatus.innerText = "Fetching tables data ok!";
        displayTables(tablesResult.tables);
        console.log(tablesResult.tables)
    } else {
        /* Else atleast present an error */
        uploadStatus.innerText = "Error getting table data.";
    }
});