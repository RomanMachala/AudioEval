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

// Allowed metrics, that are taken into consideration when generating sections
const allowedMetrics = ["Pesq", "Stoi", "Estoi", "Mcd", "Mos"];

/**
 * 
 * @brief simlpe function to hide analysis section and show default selection
 * 
 */
function revert(){
    document.querySelector("#container").style.display = "block";
    document.querySelector(".analysis-section").style.display = "none";
}

/**
 * 
 * @brief simlpe function to hide default section and show analysis section
 * 
 */
function display(){
    document.querySelector("#container").style.display = "none";
    document.querySelector(".analysis-section").style.display = "block";
}

/**
 * 
 * @param flag whether loading previous analysis or creating a new one
 * 
 * @brief async function to display analysis, gets graphs, tables and samples to display
 * 
 */
async function displayAnalysis(flag){
    try{
        if(flag){
            showModal("Loading last analysis");
        }
        display(); // shows analysis section

        /* Update loading modal */
        updateModalText("Processing files...");

        /* Call endpoint for processing */
        let processResponse = await fetch('/process/', { method: 'POST' });
        let processResult = await processResponse.json();

        getSamples(); // gets audio samples

        /* Show graphs and tables */
        if (processResponse.ok) {
            displayGraphs(processResult.generated_plots);
            displayTables(processResult.generated_plots.tables);
            console.log(processResult.generated_plots);
        } else {
            updateModalText("Error generating graphs.");
            alert("Error generating graphs.");
            return;
        }
    }catch (error){
        console.log(error);
        alert("An error occured while trying to display analysis section");
        // Revert back to selection
        revert();
        return;
    }finally{
        hideModal();
    }
}
// Event lisener for uploaded files button, on click do:
document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault(); /* Cancel automatic redirection */

    let formData = new FormData();
    let files = document.getElementById("file-input").files;

    /* If there are no files */
    if (files.length === 0) {
        alert("Please input at least one file!");
        return;
    }

    /* Add files to formData */
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    /* Show modal window for loading */
    showModal("Uploading files...");

    try {
        let response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        let result = await response.json();
        console.log(JSON.stringify(result, null, 2));

        updateModalText("Loading files...");
        if (result.valid_files && result.valid_files.length > 0) {
            let validFilesText = "Valid files:\n" + result.valid_files.join("\n");
            updateModalText(validFilesText);
            displayAnalysis(false); //displays analysis
        } else {
            updateModalText("No valid files uploaded.");
            alert("No valid files uploaded.");
            revert(); //hides analysis on fail
            return;
        }
    } catch (error){
        console.error("Error:", error);
        alert("An error occured while uploading files, please check your files and try again.");
        revert(); //hides analysis on fail
        return
    }

    /* Clear input files */
    document.getElementById('file-input').value = '';
});

// button event listener, displaying previous analysis
document.getElementById("analysis-button-continue").addEventListener('click', async function(event) {
    event.preventDefault();
    displayAnalysis(true); //display previous analysis
});

/**
 * 
 * @param text text to be shown in loading modal
 * 
 * @brief function to show modal window while fetching results
 * 
 */
function showModal(text) {
    document.getElementById("upload-modal-text").innerText = text;
    document.getElementById("upload-modal").style.display = "flex";
}

/**
 * 
 * @param text text to be shown in loading modal
 * 
 * @brief function to update modal window
 * 
 */
function updateModalText(text) {
    document.getElementById("upload-modal-text").innerText = text;
}

/**
 * 
 * @brief function to hide modal
 * 
 */
function hideModal() {
    document.getElementById("upload-modal").style.display = "none";
}

/**
 * 
 * @param metric string of use metric - for example Mos, Pesq, etc.
 * 
 * @brief creates metric section with graphs and tables
 * 
 */
