/**
 * Task Details Modal - Simple direct implementation
 * This approach creates and manages DOM elements directly without relying on Bootstrap modal
 * to avoid the flickering issue
 */

document.addEventListener('DOMContentLoaded', () => {
    // Find all task view buttons and add click event listener
    const taskViewButtons = document.querySelectorAll('.task-view-btn');
    
    taskViewButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const taskId = button.getAttribute('data-task-id');
            
            if (!taskId) return;
            
            try {
                // Fetch task details
                const response = await fetch(`/api/tasks/${taskId}`);
                
                if (!response.ok) {
                    throw new Error('Failed to load task details');
                }
                
                const taskData = await response.json();
                
                // Create and show modal with task data
                showTaskDetailsModal(taskData);
                
            } catch (error) {
                console.error('Error loading task details:', error);
                alert('Could not load task details. Please try again later.');
            }
        });
    });
    
    // Close modal when clicking outside
    document.addEventListener('click', (e) => {
        const modal = document.querySelector('.task-details-modal');
        if (modal && e.target.classList.contains('task-details-backdrop')) {
            closeTaskDetailsModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeTaskDetailsModal();
        }
    });
});

/**
 * Create and display the task details modal
 */
function showTaskDetailsModal(task) {
    // Remove any existing modal
    closeTaskDetailsModal();
    
    // Create modal elements
    const modalContainer = document.createElement('div');
    modalContainer.className = 'task-details-modal';
    
    const modalBackdrop = document.createElement('div');
    modalBackdrop.className = 'task-details-backdrop';
    
    const modalDialog = document.createElement('div');
    modalDialog.className = 'task-details-dialog';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'task-details-content';
    
    // Modal header
    const modalHeader = document.createElement('div');
    modalHeader.className = 'task-details-header';
    
    const modalTitle = document.createElement('h5');
    modalTitle.className = 'task-details-title';
    modalTitle.textContent = `Task Details: ${task.task_id}`;
    
    const closeButton = document.createElement('button');
    closeButton.className = 'task-details-close';
    closeButton.innerHTML = '&times;';
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.addEventListener('click', closeTaskDetailsModal);
    
    modalHeader.appendChild(modalTitle);
    modalHeader.appendChild(closeButton);
    
    // Modal body with task details
    const modalBody = document.createElement('div');
    modalBody.className = 'task-details-body';
    modalBody.innerHTML = generateTaskDetailsHTML(task);
    
    // Modal footer
    const modalFooter = document.createElement('div');
    modalFooter.className = 'task-details-footer';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'btn btn-secondary';
    closeBtn.textContent = 'Close';
    closeBtn.addEventListener('click', closeTaskDetailsModal);
    
    modalFooter.appendChild(closeBtn);
    
    // Add edit button if task is completed
    if (task.status === 'completed') {
        const editBtn = document.createElement('a');
        editBtn.className = 'btn btn-warning ms-2';
        editBtn.href = `/admin/tasks/${task.task_id}/edit`;
        editBtn.innerHTML = '<i class="fas fa-pen-to-square me-1"></i>Request Edit';
        modalFooter.appendChild(editBtn);
    }
    
    // Assemble modal
    modalContent.appendChild(modalHeader);
    modalContent.appendChild(modalBody);
    modalContent.appendChild(modalFooter);
    modalDialog.appendChild(modalContent);
    modalContainer.appendChild(modalBackdrop);
    modalContainer.appendChild(modalDialog);
    
    // Add to document
    document.body.appendChild(modalContainer);
    
    // Show modal with animation
    setTimeout(() => {
        modalContainer.classList.add('show');
    }, 10);
    
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
}

/**
 * Close the task details modal
 */
function closeTaskDetailsModal() {
    const modal = document.querySelector('.task-details-modal');
    
    if (modal) {
        // Add closing animation
        modal.classList.remove('show');
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            modal.remove();
            document.body.style.overflow = '';
        }, 300);
    }
}

/**
 * Generate HTML content for the task details
 */
