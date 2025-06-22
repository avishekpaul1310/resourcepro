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
            },            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: Math.max(Math.max(...utilizationData) * 1.2, 50),
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
                        '#4C51BF', // indigo-700 (good contrast)
                        '#667EEA', // indigo-500 (good contrast)
                        '#2563EB', // blue-600 (better contrast)
                        '#DC2626', // red-600 (high contrast)
                        '#F97316', // orange-500 (good contrast)
                        '#059669', // green-600 (high contrast)
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        align: 'center',
                        labels: {
                            boxWidth: 16,
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 14,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return label + ': ' + value.toFixed(1) + '%';
                            }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 20,
                        right: 20,
                        bottom: 20,
                        left: 20
                    }
                }
            }
        });
    }
});