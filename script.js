window.onload = function() {
    fetchClients();

    document.getElementById('addFeatureForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const clientId = document.getElementById('client_id').value;
        const feature = document.getElementById('feature').value;
        const value = document.getElementById('value').value;
        addFeature(clientId, feature, value);
    });
};

function fetchClients() {
    // Get the table body
    var tableBody = document.getElementById('clientsTable').getElementsByTagName('tbody')[0];

    // Clear the table body
    tableBody.innerHTML = '';
    fetch('http://localhost:8080/')
        .then(response => response.json())
        .then(clients => {
            const table = document.getElementById('clientsTable');
            clients.forEach(client => {
                const row = table.insertRow();
                row.insertCell().textContent = client.client_id;
                row.insertCell().textContent = client.ip;
                row.insertCell().textContent = client.port;
                row.insertCell().textContent = client.offset;
                row.insertCell().textContent = JSON.stringify(client.features);
            });
        });
}

function addFeature(clientId, feature, value) {
    fetch(`http://localhost:8080/${clientId}/config`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            client_id: clientId,
            features: {
                [feature]: value,
            },
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        fetchClients();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}