function generateTaskDetailsHTML(task) {
    // Format dates
    const createdDate = new Date(task.created_at).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const deadlineDate = new Date(task.deadline).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
    
    const completedDate = task.completed_at 
        ? new Date(task.completed_at).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
        : null;
    
    // Generate status badge
    let statusBadge = '';
    if (task.status === 'pending') {
        statusBadge = '<span class="badge bg-warning text-dark">Pending</span>';
    } else if (task.status === 'completed') {
        statusBadge = '<span class="badge bg-success">Completed</span>';
    } else if (task.status === 'edit_requested') {
        statusBadge = '<span class="badge bg-info">Edit Requested</span>';
    }
    
    // Generate HTML
    let html = `
        <div class="row mb-3">
            <div class="col-md-6">
                <p><strong>Assigned To:</strong> ${task.user_name}</p>
                <p><strong>Status:</strong> ${statusBadge}</p>
                <p><strong>Price:</strong> ₹${task.price.toFixed(2)}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Created:</strong> ${createdDate}</p>
                <p><strong>Deadline:</strong> ${deadlineDate}</p>
                ${completedDate ? `<p><strong>Completed:</strong> ${completedDate}</p>` : ''}
            </div>
        </div>
        
        <div class="mb-3">
            <h6>Description:</h6>
            <div class="p-3 bg-light text-dark rounded">${task.description}</div>
        </div>
    `;
    
    // Task Files
    html += `
        <div class="mb-3">
            <h6>Task Files:</h6>
            <ul class="list-group">
    `;
    
    if (task.files && task.files.task && task.files.task.length > 0) {
        task.files.task.forEach(file => {
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    ${file.original_filename}
                    <a href="/download/task/${file.filename}" class="btn btn-sm btn-primary">
                        <i class="fas fa-download me-1"></i>Download
                    </a>
                </li>
            `;
        });
    } else {
        html += '<li class="list-group-item">No files attached to this task</li>';
    }
    
    html += `
            </ul>
        </div>
    `;
    
    // Submission Files
    if (task.status === 'completed' || task.status === 'edit_requested') {
        html += `
            <div class="mb-3">
                <h6>Submission Files:</h6>
                <ul class="list-group">
        `;
        
        if (task.files && task.files.submission && task.files.submission.length > 0) {
            task.files.submission.forEach(file => {
                html += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        ${file.original_filename}
                        <a href="/download/submission/${file.filename}" class="btn btn-sm btn-success">
                            <i class="fas fa-download me-1"></i>Download
                        </a>
                    </li>
                `;
            });
        } else {
            html += '<li class="list-group-item">No submission files found</li>';
        }
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // Edit History
    if (task.edits && task.edits.length > 0) {
        html += `
            <div class="mb-3">
                <h6>Edit History:</h6>
                <div class="accordion" id="editAccordion">
        `;
        
        task.edits.forEach((edit, index) => {
            const editCreatedDate = new Date(edit.created_at).toLocaleDateString('en-IN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const editStatusBadge = edit.status === 'pending'
                ? '<span class="badge bg-warning text-dark ms-2">Pending</span>'
                : '<span class="badge bg-success ms-2">Completed</span>';
            
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="editHeading${index}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#editCollapse${index}" aria-expanded="false" aria-controls="editCollapse${index}">
                            Edit Request: ${editCreatedDate} - ${editStatusBadge}
                        </button>
                    </h2>
                    <div id="editCollapse${index}" class="accordion-collapse collapse" 
                         aria-labelledby="editHeading${index}" data-bs-parent="#editAccordion">
                        <div class="accordion-body">
                            <div class="mb-3">
                                <h6>Instructions:</h6>
                                <div class="p-3 bg-light text-dark rounded">${edit.instructions}</div>
                            </div>
            `;
            
            // Edit Instruction Files
            html += `
                <div class="mb-3">
                    <h6>Instruction Files:</h6>
                    <ul class="list-group">
            `;
            
            if (edit.files && edit.files.instruction && edit.files.instruction.length > 0) {
                edit.files.instruction.forEach(file => {
                    html += `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            ${file.original_filename}
                            <a href="/download/edit/${file.filename}" class="btn btn-sm btn-primary">
                                <i class="fas fa-download me-1"></i>Download
                            </a>
                        </li>
                    `;
                });
            } else {
                html += '<li class="list-group-item">No instruction files attached</li>';
            }
            
            html += `
                    </ul>
                </div>
            `;
            
            // Edit Submission Files
            if (edit.status === 'completed') {
                html += `
                    <div class="mb-3">
                        <h6>Edit Submission Files:</h6>
                        <ul class="list-group">
                `;
                
                if (edit.files && edit.files.submission && edit.files.submission.length > 0) {
                    edit.files.submission.forEach(file => {
                        html += `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                ${file.original_filename}
                                <a href="/download/edit/${file.filename}" class="btn btn-sm btn-success">
                                    <i class="fas fa-download me-1"></i>Download
                                </a>
                            </li>
                        `;
                    });
                } else {
                    html += '<li class="list-group-item">No edit submission files found</li>';
                }
                
                html += `
                        </ul>
                    </div>
                `;
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    return html;
}