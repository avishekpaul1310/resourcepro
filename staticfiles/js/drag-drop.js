document.addEventListener('DOMContentLoaded', function() {
    const tasks = document.querySelectorAll('.task-card');
    const dropZones = document.querySelectorAll('.resource-assignments');
    const modal = document.querySelector('.modal-overlay');
    const modalClose = document.querySelector('.modal-close');
    const cancelButton = document.querySelector('.modal-actions .btn-secondary');
    const confirmButton = document.querySelector('.modal-actions .btn-primary');
    
    let currentTaskId = null;
    let currentResourceId = null;
    
    // Make tasks draggable
    tasks.forEach(task => {
        task.setAttribute('draggable', true);
        
        task.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', task.dataset.taskId);
            currentTaskId = task.dataset.taskId;
        });
    });
    
    // Set up drop zones
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            zone.classList.add('drag-hover');
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-hover');
        });
        
        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('drag-hover');
            
            const taskId = e.dataTransfer.getData('text/plain');
            const resourceId = zone.dataset.resourceId;
            
            currentTaskId = taskId;
            currentResourceId = resourceId;
            
            // Check for conflicts
            checkForConflicts(taskId, resourceId);
        });
    });
    
    // Function to check for conflicts
    function checkForConflicts(taskId, resourceId) {
        fetch(`/api/check-conflicts/?task_id=${taskId}&resource_id=${resourceId}`)
            .then(response => response.json())
            .then(data => {
                if (data.conflicts && data.conflicts.length > 0) {
                    showConflictModal(data);
                } else {
                    assignResource(taskId, resourceId);
                }
            });
    }
    
    // Function to show conflict modal
    function showConflictModal(data) {
        const conflictTitle = document.querySelector('.conflict-title');
        const conflictDetails = document.querySelector('.conflict-details');
        
        conflictTitle.textContent = `Warning: ${data.conflicts[0].type === 'overallocation' ? 'Resource Overallocation' : 'Conflict Detected'}`;
        conflictDetails.textContent = data.conflicts[0].message;
        
        modal.style.display = 'flex';
    }
    
    // Assign resource function
    function assignResource(taskId, resourceId) {
        fetch('/api/assign-resource/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                task_id: taskId,
                resource_id: resourceId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateUI(data.assignment);
            }
        });
    }
    
    // Update UI after assignment
    function updateUI(assignment) {
        // Remove task from unassigned list
        const taskElement = document.querySelector(`.task-card[data-task-id="${assignment.task_id}"]`);
        if (taskElement) {
            taskElement.remove();
        }
        
        // Add assignment to resource
        const resourceDropZone = document.querySelector(`.resource-assignments[data-resource-id="${assignment.resource_id}"]`);
        const emptyMessage = resourceDropZone.querySelector('.empty-assignments');
        
        if (emptyMessage) {
            emptyMessage.remove();
            
            // Create assignment list if it doesn't exist
            if (!resourceDropZone.querySelector('.assignment-list')) {
                const assignmentList = document.createElement('div');
                assignmentList.className = 'assignment-list';
                resourceDropZone.appendChild(assignmentList);
            }
        }
        
        const assignmentList = resourceDropZone.querySelector('.assignment-list');
        
        // Create new assignment card
        const assignmentCard = document.createElement('div');
        assignmentCard.className = 'assignment-card';
        assignmentCard.dataset.assignmentId = assignment.id;
        
        assignmentCard.innerHTML = `
            <div class="assignment-info">
                <span class="assignment-title">${assignment.task_name}</span>
                <span class="assignment-project">${assignment.project_name}</span>
            </div>
            <div class="assignment-hours">${assignment.allocated_hours}h</div>
            <div class="assignment-remove">×</div>
        `;
        
        assignmentList.appendChild(assignmentCard);
        
        // Update resource utilization
        const utilizationText = document.querySelector(`.resource-card .resource-utilization .utilization-text`);
        const progressFill = document.querySelector(`.resource-card .progress-fill`);
        
        if (utilizationText && progressFill) {
            // Update utilization text
            utilizationText.textContent = `${assignment.utilization}% Utilized`;
            
            // Update progress bar width
            progressFill.style.width = `${Math.min(assignment.utilization, 100)}%`;
            
            // Update classes based on utilization
            if (assignment.utilization > 100) {
                utilizationText.className = 'utilization-text utilization-danger';
                progressFill.className = 'progress-fill progress-danger';
            } else if (assignment.utilization > 85) {
                utilizationText.className = 'utilization-text utilization-warning';
                progressFill.className = 'progress-fill progress-warning';
            } else {
                utilizationText.className = 'utilization-text utilization-normal';
                progressFill.className = 'progress-fill progress-normal';
            }
        }
        
        // Add event listener to remove button
        const removeButton = assignmentCard.querySelector('.assignment-remove');
        if (removeButton) {
            removeButton.addEventListener('click', function() {
                removeAssignment(assignment.id);
            });
        }
    }
    
    // Remove assignment function
    function removeAssignment(assignmentId) {
        fetch('/api/remove-assignment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                assignment_id: assignmentId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove assignment card
                const assignmentCard = document.querySelector(`.assignment-card[data-assignment-id="${assignmentId}"]`);
                if (assignmentCard) {
                    const assignmentList = assignmentCard.parentElement;
                    assignmentCard.remove();
                    
                    // If no more assignments, show empty message
                    if (assignmentList.children.length === 0) {
                        const resourceDropZone = assignmentList.parentElement;
                        assignmentList.remove();
                        
                        const emptyMessage = document.createElement('div');
                        emptyMessage.className = 'empty-assignments';
                        emptyMessage.textContent = 'Drop tasks here to assign';
                        resourceDropZone.appendChild(emptyMessage);
                    }
                }
            }
        });
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Modal close button
    if (modalClose) {
        modalClose.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    // Modal cancel button
    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    // Modal confirm button
    if (confirmButton) {
        confirmButton.addEventListener('click', () => {
            modal.style.display = 'none';
            if (currentTaskId && currentResourceId) {
                assignResource(currentTaskId, currentResourceId);
            }
        });
    }
});