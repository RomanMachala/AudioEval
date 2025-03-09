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

// Event lisener for uploaded files button, on click do:
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

        let tablesResponse = await fetch('/get_tables/', { method: 'POST' });
        let tablesResult = await tablesResponse.json();
        console.log(tablesResponse);
        if (tablesResponse.ok){
            uploadStatus.innerText = "Tables generation ok.";
            displayTables(tablesResult.tables);
            console.log(tablesResult.tables);
        }else{
            uploadStatus.innerText = "An error occured while trying to get values.";
        }

    } else {
        /* If there are no valid files */
        uploadStatus.innerText = "No valid files uploaded.";
    }

    //Clears file input
    document.getElementById('file-input').value = '';
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
 * @brief function for table displaying
 * 
 * @param tables json response, containing metric values (mean, median, ...)
 * 
 */
function displayTables(tables) {
    const metrics = ["Pesq", "Stoi", "Estoi", "Mcd", "Mos"];
    const mosLabels = {
        "ovrl_mos": "Overall MOS",
        "sig_mos": "Signal MOS",
        "bak_mos": "Background MOS",
        "p808_mos": "P808 MOS"
    };
    // Iterates through each section
    metrics.forEach(metric => {
        let section = document.getElementById(`${metric}-section`);
        if (!section) {
            console.warn(`No section for ${metric} metric.`);
            return;
        }

        let tablesContainer = section.querySelector(".tables-container");
        tablesContainer.innerHTML = ""; // Removes previous tables

        if (metric === "Mos") {
            // If the metric is mos, then we create 4 separate tables
            Object.entries(mosLabels).forEach(([subMetric, label]) => {
                if (!tables.Values[subMetric]) return;

                let tableWrapper = document.createElement("div");
                tableWrapper.classList.add("mos-table-wrapper");

                let title = document.createElement("h4");
                title.innerText = label;
                tableWrapper.appendChild(title);
                // For each table we fill it with values
                let table = createTable(tables.Files, tables.Values[subMetric]);
                tableWrapper.appendChild(table);

                tablesContainer.appendChild(tableWrapper);
            });
        } else {
            //Other metrics have only one table
            let table = createTable(tables.Files, tables.Values[metric]);
            tablesContainer.appendChild(table);
        }
    });
}

/**
 * 
 * @brief Help function for table creation
 * 
 * @param files name of the files
 * @param values metric values
 * @returns created table
 * 
 */
function createTable(files, values) {
    let table = document.createElement("table");
    table.classList.add("metric-table");

    let thead = document.createElement("thead");
    let tbody = document.createElement("tbody");

    //Header of the table
    let headerRow = document.createElement("tr");
    headerRow.innerHTML = `<th>File</th><th>Mean</th><th>Median</th><th>Min</th><th>Max</th>`;
    thead.appendChild(headerRow);

    //Values filling
    values.forEach((fileValues, fileIndex) => {
        let row = document.createElement("tr");
        row.innerHTML = `
            <td>${files[fileIndex]}</td>
            <td>${formatValue(fileValues[0])}</td>
            <td>${formatValue(fileValues[1])}</td>
            <td>${formatValue(fileValues[2])}</td>
            <td>${formatValue(fileValues[3])}</td>
        `;
        tbody.appendChild(row);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    return table;
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

/**
 * 
 * Help function for value formatting
 * 
 * @param value value to be formatted
 * @returns formatted value
 */
function formatValue(value) {
    return isNaN(value) ? "N/A" : value.toFixed(2);
}