function createMetricSection(metric){
    if(document.getElementById(`${metric}-section`)){
        // If this metric already exists, return
        return;
    }
    let section = document.getElementsByClassName("graphs-section")[0];
    const newSection = document.createElement('div'); //Metric section (MOS-section for example)
    newSection.classList.add('metric-section');
    newSection.id =`${metric}-section`;
    // Creates header
    const sectionHeader = document.createElement('h3');
    sectionHeader.classList.add('metric-section-header');
    sectionHeader.innerText = metric;

    //Adds event listener for each section, roll-out effect
    sectionHeader.addEventListener("click", function() {
        let content = this.nextElementSibling;
        if (content.style.maxHeight && content.style.maxHeight !== "0px") {
            content.style.maxHeight = "0px";
            content.style.padding = "0 10px";
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            content.style.padding = "10px";
        }
    });

    newSection.appendChild(sectionHeader);
    // Wrapper for graphs and tables
    const newSectionContainer = document.createElement('div');
    newSectionContainer.classList.add('metric-section-container');

    //adding charts and tables
    const newChartsContainer = document.createElement('div');
    const newTableContainer = document.createElement('div');
    newChartsContainer.classList.add('charts-container');
    newTableContainer.classList.add('tables-container');

    newSectionContainer.appendChild(newChartsContainer);
    newSectionContainer.appendChild(newTableContainer);

    newSection.appendChild(newSectionContainer);
    // append section for each metric
    section.appendChild(newSection);
}

/**
 * 
 * @param graphs json response containing graphs paths for each metric
 * 
 * @brief fucntion to display graphs based on response from /process/ endpoint
 * 
 */
function displayGraphs(graphs) {
    console.log(graphs);
    for (const [metric, paths] of Object.entries(graphs)) {
        if (!allowedMetrics.includes(metric)) continue;
        /* Select corresponding HTML element based on metric */
        console.log(metric);
        createMetricSection(metric);
        let section = document.getElementById(`${metric}-section`).querySelector(".charts-container");
        section.innerHTML = ""; /* If there are some graphs remove them */
        paths.forEach(path => {
            console.log(path);
            if (path === null || path === undefined || path === "" || path === "null") return;
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
    const mosLabels = {
        "ovrl_mos": "Overall MOS",
        "sig_mos": "Signal MOS",
        "bak_mos": "Background MOS",
        "p808_mos": "P808 MOS"
    };
    // Iterates through each section
    allowedMetrics.forEach(metric => {
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
                if (!table){
                    tableWrapper.innerHTML = `<p>There was no data provided for ${subMetric} metric due to non-intrusive evaluation only.</p>`;
                }else{
                    tableWrapper.appendChild(table);
                }
                tablesContainer.appendChild(tableWrapper);
            });
        } else {
            //Other metrics have only one table
            let table = createTable(tables.Files, tables.Values[metric]);
            if(table){
                tablesContainer.appendChild(table);
            }else{
                tablesContainer.innerHTML = `<p>There was no data provided for ${metric} metric due to non-intrusive evaluation only.</p>`;
            }
        }
    });
}

/**
 * 
 * @param files name of the files
 * @param values metric values
 * 
 * @returns created table
 * 
 * @brief Help function for table creation
 * 
 */
function createTable(files, values) {
    console.log(values);
    if (values.length === 0) {
        console.log("No data was provided for table creation");
        return null;
    }
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

/**
 * 
 * @brief gets audio samples for each file provided if possible
 * 
 */
async function getSamples() {
    try{
        //fetches audio paths
        let processResponse = await fetch('/audios/', { method: 'POST' });
        let processResult = await processResponse.json();
        // if got audio paths
        if (processResponse.ok) {
            console.log("Got a positive response for audio samples.");
            console.log(processResult);
            displaySamples(processResult.samples);
            //display them
        } else {
            console.log("Got a negative response for audio samples.");
            return;
        }
    }catch (error){
        console.log(error);
        return;
    }finally{
        console.log("Done getting samples");
        return;
    }
}

/**
 * 
 * @param samples samples to be displayed
 * 
 * @brief display audio samples for listening
 * 
 */
function displaySamples(samples){
    for (const [key, value] of Object.entries(samples)){
        console.log(`${key}: ${value}`);
        createSamplesSection(value, key); // for each file(key) -> display all samples
    }
}

/**
 * 
 * @param samples audio sample paths
 * @param label model name/file name
 * 
 * @brief creates section for each model/file presented and shows samples
 * 
 */
function createSamplesSection(samples, label){
    if (document.getElementById(label)){
        //if section exists return
        return;
    }
    let samplesSection = document.getElementById('samples-section');

    const newSection = document.createElement('div');
    newSection.id = label;
    const newHeader = document.createElement('h3');
    newHeader.innerText = label;
    const newSamplesSection = document.createElement('div');
    // for each sample create audio element
    samples.forEach(sample =>{
        var newSample = document.createElement('audio');
        newSample.controls = 'controls';
        newSample.src = sample;
        newSample.type = 'audio/mpeg'
        newSamplesSection.appendChild(newSample);
    });

    newSection.appendChild(newHeader);
    newSection.appendChild(newSamplesSection);

    samplesSection.appendChild(newSection);
}
