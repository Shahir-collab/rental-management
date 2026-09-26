function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '₹0';
    return '₹' + amount.toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

document.addEventListener('DOMContentLoaded', function() {
    // Occupancy Chart
    const occCanvas = document.getElementById('occupancyChart');
    if (occCanvas) {
        new Chart(occCanvas, {
            type: 'pie',
            data: {
                labels: ['Occupied', 'Vacant'],
                datasets: [{
                    data: [occCanvas.dataset.occupied, occCanvas.dataset.vacant],
                    backgroundColor: ['#10B981', '#EF4444'],
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Tenant Type Chart
    const typeCanvas = document.getElementById('tenantTypeChart');
    if (typeCanvas) {
        new Chart(typeCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Residential', 'Commercial'],
                datasets: [{
                    data: [typeCanvas.dataset.residential, typeCanvas.dataset.commercial],
                    backgroundColor: ['#3B82F6', '#F97316'],
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Agreement Chart
    const agrCanvas = document.getElementById('agreementChart');
    if (agrCanvas) {
        new Chart(agrCanvas, {
            type: 'pie',
            data: {
                labels: ['Active', 'Expired'],
                datasets: [{
                    data: [agrCanvas.dataset.active, agrCanvas.dataset.expired],
                    backgroundColor: ['#10B981', '#F59E0B'],
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Rent Chart
    const rentCanvas = document.getElementById('rentChart');
    if (rentCanvas) {
        new Chart(rentCanvas, {
            type: 'bar',
            data: {
                labels: ['Rent Status'],
                datasets: [
                    {
                        label: 'Due',
                        data: [rentCanvas.dataset.due],
                        backgroundColor: '#3B82F6'
                    },
                    {
                        label: 'Paid',
                        data: [rentCanvas.dataset.paid],
                        backgroundColor: '#10B981'
                    },
                    {
                        label: 'Outstanding',
                        data: [rentCanvas.dataset.outstanding],
                        backgroundColor: '#EF4444'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});
