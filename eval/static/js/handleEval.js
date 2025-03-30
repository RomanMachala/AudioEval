/**
 * 
 * @author Roman Machala
 * @date 18.05.2025
 * @brief Script file responsible for evaluation logic handling
 *          main functionality: handle evalaution submit form
 *                              start evaluation with correct files
 *                              handle and visualize evaluation progress
 * 
 */

/**
 * 
 * @brief function responsible for evaluation starting
 *          handles correctness of submited files and calls
 *          evaluation function with presented files
 * 
 */
function startEvaluation() {
    const metaFile = document.getElementById("meta-file").value;
    const datasetPath = document.getElementById("dataset-path").value;
    const intrusive = document.getElementById("intrusive").checked;
    const filename = document.getElementById("save-name").value;
    /* Form values, presented file, dataset path and whether to use intrusive evaluation aswell */

    /* If there were no values presented */
    if (!metaFile || !datasetPath) {
        alert("Please enter both meta file path and dataset path.");
        return;
    }
    /* Else start evaluation */
    fetch("/start-evaluation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meta_file: metaFile, dataset_path: datasetPath, intrusive: intrusive, save_name: filename })
    })
    .then(response => response.json())
    .then(data => {
        /* If evaluation has started correctly */
        if (data.message === "Evaluation started") {
            /* Hide select container and show evaluation progress */
            document.getElementById("evaluation").style.display = "block";
            document.getElementById("container").style.display = "none";
            startLogStream(); /* Streaming of logs */
        } else {
            /* If eval hasn't started correctly atleast let know */
            alert(data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}

/**
 * 
 * @brief function responsible for handling streaming form server
 * 
 */
function startLogStream() {
    const logOutput = document.getElementById("log-output");
    logOutput.textContent = ""; /* Delete previous logs */

    /* Wait for incoming log messages */
    const eventSource = new EventSource("/log-stream/");
    /* On new incoming message */
    eventSource.onmessage = function(event) {
        logOutput.textContent += event.data + "\n";
        logOutput.scrollTop = logOutput.scrollHeight;
        if (event.data === "Evaluation completed.") {
            console.log("Evaluation completed, disconnecting.");
            eventSource.close();
        }
        /* Append message to the "console" and scroll to last message */
    };
    /* In case an error occures print to console */
    eventSource.onerror = function() {
        console.error("Log stream disconnected.");
        eventSource.close();
        /* Close streaming source */
    };
}

