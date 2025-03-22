document.addEventListener('DOMContentLoaded', function() {
    // Resource Utilization Chart
    const utilizationCtx = document.getElementById('utilizationChart');
    if (utilizationCtx) {
        const resourceNames = JSON.parse(utilizationCtx.dataset.labels);
        const utilizationData = JSON.parse(utilizationCtx.dataset.values);
        const colors = JSON.parse(utilizationCtx.dataset.colors);
        
        new Chart(utilizationCtx, {
            type: 'bar',
            data: {
                labels: resourceNames,
                datasets: [{
                    label: 'Utilization (%)',
                    data: utilizationData,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 120,
                        title: {
                            display: true,
                            text: 'Utilization (%)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Project Progress Chart
    const progressCtx = document.getElementById('progressChart');
    if (progressCtx) {
        const projectNames = JSON.parse(progressCtx.dataset.labels);
        const progressData = JSON.parse(progressCtx.dataset.values);
        
        new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: projectNames,
                datasets: [{
                    data: progressData,
                    backgroundColor: [
                        '#4C51BF', // indigo-800
                        '#667EEA', // indigo-500
                        '#A3BFFA', // indigo-300
                        '#EBF4FF', // indigo-100
                        '#F97316', // orange-500
                        '#FDBA74', // orange-300
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
});