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
            displayGraphs(processResult.generated_plots.plots);
            displayTables(processResult.generated_plots.tables);
            console.log(processResult.generated_plots);
            console.log(processResult.generated_plots.tables);
        } else {
            updateModalText("Error generating graphs.");
            alert("Error generating graphs.");
            return;
        }
    }catch (error){
        console.warn(error);
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
export function showModal(text) {
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
export function updateModalText(text) {
    document.getElementById("upload-modal-text").innerText = text;
}

/**
 * 
 * @brief function to hide modal
 * 
 */
 export function hideModal() {
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
    for (const [metric, paths] of Object.entries(graphs)) {
        /* Select corresponding HTML element based on metric */
        createMetricSection(metric);
        let section = document.getElementById(`${metric}-section`).querySelector(".charts-container");
        section.innerHTML = ""; /* If there are some graphs remove them */
        paths.forEach(path => {
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
    let count = 0;
    const mosLabels = {
        "ovrl_mos": "Overall MOS",
        "sig_mos": "Signal MOS",
        "bak_mos": "Background MOS",
        "p808_mos": "P808 MOS"
    };
    // Iterates through each section
    Object.entries(tables.Values).forEach(([metricName, metric]) => {
        if (!metric) return;
        if(metricName in mosLabels){
                let section = document.getElementById('Mos-section');
                if (!section) {
                    console.warn(`No section for ${metricName} metric.`);
                    return;
                }
                let tablesContainer = section.querySelector(".tables-container");
                if (count === 0){
                    tablesContainer.innerHTML = ""; // Removes previous tables
                }
                count += 1;
                let tableWrapper = document.createElement("div");
                tableWrapper.classList.add("mos-table-wrapper");

                let title = document.createElement("h4");
                title.innerText = mosLabels[metricName];
                tableWrapper.appendChild(title);
                // For each table we fill it with values
                console.log("Creating table for ");
                console.log(metricName);
                let table = createTable(tables.Files, tables.Values[metricName]);
                if (!table){
                    tableWrapper.innerHTML = `<p>There was no data provided for ${metricName} metric due to non-intrusive evaluation only.</p>`;
                }else{
                    tableWrapper.appendChild(table);
                }
                tablesContainer.appendChild(tableWrapper);
        }else{
            let section = document.getElementById(`${metricName}-section`);
            if (!section) {
                console.warn(`No section for ${metricName} metric.`);
                return;
            }
            let tablesContainer = section.querySelector(".tables-container");
            tablesContainer.innerHTML = ""; // Removes previous tables

    
            //Other metrics have only one table
            let table = createTable(tables.Files, tables.Values[metricName]);
            if(table){
                tablesContainer.appendChild(table);
            }else{
                tablesContainer.innerHTML = `<p>There was no data provided for ${metricName} metric due to non-intrusive evaluation only.</p>`;
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
 * Event listener for switching between analysis section and section to choose options.
 * 
 */
document.getElementById("back-button").addEventListener("click", function (event){
    event.preventDefault();
    goBackToSelect();
});

/**
 * 
 * Help function for value formatting
 * 
 * @param value value to be formatted
 * @returns formatted value
 */
function formatValue(value) {
    return value === null || value === undefined || isNaN(value) ? "N/A" : value.toFixed(2);
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
            displaySamples(processResult.samples);
            //display them
        } else {
            console.warn("Got a negative response for audio samples.");
            return;
        }
    }catch (error){
        console.warn(error);
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
function displaySamples(samples) {
    const samplesContainer = document.getElementById("samples-section");
    samplesContainer.innerHTML = "";

    for (const [filename, types] of Object.entries(samples)) {
        createSamplesSection(types, filename);
    }
}


/**
 * 
 * @param types sample types - ref and gen lists containing audio sample paths
 * @param label model name/file name
 * 
 * @brief creates section for each model/file presented and shows samples
 * 
 */
function createSamplesSection(types, label) {
    if (document.getElementById(label)) {
        return;
    }

    const samplesSection = document.getElementById('samples-section');

    const newSection = document.createElement('div');
    newSection.id = label;
    newSection.classList.add("main-sample-section");

    const newHeader = document.createElement('h3');
    newHeader.innerText = label;
    newSection.appendChild(newHeader);

    for (const [subLabel, audioArray] of Object.entries(types)) {
        const subSection = document.createElement('div');
        subSection.classList.add("sub-sample-section");

        const subHeader = document.createElement('h4');
        subHeader.innerText = subLabel;
        subSection.appendChild(subHeader);

        const audioContainer = document.createElement('div');

        const validAudios = audioArray.filter(path => path && path !== "None");

        if (validAudios.length === 0) {
            const warning = document.createElement('p');
            warning.innerText = 'No audio samples available.';
            audioContainer.appendChild(warning);
        } else {
            validAudios.forEach(sample => {
                const newSample = document.createElement('audio');
                newSample.controls = true;
                newSample.src = sample;
                newSample.type = 'audio/mpeg';
                audioContainer.appendChild(newSample);
            });
        }

        subSection.appendChild(audioContainer);
        newSection.appendChild(subSection);
    }

    samplesSection.appendChild(newSection);
}

/**
 * 
 * Event listener for clearing previous analysisis
 * 
 */
document.getElementById("analysis-clear-button").addEventListener("click", function (event){
    event.preventDefault();
    clearCache();
});

/**
 * 
 * @brief simple function to clear cache, used when previous evaluations are not needed anymore
 *          removes all graphs and mentiones of previous evaluations
 * 
 */
async function clearCache(){
    try{
        // calls an endpoint for cache clearing
        let processResponse = await fetch('/clear_cache/', { method: 'POST' });
        let processResult = await processResponse.json();

        if(processResponse.ok){
            alert("Cached has been cleared: " + processResult.status);
        }else{
            alert("Something went wron while trying to clear cache.");
        }
    }catch (e){
        alert("An error occured while trying to clear cache.");
    }
}
