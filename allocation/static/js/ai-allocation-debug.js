/**
 * AI-Enhanced Allocation Board JavaScript - Debug Version
 * Extends the basic drag-drop functionality with AI-powered suggestions
 */

console.log('AI-Allocation JavaScript loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing allocation-specific AI features...');
    initializeAllocationAIFeatures();
    initializeDragDrop();
});

function initializeAllocationAIFeatures() {
    console.log('Initializing allocation-specific AI features...');
    
    // Initialize NLI Search (needed for search bar functionality)
    if (typeof initializeNLISearch === 'function') {
        initializeNLISearch();
        console.log('NLI Search initialized for allocation page');
    } else {
        console.warn('initializeNLISearch function not available');
    }
    
    // AI Task Suggestions button (renamed from auto-assign)
    const aiSuggestionsBtn = document.getElementById('ai-task-suggestions');
    console.log('AI Task Suggestions button found:', !!aiSuggestionsBtn);
    if (aiSuggestionsBtn) {
        aiSuggestionsBtn.addEventListener('click', handleAITaskSuggestions);
        console.log('AI Task Suggestions click handler added');
    }

    // AI suggestion buttons on individual task cards
    const suggestBtns = document.querySelectorAll('.ai-suggest-btn');
    console.log('AI suggest buttons found:', suggestBtns.length);
    suggestBtns.forEach(btn => {
        btn.addEventListener('click', handleIndividualTaskSuggestions);
    });
    
    // Assignment remove buttons
    const removeBtns = document.querySelectorAll('.assignment-remove');
    console.log('Assignment remove buttons found:', removeBtns.length);
    removeBtns.forEach(btn => {
        btn.addEventListener('click', handleUnassignTask);
    });
    
    // Check CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    console.log('CSRF token found:', !!csrfToken);
}

function initializeDragDrop() {
    console.log('Initializing drag-drop...');
    
    // Existing drag-drop functionality
    const taskCards = document.querySelectorAll('.task-card');
    const resourceAssignments = document.querySelectorAll('.resource-assignments');
    
    console.log('Task cards found:', taskCards.length);
    console.log('Resource assignments found:', resourceAssignments.length);

    taskCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });

    resourceAssignments.forEach(area => {
        area.addEventListener('dragover', handleDragOver);
        area.addEventListener('drop', handleDrop);
        area.addEventListener('dragenter', handleDragEnter);
        area.addEventListener('dragleave', handleDragLeave);
    });
}

// AI Task Suggestions - Shows all recommendations with reasoning
async function handleAITaskSuggestions() {
    console.log('AI Task Suggestions clicked!');
    
    const suggestionsBtn = document.getElementById('ai-task-suggestions');
    const unassignedTasks = document.querySelectorAll('.task-card');
    
    console.log('Unassigned tasks found:', unassignedTasks.length);
    
    if (unassignedTasks.length === 0) {
        showNotification('No unassigned tasks found', 'info');
        return;
    }    // Show loading state
    suggestionsBtn.disabled = true;
    suggestionsBtn.innerHTML = '<span class="ai-icon">⚡</span><span class="ai-text">AI Analyzing...</span>';

    try {
        const taskIds = Array.from(unassignedTasks).map(task => 
            parseInt(task.dataset.taskId)
        );
        
        console.log('Getting AI suggestions for tasks:', taskIds);

        // Get suggestions for all tasks
        const allSuggestions = [];
        for (const taskId of taskIds) {
            const response = await fetch(`/allocation/api/ai-suggestions/${taskId}/`);
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                allSuggestions.push({
                    task: data.task,
                    suggestion: data.suggestions[0] // Best suggestion
                });
            }
        }

        if (allSuggestions.length > 0) {
            showAITaskSuggestionsModal(allSuggestions);
        } else {
            showNotification('No AI recommendations available for current tasks', 'warning');
        }

    } catch (error) {
        console.error('AI task suggestions error:', error);
        showNotification('Failed to get AI suggestions', 'error');
    } finally {        // Restore button
        suggestionsBtn.disabled = false;
        suggestionsBtn.innerHTML = '<span class="ai-icon">🤖</span><span class="ai-text">AI Task Suggestions</span><span class="ai-badge">SMART</span>';
    }
}

