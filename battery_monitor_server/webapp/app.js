const voltageData = [];
const currentData = [];
const labels = [];
const MAX_POINTS = 50;

const chartOptions = {
    animation: false,
    responsive: true,
    scales: {
        x: {
            display: true,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { display: false }
        },
        y: {
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#e0e0e0' }
        }
    },
    plugins: {
        legend: { display: false }
    }
};

const voltageCtx = document.getElementById("voltageChart").getContext('2d');
const voltageChart = new Chart(voltageCtx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "Voltage (V)",
            data: voltageData,
            borderColor: "#03dac6",
            backgroundColor: "rgba(3, 218, 198, 0.1)",
            fill: true,
            tension: 0.4,
            pointRadius: 0
        }]
    },
    options: chartOptions
});

const currentCtx = document.getElementById("currentChart").getContext('2d');
const currentChart = new Chart(currentCtx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "Current (A)",
            data: currentData,
            borderColor: "#cf6679",
            backgroundColor: "rgba(207, 102, 121, 0.1)",
            fill: true,
            tension: 0.4,
            pointRadius: 0
        }]
    },
    options: chartOptions
});

async function update() {
    try {
        const res = await fetch("/api/telemetry");
        let data = await res.json();
        // The backend might return a double-encoded JSON or a simple object depending on implementation
        // dashboard.py does json.dumps(self.telemetry.read()), which FastAPI might double encode if returned as a string.
        // Let's handle both.
        if (typeof data === 'string') {
            data = JSON.parse(data);
        }

        const now = new Date().toLocaleTimeString();

        // push new values
        voltageData.push(data.voltage);
        currentData.push(data.current);
        labels.push(now);

        // keep last N points
        if (voltageData.length > MAX_POINTS) {
            voltageData.shift();
            currentData.shift();
            labels.shift();
        }

        voltageChart.update();
        currentChart.update();
    } catch (e) {
        console.error("Failed to fetch telemetry:", e);
    }
}

setInterval(update, 500);
update();
