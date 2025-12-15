/* Custom Reports Dashboard JavaScript */

(function() {
    'use strict';

    // Initialize charts when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeResourceCharts();
        initializeProgressBars();
    });

    function initializeResourceCharts() {
        const chartCanvas = document.getElementById('resourceChart');
        if (!chartCanvas) return;

        // Get data from template context
        const quotaData = window.quotaData || {};
        
        if (Object.keys(quotaData).length === 0) {
            console.warn('No quota data available for charts');
            return;
        }

        const ctx = chartCanvas.getContext('2d');
        
        // Create responsive chart
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    'Instances Used',
                    'Instances Available',
                    'Cores Used', 
                    'Cores Available',
                    'RAM Used (MB)',
                    'RAM Available (MB)'
                ],
                datasets: [{
                    data: [
                        quotaData.compute.instances.used,
                        Math.max(0, quotaData.compute.instances.limit - quotaData.compute.instances.used),
                        quotaData.compute.cores.used,
                        Math.max(0, quotaData.compute.cores.limit - quotaData.compute.cores.used),
                        quotaData.compute.ram.used,
                        Math.max(0, quotaData.compute.ram.limit - quotaData.compute.ram.used)
                    ],
                    backgroundColor: [
                        '#FF6384',  // Instances Used
                        '#FFE6E6',  // Instances Available
                        '#36A2EB',  // Cores Used
                        '#E6F3FF',  // Cores Available
                        '#FFCE56',  // RAM Used
                        '#FFF6E6'   // RAM Available
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Resource Usage Distribution',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
    }

    function initializeProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        progressBars.forEach(function(bar) {
            const width = bar.style.width;
            const percentage = parseFloat(width);
            
            // Add color coding based on usage percentage
            if (percentage >= 90) {
                bar.classList.add('bg-danger');
            } else if (percentage >= 75) {
                bar.classList.add('bg-warning');
            } else {
                bar.classList.add('bg-success');
            }
            
            // Animate progress bars
            bar.style.width = '0%';
            setTimeout(function() {
                bar.style.width = width;
            }, 100);
        });
    }

    // Export functions for global access if needed
    window.CustomReports = {
        initializeResourceCharts: initializeResourceCharts,
        initializeProgressBars: initializeProgressBars
    };

})();
