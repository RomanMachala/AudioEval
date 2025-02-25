/**
 * 
 * @author Roman Machala
 * @date 18.02.2025
 * @brief Script containining logic for handling analysis
 *          main functions: correctly handle analysis form and submited files
 *                          start analysis
 *                          load corresponding graphs and show them in their section
 * 
 */

document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault(); /* Cancel automatic redirection */

    let formData = new FormData();
    let files = document.getElementById("file-input").files;

    /* If there are no files, return */
    if (files.length === 0) {
        alert("Please input at least one file!");
        return;
    }
    /* Append submited files to the formData */
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    /* Uploads files, validates them */
    let response = await fetch('/upload/', {
        method: 'POST',
        body: formData
    });

    /* Wait for result */
    let result = await response.json();
    console.log(JSON.stringify(result, null, 2));
    /* HTML element where status about uploading is presented */
    let uploadStatus = document.getElementById("upload-status");

    /* If there are some files that are valid */
    if (result.valid_files && result.valid_files.length > 0) {
        let validFilesText = "Valid files:\n" + result.valid_files.join("\n");
        uploadStatus.innerText = validFilesText;

        /* Hide upload section and show analysis section */
        document.querySelector("#container").style.display = "none";
        document.querySelector(".analysis-section").style.display = "block";

        /* Call the process endpoint */
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

    } else {
        /* If there are no valid files */
        uploadStatus.innerText = "No valid files uploaded.";
    }
});

/**
 * 
 * @param graphs json response containing graphs paths for each metric
 * 
 * @brief fucntion to display graphs based on response from /process/ endpoint
 * 
 */
function displayGraphs(graphs) {
    for (const [metric, paths] of Object.entries(graphs)) {
        /* Select corresponding HTML element based on metric */
        let section = document.getElementById(`${metric}-section`).querySelector(".charts-container");
        section.innerHTML = ""; /* If there are some graphs remove them */
        paths.forEach(path => {
            /* For each path (one path = one graph) create an img element with said path*/
            let img = document.createElement("img");
            img.src = path;
            img.alt = `${metric} graph`;
            img.style.maxWidth = "100%";
            img.style.marginBottom = "10px";
            section.appendChild(img);
        });
    }
}

/**
 * 
 * @brief function to handle button click to return back to selection 
 *          between analysis and evaluation
 * 
 */
function goBackToSelect() {
    console.log("Back button clicked!");
    /* Debugging */

    let container = document.querySelector("#container");
    let analysisSection = document.querySelector(".analysis-section");
    /* Select corresponding sections */

    /* If these section exists hide one and show other */
    if (container && analysisSection) {
        container.style.display = "block";
        analysisSection.style.display = "none";
    } else {
        console.log("Error: container or analysis-section not found!");
        /* Debugging */
    }
}

