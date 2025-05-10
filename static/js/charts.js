/**
 * Chart.js utility functions for Task Management System dashboards
 */

/**
 * Safely parses JSON with fallback
 * @param {string} jsonString - JSON string to parse
 * @param {any} fallback - Fallback value if parsing fails
 * @returns {any} - Parsed JSON or fallback
 */
function safeJsonParse(jsonString, fallback) {
    try {
        return JSON.parse(jsonString) || fallback;
    } catch (e) {
        console.error('Error parsing JSON:', e);
        return fallback;
    }
}

/**
 * Gets CSS variable value
 * @param {string} variableName - CSS variable name
 * @returns {string} - CSS variable value
 */
function getCssVariable(variableName) {
    return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
}

/**
 * Initializes a task completion progress chart with stacked bars
 * @param {string} elementId - Canvas element ID
 * @param {Object} data - Chart data containing completed and pending tasks by month
 * @param {Array} labels - Month names
 */
function initTaskCompletionProgressChart(elementId, data, labels) {
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.warn(`Canvas element with ID '${elementId}' not found.`);
        return;
    }
    
    // Set fixed height for better mobile display
    ctx.style.height = '300px';
    
    // Colors for dark theme
    const completedColor = 'rgb(77, 169, 169)'; // Teal for completed tasks
    const pendingColor = 'rgb(148, 116, 89)';  // Brown for pending tasks
    const editRequestedColor = 'rgb(92, 102, 168)';  // Purple for edit requested tasks
    
    // Get the data from the passed object
    const completedTasks = data.completed || [];
    const pendingTasks = data.pending || [];
    const editRequestedTasks = data.edit_requested || [];
    
    try {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Completed Tasks',
                        data: completedTasks,
                        backgroundColor: completedColor,
                        borderColor: completedColor,
                        borderWidth: 0,
                        barPercentage: 0.5,
                        categoryPercentage: 0.8
                    },
                    {
                        label: 'Pending Tasks',
                        data: pendingTasks,
                        backgroundColor: pendingColor,
                        borderColor: pendingColor,
                        borderWidth: 0,
                        barPercentage: 0.5,
                        categoryPercentage: 0.8
                    },
                    {
                        label: 'Edit Requested Tasks',
                        data: editRequestedTasks,
                        backgroundColor: editRequestedColor,
                        borderColor: editRequestedColor,
                        borderWidth: 0,
                        barPercentage: 0.5,
                        categoryPercentage: 0.8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            color: '#9aa0ac'
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    title: {
                        display: true,
                        text: 'Task Completion by Month',
                        position: 'top',
                        align: 'center',
                        color: '#9aa0ac',
                        font: {
                            size: 12
                        },
                        padding: {
                            top: 0,
                            bottom: 10
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#9aa0ac'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        suggestedMax: 5,
                        grid: {
                            color: 'rgba(154, 160, 172, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            precision: 0,
                            color: '#9aa0ac',
                            callback: function(value) {
                                return value.toFixed(1);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating task completion progress chart:', error);
        ctx.parentNode.innerHTML = '<div class="alert alert-warning">Chart could not be loaded. Please refresh the page.</div>';
    }
}

/**
 * Initializes a task completion progress chart with stacked bars
 * @param {string} elementId - Canvas element ID
 * @param {Object} data - Chart data containing completed and pending tasks by month
 * @param {Array} labels - Month names
 */
function initTaskCompletionProgressChart(elementId, data, labels) {
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.warn(`Canvas element with ID '${elementId}' not found.`);
        return;
    }
    
    // Log the data being used for debugging
    console.log('Task completion progress chart data:', data);
    
    // Ensure container has proper dimensions
    const container = ctx.parentNode;
    container.style.height = '300px';
    container.style.position = 'relative';
    container.style.width = '100%';
    
    // Set fixed height for better mobile display
    ctx.style.height = '100%';
    ctx.style.width = '100%';
    
    // Get theme colors exactly like in the provided image
    const completedColor = 'rgba(122, 190, 190, 0.8)'; // Teal for completed tasks
    const pendingColor = 'rgba(146, 111, 91, 0.8)';    // Brown for pending tasks
    
    // Parse data or use empty arrays if unavailable
    const completedTasks = data.completed || new Array(labels.length).fill(0);
    const pendingTasks = data.pending || new Array(labels.length).fill(0);
    // Not using edit_requested tasks as per the reference image
    
    // Make sure we always have data to display - no need to check
    const hasData = true;
    
    try {
        // Always display charts with at least default data
        // This ensures visual consistency with the reference image
        
        // Destroy existing chart if any
        if (window.taskProgressChart) {
            window.taskProgressChart.destroy();
        }
        
        window.taskProgressChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Completed Tasks',
                        data: completedTasks,
                        backgroundColor: completedColor,
                        borderColor: completedColor,
                        borderWidth: 0
                    },
                    {
                        label: 'Pending Tasks',
                        data: pendingTasks,
                        backgroundColor: pendingColor,
                        borderColor: pendingColor,
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Month',
                            color: '#9aa0ac'
                        },
                        ticks: {
                            color: '#9aa0ac'
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Tasks',
                            color: '#9aa0ac'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            precision: 0,
                            color: '#9aa0ac'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'start',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            color: '#9aa0ac'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Task Completion by Month',
                        color: '#9aa0ac',
                        font: {
                            size: 12
                        },
                        padding: {
                            top: 0,
                            bottom: 10
                        }
                    },
                    tooltip: {
                        padding: 12,
                        bodyFont: {
                            size: 14
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating task completion chart:', error);
        ctx.parentNode.innerHTML = '<div class="alert alert-warning">Chart could not be loaded. Please refresh the page.</div>';
    }
}

/**
 * Initializes a monthly budget/earnings chart
 * @param {string} elementId - Canvas element ID
 * @param {Array} data - Monthly budget amounts
 * @param {Array} labels - Month names
 * @param {string} label - Chart label text
 */
function initMonthlyBudgetChart(elementId, data, labels, label = 'Budget (₹)') {
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.warn(`Canvas element with ID '${elementId}' not found.`);
        return;
    }
    
    // Set fixed height for better mobile display
    ctx.style.height = '300px';
    
    // Get theme colors for dark theme
    const lineColor = 'rgb(33, 148, 243)'; // Blue color
    
    try {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Budget (Completed Tasks)',
                    data: data,
                    backgroundColor: 'transparent',
                    borderColor: lineColor,
                    borderWidth: 2,
                    fill: false,
                    tension: 0.2,
                    pointBackgroundColor: lineColor,
                    pointBorderColor: lineColor,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            color: '#9aa0ac'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Monthly Budget from Completed Tasks',
                        position: 'top',
                        align: 'center',
                        color: '#9aa0ac',
                        font: {
                            size: 12
                        },
                        padding: {
                            top: 0,
                            bottom: 10
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += '₹' + context.parsed.y.toFixed(0);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#9aa0ac'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(154, 160, 172, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#9aa0ac',
                            callback: function(value) {
                                return '₹' + value;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating budget chart:', error);
        ctx.parentNode.innerHTML = '<div class="alert alert-warning">Chart could not be loaded. Please refresh the page.</div>';
    }
}

/**
 * Initializes a task status distribution chart
 * @param {string} elementId - Canvas element ID
 * @param {Object} data - Task counts by status
 */
function initTaskStatusChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.warn(`Canvas element with ID '${elementId}' not found.`);
        return;
    }
    
    // Log the data being used for debugging
    console.log('Task status chart data:', data);
    
    // Ensure container has proper dimensions
    const container = ctx.parentNode;
    container.style.height = '300px';
    container.style.position = 'relative';
    container.style.width = '100%';
    
    // Set fixed height for better mobile display
    ctx.style.height = '100%';
    ctx.style.width = '100%';
    
    // Get theme colors exactly like in the provided image
    const completedColor = 'rgb(122, 190, 190)'; // Teal for completed
    const pendingColor = 'rgb(146, 111, 91)';    // Brown for pending
    
    // Ensure we have valid data - use 0 as default value if not provided
    const pending = parseInt(data.pending) || 0;
    const completed = parseInt(data.completed) || 0;
    
    // Make sure we always have data to show
    const hasData = true;
    
    try {
        // Always create a chart even with default data
        // This ensures visual consistency with the reference image
        
        // Destroy existing chart if any
        if (window.taskStatusChart) {
            window.taskStatusChart.destroy();
        }
        
        window.taskStatusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Pending'],
                datasets: [{
                    data: [completed, pending],
                    backgroundColor: [
                        completedColor,
                        pendingColor
                    ],
                    borderColor: [
                        completedColor,
                        pendingColor
                    ],
                    borderWidth: 0,
                    cutout: '70%',
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'start',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            color: '#9aa0ac'
                        }
                    },
                    title: {
                        display: false,
                        text: '',
                        position: 'top',
                        align: 'center',
                        color: '#9aa0ac',
                        font: {
                            size: 12
                        },
                        padding: {
                            top: 0,
                            bottom: 10
                        }
                    },
                    tooltip: {
                        padding: 12,
                        bodyFont: {
                            size: 14
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating status chart:', error);
        container.innerHTML = '<div class="alert alert-warning">Chart could not be loaded. Please refresh the page.</div>';
    }
}

/**
 * Initializes charts on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chart.js initialization...');
    
    // Add debug information
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded!');
        document.querySelectorAll('canvas').forEach(canvas => {
            canvas.parentNode.innerHTML = '<div class="alert alert-danger">Chart.js library could not be loaded. Please check your internet connection and refresh the page.</div>';
        });
        return;
    }
    
    console.log('Chart.js version:', Chart.version);
    
    // Add debugging for time period
    const timePeriodButtons = document.querySelectorAll('.btn-group a');
    const currentTimePeriod = Array.from(timePeriodButtons).find(btn => btn.classList.contains('btn-dark'))?.textContent || 'Year';
    console.log('Current time period:', currentTimePeriod);
    
    // Admin Dashboard Charts
    const adminTaskChart = document.getElementById('adminTaskChart');
    if (adminTaskChart) {
        console.log('Initializing admin task chart...');
        try {
            // Get the data from data attributes
            const taskData = {
                completed: safeJsonParse(adminTaskChart.dataset.completedTasks, [0,0,0,0,0,0,0,0,0,0,0,0]),
                pending: safeJsonParse(adminTaskChart.dataset.pendingTasks, [0,0,0,0,0,0,0,0,0,0,0,0]),
                edit_requested: safeJsonParse(adminTaskChart.dataset.editTasks, [0,0,0,0,0,0,0,0,0,0,0,0])
            };
            // Get the labels (months) from the server
            let labels = safeJsonParse(adminTaskChart.dataset.labels, ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
            
            // Process month labels for display
            // For all time periods, just use the first 3 letters of each month name for consistency
            labels = labels.map(month => {
                // Handle case where we have full month names (January, February, etc.)
                if (month.length > 3) {
                    return month.substring(0, 3);
                }
                return month;
            });
            
            console.log('Chart data for time period', currentTimePeriod, ':', {labels, taskData});
            initTaskCompletionProgressChart('adminTaskChart', taskData, labels);
        } catch (e) {
            console.error('Error initializing task completion chart:', e);
        }
    }
    
    const adminBudgetChart = document.getElementById('adminBudgetChart');
    if (adminBudgetChart) {
        console.log('Initializing admin budget chart...');
        const budget = safeJsonParse(adminBudgetChart.dataset.budget, [0,0,0,0,0,0,0,0,0,0,0,0]);
        let labels = safeJsonParse(adminBudgetChart.dataset.labels, ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
        
        // Process month labels for display
        // For all time periods, just use the first 3 letters of each month name for consistency
        labels = labels.map(month => {
            // Handle case where we have full month names (January, February, etc.)
            if (month.length > 3) {
                return month.substring(0, 3);
            }
            return month;
        });
        
        initMonthlyBudgetChart('adminBudgetChart', budget, labels, 'Budget (Completed Tasks)');
    }
    
    const adminStatusChart = document.getElementById('adminStatusChart');
    if (adminStatusChart) {
        console.log('Initializing admin status chart...');
        try {
            // Default data for chart - ensure we have data to display
            let statusData = {
                pending: 0,
                completed: 0
            };
            
            // Try to parse the status data from the data attribute
            if (adminStatusChart.dataset.status) {
                try {
                    const parsedData = JSON.parse(adminStatusChart.dataset.status);
                    console.log('Parsed status data:', parsedData);
                    
                    if (parsedData) {
                        // Only include the data we need for our chart (pending and completed)
                        statusData.pending = parseInt(parsedData.pending) || 0;
                        statusData.completed = parseInt(parsedData.completed) || 0;
                    }
                } catch (e) {
                    console.error('Failed to parse status data:', e);
                }
            }
            
            console.log('Status data for chart:', statusData);
            initTaskStatusChart('adminStatusChart', statusData);
        } catch (e) {
            console.error('Error initializing status chart:', e);
        }
    }
    
    // User Dashboard Charts
    const userTaskChart = document.getElementById('userTaskChart');
    if (userTaskChart) {
        console.log('Initializing user task chart...');
        try {
            const taskData = {
                completed: safeJsonParse(userTaskChart.dataset.completedTasks, [0,0,0,0,0,0,0,0,0,0,0,0]),
                pending: safeJsonParse(userTaskChart.dataset.pendingTasks, [0,0,0,0,0,0,0,0,0,0,0,0]),
                edit_requested: safeJsonParse(userTaskChart.dataset.editTasks, [0,0,0,0,0,0,0,0,0,0,0,0])
            };
            let labels = safeJsonParse(userTaskChart.dataset.labels, ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
            
            // Process month labels for display
            // For all time periods, just use the first 3 letters of each month name for consistency
            labels = labels.map(month => {
                // Handle case where we have full month names (January, February, etc.)
                if (month.length > 3) {
                    return month.substring(0, 3);
                }
                return month;
            });
            
            initTaskCompletionProgressChart('userTaskChart', taskData, labels);
        } catch (e) {
            console.error('Error initializing user task completion chart:', e);
        }
    }
    
    const userEarningsChart = document.getElementById('userEarningsChart');
    if (userEarningsChart) {
        console.log('Initializing user earnings chart...');
        const earnings = safeJsonParse(userEarningsChart.dataset.earnings, [0,0,0,0,0,0,0,0,0,0,0,0]);
        let labels = safeJsonParse(userEarningsChart.dataset.labels, ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
        
        // Process month labels for display
        // For all time periods, just use the first 3 letters of each month name for consistency
        labels = labels.map(month => {
            // Handle case where we have full month names (January, February, etc.)
            if (month.length > 3) {
                return month.substring(0, 3);
            }
            return month;
        });
        
        initMonthlyBudgetChart('userEarningsChart', earnings, labels, 'Earnings (₹)');
    }
    
    const userStatusChart = document.getElementById('userStatusChart');
    if (userStatusChart) {
        console.log('Initializing user status chart...');
        try {
            // Default data for chart - ensure we have data to display
            let statusData = {
                pending: 0,
                completed: 0
            };
            
            // Try to parse the status data from the data attribute
            if (userStatusChart.dataset.status) {
                try {
                    const parsedData = JSON.parse(userStatusChart.dataset.status);
                    console.log('Parsed user status data:', parsedData);
                    
                    if (parsedData) {
                        // Only include the data we need for our chart (pending and completed)
                        statusData.pending = parseInt(parsedData.pending) || 0;
                        statusData.completed = parseInt(parsedData.completed) || 0;
                    }
                } catch (e) {
                    console.error('Failed to parse user status data:', e);
                }
            }
            
            console.log('User status data for chart:', statusData);
            initTaskStatusChart('userStatusChart', statusData);
        } catch (e) {
            console.error('Error initializing user status chart:', e);
        }
    }
});