// Individual task-specific AI suggestions
async function handleIndividualTaskSuggestions(event) {
    console.log('Individual AI suggestions clicked for task');
    
    event.stopPropagation(); // Prevent card drag
    const taskId = event.target.closest('.ai-suggest-btn').dataset.taskId;
    const suggestionsPanel = document.querySelector(`.ai-suggestions[data-task-id="${taskId}"]`);
    const suggestionsContent = suggestionsPanel.querySelector('.suggestions-content');

    console.log('Task ID:', taskId);
    console.log('Suggestions panel found:', !!suggestionsPanel);

    // Toggle panel visibility
    if (suggestionsPanel.style.display !== 'none') {
        suggestionsPanel.style.display = 'none';
        return;
    }

    // Show loading state
    suggestionsPanel.style.display = 'block';
    suggestionsContent.innerHTML = '<div class="ai-loading">Loading AI recommendations...</div>';

    try {
        console.log('Fetching AI suggestions for task:', taskId);
        const response = await fetch(`/allocation/api/ai-suggestions/${taskId}/`);
        console.log('Suggestions API response status:', response.status);
        
        const data = await response.json();
        console.log('Suggestions API response data:', data);

        if (data.success && data.suggestions && data.suggestions.length > 0) {
            renderTaskSuggestions(suggestionsContent, data.suggestions, taskId);
            highlightRecommendedResources(data.suggestions);
        } else {
            suggestionsContent.innerHTML = `<div class="text-muted">No AI recommendations available</div>`;
        }

    } catch (error) {
        console.error('Error fetching AI suggestions:', error);
        suggestionsContent.innerHTML = `<div class="text-danger">Failed to load suggestions</div>`;
    }
}

// Unassign task functionality
async function handleUnassignTask(event) {
    console.log('Unassign task clicked');
    
    event.stopPropagation();
    
    // Ensure we get the button element, not the icon inside it
    const button = event.target.closest('.assignment-remove');
    if (!button) {
        console.error('Could not find assignment-remove button');
        return;
    }
    
    const assignmentId = button.dataset.assignmentId;
    const taskId = button.dataset.taskId;
    
    console.log('Unassigning assignment:', assignmentId, 'task:', taskId);

    // Validate we have the required IDs
    if (!assignmentId) {
        console.error('Assignment ID not found');
        showNotification('Error: Assignment ID not found', 'error');
        return;
    }

    // Get task details for better confirmation dialog
    const assignmentCard = button.closest('.assignment-card');
    const taskName = assignmentCard.querySelector('.assignment-title').textContent;
    const resourceCard = assignmentCard.closest('.resource-card');
    const resourceName = resourceCard.querySelector('.resource-name').textContent;

    // Show custom confirmation dialog
    const shouldProceed = await showUnassignConfirmationDialog(taskName, resourceName);
    if (!shouldProceed) {
        return;
    }

    try {
        const response = await fetch('/allocation/api/unassign-task/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                assignment_id: assignmentId
            })
        });

        console.log('Unassign response status:', response.status);
        const data = await response.json();
        console.log('Unassign response data:', data);

        if (data.success) {
            showNotification('Task unassigned successfully!', 'success');
            
            // Remove assignment card from UI
            const assignmentCard = event.target.closest('.assignment-card');
            assignmentCard.remove();
            
            // Update resource utilization
            updateResourceUtilization(data.resource_id, data.new_utilization);
            
            // Add task back to unassigned list
            addTaskToUnassignedList(data.task);
            
        } else {
            showNotification(data.error || 'Failed to unassign task', 'error');
        }

    } catch (error) {
        console.error('Error unassigning task:', error);
        showNotification('Failed to unassign task', 'error');
    }
}

