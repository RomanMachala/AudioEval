/**
 * 
 * @author Roman Machala
 * @date 18.02.2025
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
export function startEvaluation(rootFolderName) {
    const metaFile = document.getElementById("meta-file").value;
    const intrusive = document.getElementById("intrusive").checked;
    const filename = document.getElementById("save-name").value;
    /* Form values, presented file, dataset path and whether to use intrusive evaluation aswell */

    /* If there were no values presented */
    if (!metaFile) {
        alert("Please enter the name of the meta file.");
        return;
    }
    /* Else start evaluation */
    fetch("/start-evaluation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meta_file: metaFile, root_folder: rootFolderName, intrusive: intrusive, save_name: filename })
    })
    .then(response => response.json())
    .then(data => {
        /* If evaluation has started correctly */
        if (data.message === "Evaluation started") {
            /* Hide select container and show evaluation progress */
            document.getElementById("evaluation").style.display = "block";
            document.getElementById("container").style.display = "none";
            disableButtonEvaluation();
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
        
        handleLog(event.data, logOutput);
        if (event.data === "Evaluation completed.") {
            enableButtonEvaluation();
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

/**
 * 
 * @param message received message
 * @param section section to display the message
 * 
 * @brief handles incoming messages and displays them in more structured way
 * 
 */
function handleLog(message, section){
    try {
        const fixedMessage = message
            .replace(/'/g, '"')
            .replace(/\bNone\b/g, 'null');
        const data = JSON.parse(fixedMessage);
        section.textContent += "Files: " + data.file + "\n";
        Object.entries(data.metrics).forEach(([metricName, values]) => {
            if(metricName === "Mos"){
                section.textContent += "Mos:\n";
                Object.entries(data.metrics.Mos).forEach(([subMetric, value]) => {
                    section.textContent += "\t" + subMetric + ": " + value + "\n";
                });
            }
            else{
                section.textContent += metricName + ": " + values + "\n";
            }
        });
        section.textContent += "\n";
        section.scrollTop = section.scrollHeight;
    } catch (error) {
        section.textContent += message + "\n";
        section.scrollTop = section.scrollHeight;
    }
}

/**
 * 
 * @brief clears form's inputs for evaluation
 * 
 */
function clearInputs(){
    document.getElementById("meta-file").value = "";
    document.getElementById("intrusive").checked = false;
    document.getElementById("save-name").value = "";
    document.getElementById('folderInput').value = "";
}

/**
 * 
 * @brief Enables button to continue after finishing evaluation
 * 
 */
function enableButtonEvaluation(){
    document.getElementById("evaluation-done").disabled = false;
}

/**
 * 
 * @brief Disables button to continue during evalaution
 * 
 */
function disableButtonEvaluation(){
    document.getElementById("evaluation-done").disabled = true;
}

/**
 * 
 * @brief handles continue button after finishing evalaution
 * 
 */
document.getElementById("evaluation-done").addEventListener("click", function (event){
    event.preventDefault();
    clearInputs();

    document.querySelector("#evaluation").style.display = "none";
    document.querySelector("#container").style.display = "block";
});