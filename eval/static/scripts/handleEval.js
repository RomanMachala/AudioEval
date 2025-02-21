async function startEvaluation() {
    const metaFile = document.getElementById('meta-file').value;
    const datasetPath = document.getElementById('dataset-path').value;

    const response = await fetch('/start-evaluation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ meta_file: metaFile, dataset_path: datasetPath }),
    });

    const data = await response.json();
    alert(data.message);

    // Poll for results every 10 seconds
    setInterval(fetchResults, 10000);
    setInterval(refreshGraphs, 10000);
}

function refreshGraphs() {
    document.getElementById("hist-mcd").src = "/static/graphs/mcd.png?" + new Date().getTime();
    document.getElementById("hist-pesq").src = "/static/graphs/pesq.png?" + new Date().getTime();
    document.getElementById("hist-stoi").src = "/static/graphs/stoi.png?" + new Date().getTime();
    document.getElementById("hist-estoi").src = "/static/graphs/estoi.png?" + new Date().getTime();
}

// Spustí se každých 5 sekund a aktualizuje obrázky



async function fetchResults() {
    const response = await fetch('/results/');
    const data = await response.json();

    const tableBody = document.querySelector('#results-table tbody');
    tableBody.innerHTML = ''; // Clear existing rows

    const progressVal = document.getElementById("progress");
    progressVal.textContent = data.progress + "%/100%";    

    data.results.forEach(result => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${result.file}</td>
            <td>${result.mcd || result.error || ''}</td>
            <td>${result.pesq || result.error || ''}</td>
            <td>${result.stoi || result.error || ''}</td>
            <td>${result.estoi || result.error || ''}</td>
        `;
        tableBody.appendChild(row);
    });
}