function renderTaskSuggestions(container, suggestions, taskId) {
    console.log('Rendering suggestions:', suggestions.length);
    
    const html = suggestions.slice(0, 3).map(suggestion => {
        const matchClass = getMatchClass(suggestion.match_score);
        const matchPercentage = Math.round(suggestion.match_score * 100);
        
        return `
            <div class="suggestion-item">
                <div>
                    <div class="suggestion-resource">${suggestion.resource.name}</div>
                    <div class="suggestion-reasoning">${suggestion.reasoning}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span class="suggestion-match ${matchClass}">${matchPercentage}%</span>
                    <button class="suggestion-assign-btn" 
                            data-task-id="${taskId}" 
                            data-resource-id="${suggestion.resource.id}">
                        Assign
                    </button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;

    // Add click handlers for assign buttons
    container.querySelectorAll('.suggestion-assign-btn').forEach(btn => {
        btn.addEventListener('click', handleSuggestionAssign);
    });
}

function getMatchClass(score) {
    if (score >= 0.7) return 'match-high';
    if (score >= 0.5) return 'match-medium';
    return 'match-low';
}

function highlightRecommendedResources(suggestions) {
    console.log('Highlighting recommended resources');
    
    // Remove previous recommendations
    document.querySelectorAll('.resource-card').forEach(card => {
        card.classList.remove('ai-recommended');
    });

    // Highlight top recommendations
    suggestions.slice(0, 2).forEach(suggestion => {
        const resourceCard = document.querySelector(
            `.resource-card[data-resource-id="${suggestion.resource.id}"]`
        );
        if (resourceCard) {
            resourceCard.classList.add('ai-recommended');
            console.log('Highlighted resource:', suggestion.resource.name);
        }
    });
}

async function handleSuggestionAssign(event) {
    console.log('Suggestion assign clicked');
    
    // Ensure we get the button element that has the data attributes
    const button = event.target.closest('.suggestion-assign-btn');
    if (!button) {
        console.error('Could not find suggestion-assign-btn button');
        return;
    }
    
    const taskId = button.dataset.taskId;
    const resourceId = button.dataset.resourceId;
    
    console.log('Assigning task', taskId, 'to resource', resourceId);

    try {
        const response = await fetch('/allocation/api/assign-task/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                task_id: taskId,
                resource_id: resourceId
            })
        });

        console.log('Assignment response status:', response.status);
        const data = await response.json();
        console.log('Assignment response data:', data);

        if (data.success) {
            showNotification('Task assigned successfully!', 'success');
            // Refresh to show updated assignments
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Failed to assign task', 'error');
        }

    } catch (error) {
        console.error('Error assigning task:', error);
        showNotification('Failed to assign task', 'error');
    }
}

// Enhanced drag and drop with AI conflict checking
function handleDragStart(event) {
    console.log('Drag start');
    event.dataTransfer.setData('text/plain', event.target.dataset.taskId);
    event.target.classList.add('dragging');
}

function handleDragEnd(event) {
    console.log('Drag end');
    event.target.classList.remove('dragging');
    // Clear AI highlights
    document.querySelectorAll('.resource-card').forEach(card => {
        card.classList.remove('ai-recommended');
    });
}

function handleDragOver(event) {
    event.preventDefault();
}

function handleDragEnter(event) {
    event.preventDefault();
    event.target.closest('.resource-assignments').classList.add('drag-over');
}

function handleDragLeave(event) {
    if (!event.target.closest('.resource-assignments').contains(event.relatedTarget)) {
        event.target.closest('.resource-assignments').classList.remove('drag-over');
    }
}

async function handleDrop(event) {
    console.log('Drop event');
    event.preventDefault();
    
    const taskId = event.dataTransfer.getData('text/plain');
    const resourceId = event.target.closest('.resource-assignments').dataset.resourceId;
    
    console.log('Dropping task', taskId, 'on resource', resourceId);
    
    event.target.closest('.resource-assignments').classList.remove('drag-over');

    // Check for conflicts before assigning
    try {
        const conflictResponse = await fetch(
            `/allocation/api/check-conflicts/?task_id=${taskId}&resource_id=${resourceId}`
        );
        const conflictData = await conflictResponse.json();
        
        console.log('Conflict check:', conflictData);

        if (conflictData.has_conflicts) {
            const shouldProceed = await showConflictDialog(conflictData.conflicts);
            if (!shouldProceed) return;
        }

        // Proceed with assignment
        await assignTask(taskId, resourceId);

    } catch (error) {
        console.error('Error during drop:', error);
        showNotification('Failed to assign task', 'error');
    }
}

async function assignTask(taskId, resourceId) {
    console.log('Assigning task', taskId, 'to resource', resourceId);
    
    try {
        const response = await fetch('/allocation/api/assign-task/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                task_id: taskId,
                resource_id: resourceId
            })
        });

        const data = await response.json();
        console.log('Assignment result:', data);

        if (data.success) {
            showNotification('Task assigned successfully!', 'success');
            updateUIAfterAssignment(data.assignment, data.new_utilization);
        } else {
            showNotification(data.error || 'Failed to assign task', 'error');
        }

    } catch (error) {
        console.error('Error assigning task:', error);
        showNotification('Failed to assign task', 'error');
    }
}

function updateUIAfterAssignment(assignment, newUtilization) {
    console.log('Updating UI after assignment');
    
    // Remove task from unassigned list
    const taskCard = document.querySelector(`[data-task-id="${assignment.task_id}"]`);
    if (taskCard) {
        taskCard.remove();
    }

    // Update resource utilization
    updateResourceUtilization(assignment.resource_id, newUtilization);

    // Add assignment to resource
    addAssignmentToResource(assignment);
}

function updateResourceUtilization(resourceId, newUtilization) {
    const resourceCard = document.querySelector(`.resource-card[data-resource-id="${resourceId}"]`);
    if (!resourceCard) return;

    const utilizationText = resourceCard.querySelector('.utilization-text');
    const progressFill = resourceCard.querySelector('.progress-fill');

    // Update text and color classes
    utilizationText.textContent = `${newUtilization.toFixed(1)}% Utilized`;
    utilizationText.className = 'utilization-text ' + getUtilizationClass(newUtilization);
    
    progressFill.style.width = `${Math.min(newUtilization, 100)}%`;
    progressFill.className = 'progress-fill ' + getProgressClass(newUtilization);
}

function getUtilizationClass(utilization) {
    if (utilization > 100) return 'utilization-danger';
    if (utilization > 85) return 'utilization-warning';
    return 'utilization-normal';
}

function getProgressClass(utilization) {
    if (utilization > 100) return 'progress-danger';
    if (utilization > 85) return 'progress-warning';
    return 'progress-normal';
}

function addTaskToUnassignedList(task) {
    const taskList = document.querySelector('.task-list');
    if (!taskList) return;

    // Remove empty state if present
    const emptyState = taskList.querySelector('.empty-tasks');
    if (emptyState) {
        emptyState.remove();
    }

    // Create task card
    const taskCard = document.createElement('div');
    taskCard.className = 'task-card';
    taskCard.draggable = true;
    taskCard.dataset.taskId = task.id;
    taskCard.innerHTML = `
        <div class="task-header">
            <span class="task-title">${task.name}</span>
            <span class="task-hours">${task.estimated_hours}h</span>            <button class="ai-suggest-btn" data-task-id="${task.id}" title="Get AI recommendations for this task">
                🤖
            </button>
        </div>
        <div class="task-project">${task.project_name}</div>
        <div class="task-dates">
            <span>Start: ${task.start_date}</span>
            <span>Due: ${task.end_date}</span>
        </div>
        <div class="ai-suggestions" style="display: none;" data-task-id="${task.id}">            <div class="suggestions-header">
                🤖 AI Recommendations
            </div>
            <div class="suggestions-content">
                <!-- AI suggestions will be loaded here -->
            </div>
        </div>
    `;

    taskList.appendChild(taskCard);
    
    // Add event listeners
    const aiSuggestBtn = taskCard.querySelector('.ai-suggest-btn');
    aiSuggestBtn.addEventListener('click', handleIndividualTaskSuggestions);
      // Re-initialize drag-drop for the new task
    initializeTaskDragDrop(taskCard);
}

function initializeTaskDragDrop(taskCard) {
    taskCard.addEventListener('dragstart', handleDragStart);
    taskCard.addEventListener('dragend', handleDragEnd);
}

function addAssignmentToResource(assignment, resourceId = null) {
    const targetResourceId = resourceId || assignment.resource_id;
    const resourceAssignments = document.querySelector(
        `.resource-assignments[data-resource-id="${targetResourceId}"]`
    );
    if (!resourceAssignments) return;

    // Remove empty state if present
    const emptyState = resourceAssignments.querySelector('.empty-assignments');
    if (emptyState) {
        emptyState.remove();
    }

    // Add assignment list if not present
    let assignmentList = resourceAssignments.querySelector('.assignment-list');
    if (!assignmentList) {
        assignmentList = document.createElement('div');
        assignmentList.className = 'assignment-list';
        resourceAssignments.appendChild(assignmentList);
    }

    // Create assignment card
    const assignmentCard = document.createElement('div');
    assignmentCard.className = 'assignment-card';
    assignmentCard.dataset.assignmentId = assignment.id;
    assignmentCard.innerHTML = `
        <div class="assignment-info">
            <span class="assignment-title">${assignment.task_name}</span>
            <span class="assignment-project">${assignment.project_name || 'Project'}</span>
        </div>
        <div class="assignment-hours">${assignment.allocated_hours}h</div>
        <button class="assignment-remove" data-assignment-id="${assignment.id}" data-task-id="${assignment.task_id}" title="Remove assignment">
            <i class="fas fa-trash-alt"></i>
        </button>
    `;

    assignmentList.appendChild(assignmentCard);
    
    // Add event listener to the remove button
    const removeBtn = assignmentCard.querySelector('.assignment-remove');
    removeBtn.addEventListener('click', handleUnassignTask);
}

// Custom confirmation dialog for unassigning tasks
function showUnassignConfirmationDialog(taskName, resourceName) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">
                        <i class="fas fa-exclamation-triangle" style="color: #f39c12;"></i> 
                        Confirm Task Removal
                    </h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove(); window.unassignDialogResolve(false);">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-warning" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 12px; margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: #856404;">Remove Task Assignment</h4>
                        <p style="margin: 0; color: #856404;">
                            You are about to remove "<strong>${taskName}</strong>" from "<strong>${resourceName}</strong>".
                        </p>
                    </div>
                    <p>This will:</p>
                    <ul>
                        <li>Remove the task from ${resourceName}'s workload</li>
                        <li>Move the task back to the unassigned tasks list</li>
                        <li>Update ${resourceName}'s utilization percentage</li>
                    </ul>
                    <p><strong>Are you sure you want to proceed?</strong></p>
                    <div class="modal-actions" style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px;">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove(); window.unassignDialogResolve(false);">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                        <button class="btn btn-danger" onclick="this.closest('.modal-overlay').remove(); window.unassignDialogResolve(true);">
                            <i class="fas fa-trash-alt"></i> Remove Assignment
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Store resolve function globally so buttons can access it
        window.unassignDialogResolve = resolve;
    });
}

// UI Helper functions
function showAIAssignmentResults(data) {
    console.log('Showing AI assignment results');
    
    const modal = document.createElement('div');
    modal.className = 'ai-results-modal';
    modal.innerHTML = `
        <div class="ai-results-content">
            <div class="ai-results-header">
                <i class="fas fa-robot"></i>
                AI Auto-Assignment Results
            </div>
            <div class="mb-3">
                <strong>${data.total_assigned}</strong> tasks assigned successfully
            </div>
            <div class="assignment-results">
                ${data.assignments_made.map(assignment => `
                    <div class="ai-assignment-result">
                        <div>
                            <div class="assignment-task-name">${assignment.task_name}</div>
                            <div class="assignment-resource-name">→ ${assignment.resource_name}</div>
                        </div>
                        <span class="assignment-match-score">${Math.round(assignment.match_score * 100)}%</span>
                    </div>
                `).join('')}
            </div>
            ${data.errors.length > 0 ? `
                <div class="mt-3">
                    <strong>Warnings:</strong>
                    <ul>
                        ${data.errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            <div class="mt-3 text-center">
                <button class="btn btn-primary" onclick="this.closest('.ai-results-modal').remove()">
                    Close
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (modal.parentNode) {
            modal.remove();
        }
    }, 10000);
}

function showConflictDialog(conflicts) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">Assignment Conflicts Detected</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove(); window.conflictDialogResolve(false);">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="conflict-warning">
                        <h4 class="conflict-title">The following issues were detected:</h4>
                        <ul>
                            ${conflicts.map(conflict => `
                                <li class="conflict-${conflict.severity}">${conflict.message}</li>
                            `).join('')}
                        </ul>
                    </div>
                    <p>Would you like to assign this task anyway?</p>
                    <div class="modal-actions">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove(); window.conflictDialogResolve(false);">Cancel</button>
                        <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove(); window.conflictDialogResolve(true);">Assign Anyway</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Store resolve function globally so buttons can access it
        window.conflictDialogResolve = resolve;
    });
}

async function assignTaskToResource(taskId, resourceId, hours) {
    console.log('Assigning task', taskId, 'to resource', resourceId);
    
    try {
        const response = await fetch('/allocation/api/assign-task/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                task_id: taskId,
                resource_id: resourceId
            })
        });

        const data = await response.json();
        console.log('Assignment response:', data);

        if (data.success) {
            // Remove task from unassigned list
            const taskCard = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.remove();
            }
            
            // Add to resource assignments
            addAssignmentToResource(data.assignment, resourceId);
              // Update resource utilization
            if (data.new_utilization !== undefined) {
                updateResourceUtilization(resourceId, data.new_utilization);
            }
            
            return true;
        } else {
            showNotification(data.error || 'Failed to assign task', 'error');
            return false;
        }
        
    } catch (error) {
        console.error('Error assigning task:', error);
        showNotification('Failed to assign task', 'error');
        return false;
    }
}

// Custom confirmation dialog for unassigning tasks
function showUnassignConfirmationDialog(taskName, resourceName) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">
                        <i class="fas fa-exclamation-triangle" style="color: #f39c12;"></i> 
                        Confirm Task Removal
                    </h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove(); window.unassignDialogResolve(false);">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-warning" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 12px; margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: #856404;">Remove Task Assignment</h4>
                        <p style="margin: 0; color: #856404;">
                            You are about to remove "<strong>${taskName}</strong>" from "<strong>${resourceName}</strong>".
                        </p>
                    </div>
                    <p>This will:</p>
                    <ul>
                        <li>Remove the task from ${resourceName}'s workload</li>
                        <li>Move the task back to the unassigned tasks list</li>
                        <li>Update ${resourceName}'s utilization percentage</li>
                    </ul>
                    <p><strong>Are you sure you want to proceed?</strong></p>
                    <div class="modal-actions" style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px;">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove(); window.unassignDialogResolve(false);">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                        <button class="btn btn-danger" onclick="this.closest('.modal-overlay').remove(); window.unassignDialogResolve(true);">
                            <i class="fas fa-trash-alt"></i> Remove Assignment
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Store resolve function globally so buttons can access it
        window.unassignDialogResolve = resolve;
    });
}

function showAITaskSuggestionsModal(suggestions) {
    console.log('Showing AI Task Suggestions modal with', suggestions.length, 'suggestions');
    
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.display = 'block';
    
    const modalContent = `
        <div class="modal ai-suggestions-modal">
            <div class="modal-header">
                <h3 class="modal-title">
                    <i class="fas fa-robot"></i> AI Task Recommendations
                </h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">                <div class="ai-modal-intro">
                    <p>AI has analyzed ${suggestions.length} task${suggestions.length === 1 ? '' : 's'} and found the following optimal assignment${suggestions.length === 1 ? '' : 's'}:</p>
                </div>
                <div class="ai-suggestions-list">
                    ${suggestions.map(item => `
                        <div class="ai-suggestion-item">
                            <div class="suggestion-task">
                                <h4>${item.task.name}</h4>
                                <div class="task-meta">
                                    <span class="task-project">${item.task.project}</span>
                                    <span class="task-hours">${item.task.estimated_hours}h</span>
                                </div>
                            </div>
                            <div class="suggestion-arrow">→</div>
                            <div class="suggestion-resource">
                                <div class="resource-name">${item.suggestion.resource.name}</div>
                                <div class="resource-role">${item.suggestion.resource.role}</div>
                                <div class="match-score">
                                    <span class="score-value">${Math.round(item.suggestion.match_score * 100)}% match</span>
                                </div>
                            </div>
                            <div class="suggestion-reasoning">
                                <strong>Why this match:</strong> ${item.suggestion.reasoning}
                            </div>
                            <div class="suggestion-actions">
                                <button class="btn btn-primary assign-suggestion-btn" 
                                        data-task-id="${item.task.id}" 
                                        data-resource-id="${item.suggestion.resource.id}"
                                        data-hours="${item.task.estimated_hours}">
                                    <i class="fas fa-check"></i> Assign
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>                <div class="modal-actions">
                    <button class="btn btn-secondary modal-cancel">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                    <button class="btn btn-ai-primary assign-all-suggestions">
                        <i class="fas fa-magic"></i> ${suggestions.length === 1 ? 'Assign the Recommendation' : 'Assign All Recommendations'}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
    
    // Event handlers
    modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    modal.querySelector('.modal-cancel').addEventListener('click', () => modal.remove());
    
    // Individual assign buttons
    modal.querySelectorAll('.assign-suggestion-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const taskId = e.target.dataset.taskId;
            const resourceId = e.target.dataset.resourceId;
            const hours = e.target.dataset.hours;
            
            try {
                const success = await assignTaskToResource(taskId, resourceId, hours);
                if (success) {
                    e.target.closest('.ai-suggestion-item').style.opacity = '0.5';
                    e.target.disabled = true;
                    e.target.innerHTML = '<i class="fas fa-check"></i> Assigned';
                    showNotification('Task assigned successfully!', 'success');
                }
            } catch (error) {
                showNotification('Failed to assign task', 'error');
            }
        });
    });
    
    // Assign all button
    modal.querySelector('.assign-all-suggestions').addEventListener('click', async () => {
        const buttons = modal.querySelectorAll('.assign-suggestion-btn:not(:disabled)');
        let successCount = 0;
        
        for (const btn of buttons) {
            try {
                const success = await assignTaskToResource(
                    btn.dataset.taskId, 
                    btn.dataset.resourceId, 
                    btn.dataset.hours
                );
                if (success) {
                    successCount++;
                    btn.disabled = true;
                    btn.innerHTML = '<i class="fas fa-check"></i> Assigned';
                }
            } catch (error) {
                console.error('Failed to assign task:', error);
            }
        }
        
        showNotification(`Successfully assigned ${successCount} of ${buttons.length} tasks`, 'success');
        setTimeout(() => modal.remove(), 2000);
    });
}

function showNotification(message, type = 'info') {
    console.log('Showing notification:', message, type);
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            ${message}
        </div>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 12px 16px;
        border-radius: 6px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        min-width: 250px;
        transition: all 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function getNotificationColor(type) {
    switch (type) {
        case 'success': return '#28a745';
        case 'error': return '#dc3545';
        case 'warning': return '#ffc107';
        default: return '#007bff';
    }
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

console.log('AI-Allocation JavaScript loaded successfully');
