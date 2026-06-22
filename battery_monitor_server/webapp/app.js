const voltageDataSmooth = [];
const voltageDataRaw = [];
const currentDataSmooth = [];
const currentDataRaw = [];
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
        legend: {
            display: true,
            labels: {
                color: '#e0e0e0'
            }
        }
    }
};

const voltageCtx = document.getElementById("voltageChart").getContext('2d');
const voltageChart = new Chart(voltageCtx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [
            {
                label: "Voltage Smooth",
                data: voltageDataSmooth,
                borderColor: "#03dac6",
                backgroundColor: "rgba(3, 218, 198, 0.0)",
                fill: false,
                tension: 0.4,
                pointRadius: 0,
                borderWidth: 3,
            },
            {
                label: "Voltage Raw",
                data: voltageDataRaw,
                borderColor: "#bb86fc",
                backgroundColor: "rgba(187, 134, 252, 0.0)",
                fill: false,
                tension: 0.4,
                pointRadius: 0,
                borderWidth: 1,
            }
        ]
    },
    options: chartOptions
});

const currentCtx = document.getElementById("currentChart").getContext('2d');
const currentChart = new Chart(currentCtx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [
            {
                label: "Current Smooth",
                data: currentDataSmooth,
                borderColor: "#cf6679",
                backgroundColor: "rgba(207, 102, 121, 0.0)",
                fill: false,
                tension: 0.4,
                pointRadius: 0,
                borderWidth: 3,
            },
            {
                label: "Current Raw",
                data: currentDataRaw,
                borderColor: "#ffd54f",
                backgroundColor: "rgba(255, 213, 79, 0.0)",
                fill: false,
                tension: 0.4,
                pointRadius: 0,
                borderWidth: 1,
            }
        ]
    },
    options: chartOptions
});

function parseMaybeString(data) {
    return typeof data === 'string' ? JSON.parse(data) : data;
}

const currentVoltageLabel = document.getElementById("currentVoltage");
const capacityLeftLabel = document.getElementById("capacityLeft");
const timeLeftLabel = document.getElementById("timeLeft");
// const stateOfChargeLabel = document.getElementById("stateOfCharge");
const stateOfChargeValue = document.getElementById("stateOfChargeValue");

async function update() {
    try {
        const [resSmooth, resRaw] = await Promise.all([
            fetch("/api/telemetry/smooth"),
            fetch("/api/telemetry/raw")
        ]);

        let smooth = parseMaybeString(await resSmooth.json());
        let raw = parseMaybeString(await resRaw.json());

        const now = new Date().toLocaleTimeString();

        labels.push(now);
        voltageDataSmooth.push(smooth.voltage.toFixed(2));
        voltageDataRaw.push(raw.voltage.toFixed(2));
        currentDataSmooth.push(smooth.current.toFixed(2));
        currentDataRaw.push(raw.current.toFixed(2));

        currentVoltageLabel.textContent = `Current smooth voltage: ${smooth.voltage.toFixed(2)} V`;
        capacityLeftLabel.textContent = `Capacity left: ${smooth.remainingCapacity.toFixed(2)} A/h`;
        timeLeftLabel.textContent = `Time left: ${smooth.remainingTime.toFixed(2)} `;

        let lowPowerAlert = smooth.lowPowerAlert

        stateOfChargeValue.textContent = smooth.stateOfCharge.toFixed(2);

        stateOfChargeValue.style.color = lowPowerAlert ? "#cf6679" : "#4caf50";

        // stateOfChargeLabel.textContent = `State of charge: ${smooth.stateOfCharge.toFixed(2)} `;

        if (labels.length > MAX_POINTS) {
            labels.shift();
            voltageDataSmooth.shift();
            voltageDataRaw.shift();
            currentDataSmooth.shift();
            currentDataRaw.shift();
        }

        voltageChart.update();
        currentChart.update();
    } catch (e) {
        console.error("Failed to fetch telemetry:", e);
    }
}

setInterval(update, 50);
update();
