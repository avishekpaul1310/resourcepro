/**
 * AI-Enhanced Allocation Board JavaScript
 * Extends the basic drag-drop functionality with AI-powered suggestions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeAIFeatures();
    initializeDragDrop();
});

function initializeAIFeatures() {
    // AI Auto-Assign button
    const autoAssignBtn = document.getElementById('ai-auto-assign');
    if (autoAssignBtn) {
        autoAssignBtn.addEventListener('click', handleAIAutoAssign);
    }

    // AI suggestion buttons on task cards
    document.querySelectorAll('.ai-suggest-btn').forEach(btn => {
        btn.addEventListener('click', handleTaskAISuggestions);
    });
}

function initializeDragDrop() {
    // Existing drag-drop functionality
    const taskCards = document.querySelectorAll('.task-card');
    const resourceAssignments = document.querySelectorAll('.resource-assignments');

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

// AI Auto-Assign Functionality
async function handleAIAutoAssign() {
    const autoAssignBtn = document.getElementById('ai-auto-assign');
    const unassignedTasks = document.querySelectorAll('.task-card');
    
    if (unassignedTasks.length === 0) {
        showNotification('No unassigned tasks found', 'info');
        return;
    }

    // Disable button and show loading
    autoAssignBtn.disabled = true;
    autoAssignBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI Processing...';

    try {
        const taskIds = Array.from(unassignedTasks).map(task => 
            parseInt(task.dataset.taskId)
        );

        const response = await fetch('/allocation/api/ai-auto-assign/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ task_ids: taskIds })
        });

        const data = await response.json();

        if (data.success) {
            showAIAssignmentResults(data);
            // Refresh the page to show updated assignments
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } else {
            showNotification(data.error || 'Failed to auto-assign tasks', 'error');
        }

    } catch (error) {
        console.error('AI auto-assign error:', error);
        showNotification('Failed to connect to AI service', 'error');
    } finally {
        // Restore button
        autoAssignBtn.disabled = false;
        autoAssignBtn.innerHTML = '<i class="fas fa-robot"></i> AI Auto-Assign';
    }
}

// Task-specific AI suggestions
async function handleTaskAISuggestions(event) {
    event.stopPropagation(); // Prevent card drag
    const taskId = event.target.closest('.ai-suggest-btn').dataset.taskId;
    const suggestionsPanel = document.querySelector(`.ai-suggestions[data-task-id="${taskId}"]`);
    const suggestionsContent = suggestionsPanel.querySelector('.suggestions-content');

    // Toggle panel visibility
    if (suggestionsPanel.style.display !== 'none') {
        suggestionsPanel.style.display = 'none';
        // Clear AI highlights when closing
        document.querySelectorAll('.resource-card').forEach(card => {
            card.classList.remove('ai-recommended');
        });
        return;
    }

    // Close any other open suggestion panels
    document.querySelectorAll('.ai-suggestions').forEach(panel => {
        if (panel !== suggestionsPanel) {
            panel.style.display = 'none';
        }
    });
    
    // Clear previous AI highlights
    document.querySelectorAll('.resource-card').forEach(card => {
        card.classList.remove('ai-recommended');
    });

    // Show loading state
    suggestionsPanel.style.display = 'block';
    suggestionsContent.innerHTML = '<div class="ai-loading">Loading AI recommendations...</div>';

    try {
        const response = await fetch(`/allocation/api/ai-suggestions/${taskId}/`);
        const data = await response.json();

        if (data.success && data.suggestions && data.suggestions.length > 0) {
            renderTaskSuggestions(suggestionsContent, data.suggestions, taskId);
            highlightRecommendedResources(data.suggestions);
        } else {
            suggestionsContent.innerHTML = `
                <div class="suggestions-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; color: #718096;">No recommendations available</span>
                    <button class="suggestions-close-btn" data-task-id="${taskId}" style="background: none; border: none; color: #718096; cursor: pointer; padding: 2px; font-size: 14px;" title="Close recommendations">
                        ✕
                    </button>
                </div>
                <div class="text-muted">No AI recommendations available</div>
            `;
            
            // Add close button handler for no suggestions case
            const closeBtn = suggestionsContent.querySelector('.suggestions-close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', (event) => {
                    event.stopPropagation();
                    suggestionsPanel.style.display = 'none';
                });
            }
        }

    } catch (error) {
        console.error('Error fetching AI suggestions:', error);
        suggestionsContent.innerHTML = `
            <div class="suggestions-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 11px; color: #e53e3e;">Failed to load suggestions</span>
                <button class="suggestions-close-btn" data-task-id="${taskId}" style="background: none; border: none; color: #718096; cursor: pointer; padding: 2px; font-size: 14px;" title="Close recommendations">
                    ✕
                </button>
            </div>
            <div class="text-danger">Failed to load suggestions</div>
        `;
        
        // Add close button handler for error case
        const closeBtn = suggestionsContent.querySelector('.suggestions-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', (event) => {
                event.stopPropagation();
                suggestionsPanel.style.display = 'none';
            });
        }
    }
}

function renderTaskSuggestions(container, suggestions, taskId) {
    const suggestionItemsHtml = suggestions.slice(0, 3).map(suggestion => {
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

    const html = `
        <div class="suggestions-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 11px; color: #718096;">Choose a recommendation or manually assign</span>
            <button class="suggestions-close-btn" data-task-id="${taskId}" style="background: none; border: none; color: #718096; cursor: pointer; padding: 2px; font-size: 14px;" title="Close recommendations">
                ✕
            </button>
        </div>
        ${suggestionItemsHtml}
    `;

    container.innerHTML = html;

    // Add click handlers for assign buttons
    container.querySelectorAll('.suggestion-assign-btn').forEach(btn => {
        btn.addEventListener('click', handleSuggestionAssign);
    });

    // Add click handler for close button
    const closeBtn = container.querySelector('.suggestions-close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            const taskId = closeBtn.dataset.taskId;
            const suggestionsPanel = document.querySelector(`.ai-suggestions[data-task-id="${taskId}"]`);
            if (suggestionsPanel) {
                suggestionsPanel.style.display = 'none';
                // Clear AI highlights when closing
                document.querySelectorAll('.resource-card').forEach(card => {
                    card.classList.remove('ai-recommended');
                });
            }
        });
    }
}

function getMatchClass(score) {
    if (score >= 0.7) return 'match-high';
    if (score >= 0.5) return 'match-medium';
    return 'match-low';
}

function highlightRecommendedResources(suggestions) {
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
        }
    });
}

async function handleSuggestionAssign(event) {
    const taskId = event.target.dataset.taskId;
    const resourceId = event.target.dataset.resourceId;

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

        const data = await response.json();        if (data.success) {
            showNotification('Task assigned successfully!', 'success');
              // Update UI immediately instead of page refresh
            // Remove task from unassigned list
            const taskCard = document.querySelector(`.task-list .task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.remove();
                
                // Close any open AI suggestion panels for this task
                const suggestionPanel = document.querySelector(`.ai-suggestions[data-task-id="${taskId}"]`);
                if (suggestionPanel) {
                    suggestionPanel.style.display = 'none';
                }
            }
            
            // Update resource utilization if provided
            if (data.new_utilization !== undefined) {
                updateResourceUtilization(resourceId, data.new_utilization);
            }
            
            // Add assignment to resource if assignment data is provided
            if (data.assignment) {
                addAssignmentToResource(data.assignment, resourceId);
            }
            
            // Clear AI highlights
            document.querySelectorAll('.resource-card').forEach(card => {
                card.classList.remove('ai-recommended');
            });
            
            // Check if there are no more unassigned tasks
            const remainingTasks = document.querySelectorAll('.task-card');
            if (remainingTasks.length === 0) {
                const taskList = document.querySelector('.task-list');
                if (taskList) {
                    taskList.innerHTML = '<div class="empty-tasks">All tasks have been assigned!</div>';
                }
            }
            
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
    event.dataTransfer.setData('text/plain', event.target.dataset.taskId);
    event.target.classList.add('dragging');
    
    // Close any open AI suggestion panels when dragging starts
    document.querySelectorAll('.ai-suggestions').forEach(panel => {
        if (panel.style.display !== 'none') {
            panel.style.display = 'none';
        }
    });
    
    // Clear any AI highlights
    document.querySelectorAll('.resource-card').forEach(card => {
        card.classList.remove('ai-recommended');
    });
}

function handleDragEnd(event) {
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
    event.preventDefault();
    
    const taskId = event.dataTransfer.getData('text/plain');
    const resourceId = event.target.closest('.resource-assignments').dataset.resourceId;
    
    event.target.closest('.resource-assignments').classList.remove('drag-over');

    // Check for conflicts before assigning
    try {
        const conflictResponse = await fetch(
            `/allocation/api/check-conflicts/?task_id=${taskId}&resource_id=${resourceId}`
        );
        const conflictData = await conflictResponse.json();

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
    // Remove task from unassigned list
    const taskCard = document.querySelector(`.task-list .task-card[data-task-id="${assignment.task_id}"]`);
    if (taskCard) {
        taskCard.remove();
    }

    // Update resource utilization
    updateResourceUtilization(assignment.resource_id, newUtilization);

    // Add assignment to resource
    addAssignmentToResource(assignment);
}

function updateResourceUtilization(resourceId, newUtilization) {
    const resourceCard = document.querySelector(`.resource-card [data-resource-id="${resourceId}"]`);
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

function addAssignmentToResource(assignment) {
    const resourceAssignments = document.querySelector(
        `.resource-assignments[data-resource-id="${assignment.resource_id}"]`
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
        <div class="assignment-remove">×</div>
    `;

    assignmentList.appendChild(assignmentCard);
}

// UI Helper functions
function showAIAssignmentResults(data) {
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

    // Auto-remove after 5 seconds
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

function showNotification(message, type = 'info') {
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
        case 'success': return '#48bb78';
        case 'error': return '#e53e3e';
        case 'warning': return '#ed8936';
        default: return '#4299e1';
    }
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
