async function startEvaluation() {
    const metaFile = document.getElementById('meta-file').value;
    const datasetPath = document.getElementById('dataset-path').value;

    try {
        const response = await fetch('/start-evaluation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ meta_file: metaFile, dataset_path: datasetPath }),
        });

        if (!response.ok) {
            logMessage(`❌ Error: ${response.status} - ${response.statusText}`);
            return;
        }

        const data = await response.json();
        logMessage("✅ === Starting evaluation... ===");
        logMessage(`📂 Meta file: ${metaFile}`);
        logMessage(`📁 Dataset path: ${datasetPath}`);

        // Skrytí výběrového formuláře a zobrazení logovacího okna
        document.getElementById("container").style.display = "none";
        document.getElementById("evaluation").style.display = "block";

        alert(data.message);
        setInterval(fetchResults, 5000); // Každých 5s kontrolovat progress

    } catch (error) {
        console.error("Error fetching evaluation:", error);
        logMessage("❌ Failed to start evaluation.");
    }
}

async function fetchResults() {
    const response = await fetch('/results/');
    const data = await response.json();

    logMessage(`🔄 Progress: ${data.progress}%`);

    data.results.forEach(result => {
        logMessage(
            `📄 File: ${result.file}, MCD: ${result.mcd || "N/A"}, PESQ: ${result.pesq || "N/A"}, STOI: ${result.stoi || "N/A"}, ESTOI: ${result.estoi || "N/A"}`
        );
    });

    if (data.progress >= 100) {
        logMessage("🎉 Evaluation complete!");
    }
}

function logMessage(message) {
    const logDiv = document.getElementById("log-output");
    if (!logDiv) return;

    const logEntry = document.createElement("p");
    logEntry.textContent = message;
    logDiv.appendChild(logEntry);

    // Auto-scroll dolů
    logDiv.scrollTop = logDiv.scrollHeight;
}
