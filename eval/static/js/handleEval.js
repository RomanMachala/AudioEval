function startEvaluation() {
    const metaFile = document.getElementById("meta-file").value;
    const datasetPath = document.getElementById("dataset-path").value;

    if (!metaFile || !datasetPath) {
        alert("Please enter both meta file path and dataset path.");
        return;
    }

    fetch("/start-evaluation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meta_file: metaFile, dataset_path: datasetPath })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Evaluation started") {
            document.getElementById("evaluation").style.display = "block"; // Zobrazí celý evaluation blok
            document.getElementById("container").style.display = "none";
            startLogStream(); // Spustí streamování logů
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}

function startLogStream() {
    const logOutput = document.getElementById("log-output");
    logOutput.textContent = "";  // Vymaže předchozí logy

    const eventSource = new EventSource("/log-stream/");
    eventSource.onmessage = function(event) {
        logOutput.textContent += event.data + "\n";  // Přidá nový řádek logu
        logOutput.scrollTop = logOutput.scrollHeight;  // Posun na konec logu
    };

    eventSource.onerror = function() {
        console.error("Log stream disconnected.");
        eventSource.close();
    };
}

