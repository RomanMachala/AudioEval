document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault(); /* Cancel automatic redirection */

    let formData = new FormData();
    let files = document.getElementById("file-input").files;

    /* If there are no files, return */
    if (files.length === 0) {
        alert("Please input at least one file!");
        return;
    }

    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    /* Validate files */
    let response = await fetch('/upload/', {
        method: 'POST',
        body: formData
    });

    /* Wait for result */
    let result = await response.json();
    console.log(JSON.stringify(result, null, 2));

    let uploadStatus = document.getElementById("upload-status");

    if (result.valid_files && result.valid_files.length > 0) {
        let validFilesText = "Valid files:\n" + result.valid_files.join("\n");
        uploadStatus.innerText = validFilesText;

        /* Hide upload section and show analysis */
        document.querySelector("#container").style.display = "none";
        document.querySelector(".analysis-section").style.display = "block";

        /* Call the process endpoint */
        let processResponse = await fetch('/process/', { method: 'POST' });
        let processResult = await processResponse.json();

        if (processResponse.ok) {
            uploadStatus.innerText = "Analysis complete!";
            displayGraphs(processResult.generated_plots);
            console.log(processResult.generated_plots)
        } else {
            uploadStatus.innerText = "Error generating graphs.";
        }

    } else {
        uploadStatus.innerText = "No valid files uploaded.";
    }
});

function displayGraphs(graphs) {
    for (const [metric, paths] of Object.entries(graphs)) {
        let section = document.getElementById(`${metric}-section`).querySelector(".charts-container");
        section.innerHTML = "";  // Vymazat staré grafy, pokud nějaké jsou
        paths.forEach(path => {
            let img = document.createElement("img");
            img.src = path;
            img.alt = `${metric} graph`;
            img.style.maxWidth = "100%";
            img.style.marginBottom = "10px";
            section.appendChild(img);
        });
    }
}

function goBackToSelect() {
    console.log("Back button clicked!");

    let container = document.querySelector("#container");
    let analysisSection = document.querySelector(".analysis-section");

    if (container && analysisSection) {
        container.style.display = "block";
        analysisSection.style.display = "none";
    } else {
        console.log("Error: container or analysis-section not found!");
    }
}

