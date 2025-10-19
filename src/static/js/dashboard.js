document.addEventListener('DOMContentLoaded', function() {
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        console.log('WebSocket connected');
    });

    socket.on('update_data', function(data) {
        updateDashboard(data);
    });

    function updateDashboard(data) {
        const dashboardContainer = document.getElementById('dashboard-container');
        dashboardContainer.innerHTML = ''; // Clear existing data

        data.forEach(item => {
            const alertElement = document.createElement('div');
            alertElement.className = 'alert-item';
            alertElement.innerHTML = `
                <strong>${item.timestamp}</strong>: ${item.message}
            `;
            dashboardContainer.appendChild(alertElement);
        });
    }
});