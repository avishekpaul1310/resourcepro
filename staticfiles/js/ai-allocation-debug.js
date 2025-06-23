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
    }    // Enhanced AI Task Suggestions button (now the main AI button)
    const aiSuggestionsBtn = document.getElementById('ai-task-suggestions');
    console.log('AI Task Suggestions button found:', !!aiSuggestionsBtn);
    if (aiSuggestionsBtn) {
        aiSuggestionsBtn.addEventListener('click', handleEnhancedAISuggestions);
        console.log('Enhanced AI click handler added to main button');
    }
    
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

// Enhanced AI Task Suggestions - Next-generation AI with priority-driven and future-aware scheduling
async function handleEnhancedAISuggestions() {
    console.log('Enhanced AI Suggestions clicked!');
    
    const enhancedBtn = document.getElementById('ai-task-suggestions');
    const unassignedTasks = document.querySelectorAll('.task-card');
    
    console.log('Unassigned tasks found for enhanced AI:', unassignedTasks.length);
    
    if (unassignedTasks.length === 0) {
        showNotification('No unassigned tasks found', 'info');
        return;
    }    // Show loading state
    enhancedBtn.disabled = true;
    enhancedBtn.innerHTML = '<span class="ai-icon">🧠</span><span class="ai-text">AI Analyzing...</span><span class="ai-badge">ENHANCED</span>';

    try {
        const taskIds = Array.from(unassignedTasks).map(task => 
            parseInt(task.dataset.taskId)
        );
        
        console.log('Getting enhanced AI suggestions for tasks:', taskIds);        // Call the enhanced AI API
        const response = await fetch(`/allocation/api/enhanced-ai-suggestions/?task_ids=${taskIds.join(',')}`);
        const data = await response.json();
        
        console.log('Enhanced AI API Response:', data);
        
        if (data.success) {
            showEnhancedAISuggestionsModal(data.results);
        } else {
            showNotification(data.error || 'Failed to get enhanced AI suggestions', 'error');
        }

    } catch (error) {
        console.error('Enhanced AI suggestions error:', error);
        showNotification('Failed to get enhanced AI suggestions', 'error');
    } finally {
        // Restore button
        enhancedBtn.disabled = false;
        enhancedBtn.innerHTML = '<span class="ai-icon">🧠</span><span class="ai-text">AI Task Suggestions</span><span class="ai-badge">ENHANCED</span>';
    }
}

// Show enhanced AI suggestions modal
function showEnhancedAISuggestionsModal(results) {
    console.log('Showing enhanced AI suggestions modal:', results);
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal enhanced-ai-modal">
            <div class="modal-header">
                <h3>🧠 Enhanced AI Task Recommendations</h3>
                <span class="modal-close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="enhanced-ai-summary">
                    <p><strong>Analysis Complete:</strong> ${results.total_tasks_analyzed} tasks analyzed, 
                    ${results.tasks_with_suggestions} recommendations generated</p>
                </div>
                <div class="enhanced-suggestions-container">
                    ${generateEnhancedSuggestionsHTML(results.suggestions)}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                <button class="btn btn-ai-primary" onclick="applyEnhancedSuggestions()">Apply Selected</button>
            </div>
        </div>
    `;
    
    // Add close functionality
    modal.querySelector('.modal-close').onclick = () => modal.remove();
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    
    document.body.appendChild(modal);
}

// Generate enhanced suggestions HTML
function generateEnhancedSuggestionsHTML(suggestions) {
    let html = '';
    
    for (const [taskId, suggestionData] of Object.entries(suggestions)) {
        const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
        const taskName = taskElement ? taskElement.querySelector('.task-title').textContent : `Task ${taskId}`;
        
        html += `
            <div class="enhanced-suggestion-item" data-task-id="${taskId}">
                <div class="suggestion-header">
                    <h4>${taskName}</h4>
                    <span class="suggestion-type ${suggestionData.type}">${suggestionData.type.replace('_', ' ').toUpperCase()}</span>
                </div>
                <div class="suggestion-reasoning">
                    <p><em>${suggestionData.reasoning}</em></p>
                </div>
                <div class="suggestion-options">
                    ${generateSuggestionOptionsHTML(suggestionData.suggestions, suggestionData.type)}
                </div>
            </div>
        `;
    }
    
    return html || '<p>No enhanced suggestions available at this time.</p>';
}

// Generate suggestion options HTML based on type
function generateSuggestionOptionsHTML(suggestions, type) {
    let html = '';
    
    suggestions.forEach((suggestion, index) => {
        html += `<div class="suggestion-option" data-suggestion-index="${index}">`;
        
        switch (type) {
            case 'ideal':
                html += `
                    <div class="option-content">
                        <input type="checkbox" class="suggestion-checkbox" id="sugg-${suggestion.resource_id}-${index}">
                        <label for="sugg-${suggestion.resource_id}-${index}">
                            <strong>${suggestion.resource_name}</strong>
                            <div class="option-details">
                                <span>Skill Match: ${(suggestion.skill_match * 100).toFixed(0)}%</span>
                                <span>Utilization: ${suggestion.current_utilization}% → ${suggestion.projected_utilization}%</span>
                                <span class="confidence high">High Confidence</span>
                            </div>
                        </label>
                    </div>
                `;
                break;
                
            case 'future_scheduled':
                html += `
                    <div class="option-content">
                        <input type="checkbox" class="suggestion-checkbox" id="sugg-${suggestion.resource_id}-${index}">
                        <label for="sugg-${suggestion.resource_id}-${index}">
                            <strong>${suggestion.resource_name}</strong>
                            <div class="option-details">
                                <span>Skill Match: ${(suggestion.skill_match * 100).toFixed(0)}%</span>
                                <span>Delay: ${suggestion.delay_days} days</span>
                                <span>New Start: ${suggestion.suggested_start_date}</span>
                                <span class="confidence medium">Medium Confidence</span>
                            </div>
                        </label>
                    </div>
                `;
                break;
                
            case 'collaborative':
                if (suggestion.collaborators) {
                    html += `
                        <div class="option-content">
                            <input type="checkbox" class="suggestion-checkbox" id="sugg-collab-${index}">
                            <label for="sugg-collab-${index}">
                                <strong>Collaborative Assignment</strong>
                                <div class="option-details">
                                    ${suggestion.collaborators.map(c => 
                                        `<span>${c.resource_name}: ${c.available_hours}h</span>`
                                    ).join('')}
                                    <span>Coverage: ${suggestion.coverage_percentage.toFixed(0)}%</span>
                                </div>
                            </label>
                        </div>
                    `;
                } else {
                    html += `
                        <div class="option-content">
                            <span><strong>Task Splitting Recommended</strong></span>
                            <div class="option-details">
                                <span>Duration: ${suggestion.total_duration_weeks} weeks</span>
                                <span>Phases: ${suggestion.phases ? suggestion.phases.length : 'Multiple'}</span>
                            </div>
                        </div>
                    `;
                }
                break;
                
            case 'good_fit':
                html += `
                    <div class="option-content">
                        <input type="checkbox" class="suggestion-checkbox" id="sugg-${suggestion.resource_id}-${index}">
                        <label for="sugg-${suggestion.resource_id}-${index}">
                            <strong>${suggestion.resource_name}</strong>
                            <div class="option-details">
                                <span>Skill Match: ${(suggestion.skill_match * 100).toFixed(0)}%</span>
                                <span>Gaps: ${suggestion.skill_gap ? suggestion.skill_gap.join(', ') : 'None'}</span>
                                <span class="mentoring">Mentoring: ${suggestion.mentoring_needed ? 'Required' : 'Not needed'}</span>
                                <span class="confidence medium">Medium Confidence</span>
                            </div>
                        </label>
                    </div>
                `;
                break;
                
            case 'overallocation':
                html += `
                    <div class="option-content warning">
                        <input type="checkbox" class="suggestion-checkbox" id="sugg-${suggestion.resource_id}-${index}">
                        <label for="sugg-${suggestion.resource_id}-${index}">
                            <strong>${suggestion.resource_name}</strong>
                            <div class="option-details">
                                <span>Skill Match: ${(suggestion.skill_match * 100).toFixed(0)}%</span>
                                <span class="warning">⚠️ Over-allocation: +${suggestion.overallocation_percentage.toFixed(1)}%</span>
                                <span>Risk: ${suggestion.risk_analysis.delay_risk}</span>
                                <div class="mitigation-options">
                                    <strong>Mitigation:</strong>
                                    ${suggestion.mitigation_options.slice(0, 2).map(opt => 
                                        `<span>${opt.description}</span>`
                                    ).join('')}
                                </div>
                            </div>
                        </label>
                    </div>
                `;
                break;
        }
        
        html += '</div>';
    });
    
    return html;
}

// Apply selected enhanced suggestions
async function applyEnhancedSuggestions() {
    const selectedCheckboxes = document.querySelectorAll('.suggestion-checkbox:checked');
    console.log('Applying enhanced suggestions:', selectedCheckboxes.length);
    
    if (selectedCheckboxes.length === 0) {
        showNotification('Please select at least one suggestion to apply', 'warning');
        return;
    }
    
    // Extract assignment data from selected checkboxes
    const assignments = [];
    selectedCheckboxes.forEach(checkbox => {
        const suggestionOption = checkbox.closest('.suggestion-option');
        const enhancedItem = checkbox.closest('.enhanced-suggestion-item');
        const taskId = enhancedItem.dataset.taskId;
        
        // Extract resource ID from checkbox ID (format: sugg-{resource_id}-{index})
        const checkboxId = checkbox.id;
        const resourceIdMatch = checkboxId.match(/sugg-(\d+)-\d+/);
        
        if (resourceIdMatch) {
            const resourceId = resourceIdMatch[1];
            const resourceName = checkbox.parentElement.querySelector('strong').textContent;
            
            assignments.push({
                task_id: parseInt(taskId),
                resource_id: parseInt(resourceId),
                resource_name: resourceName
            });
        }
    });
    
    console.log('Assignments to apply:', assignments);
    
    if (assignments.length === 0) {
        showNotification('No valid assignments found', 'error');
        return;
    }
    
    // Apply assignments one by one
    let successCount = 0;
    let errorCount = 0;
    
    for (const assignment of assignments) {
        try {
            const response = await fetch('/allocation/api/assign-task/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({
                    task_id: assignment.task_id,
                    resource_id: assignment.resource_id
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                successCount++;
                console.log(`Successfully assigned task ${assignment.task_id} to resource ${assignment.resource_id}`);
                
                // Remove task from unassigned list
                const taskCard = document.querySelector(`.task-list .task-card[data-task-id="${assignment.task_id}"]`);
                if (taskCard) {
                    taskCard.remove();
                }
                
                // Update resource utilization if provided
                if (data.new_utilization !== undefined) {
                    updateResourceUtilization(assignment.resource_id, data.new_utilization);
                }
                
                // Add assignment to resource if assignment data is provided
                if (data.assignment) {
                    addAssignmentToResource(data.assignment, assignment.resource_id);
                }
            } else {
                errorCount++;
                console.error(`Failed to assign task ${assignment.task_id}:`, data.error);
            }
        } catch (error) {
            errorCount++;
            console.error(`Error assigning task ${assignment.task_id}:`, error);
        }
    }
    
    // Show results notification
    if (successCount > 0 && errorCount === 0) {
        showNotification(`Successfully assigned ${successCount} task${successCount === 1 ? '' : 's'}!`, 'success');
    } else if (successCount > 0 && errorCount > 0) {
        showNotification(`Assigned ${successCount} task${successCount === 1 ? '' : 's'}, ${errorCount} failed`, 'warning');
    } else {
        showNotification('Failed to assign any tasks', 'error');
    }
    
    // Close modal
    document.querySelector('.enhanced-ai-modal').closest('.modal-overlay').remove();
    
    // Refresh page if all assignments succeeded to ensure UI is in sync
    if (successCount > 0 && errorCount === 0) {
        setTimeout(() => {
            location.reload();
        }, 1500);
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
        console.log('Assignment response data:', data);        if (data.success) {
            showNotification('Task assigned successfully!', 'success');
            
            // Update UI immediately instead of page refresh
            console.log('Updating UI after assignment:', data);
              // Remove task from unassigned list
            const taskCard = document.querySelector(`.task-list .task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.remove();
                console.log('Removed task card from unassigned list');
                
                // Close any open AI suggestion panels for this task
                const suggestionPanel = document.querySelector(`.ai-suggestions[data-task-id="${taskId}"]`);
                if (suggestionPanel) {
                    suggestionPanel.style.display = 'none';
                }
            } else {
                console.warn('Task card not found for removal:', taskId);
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
    console.log('Drag start');
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
            <span class="task-hours">${task.estimated_hours}h</span>
        </div>
        <div class="task-project">${task.project_name}</div>
        <div class="task-dates">
            <span>Start: ${task.start_date}</span>
            <span>Due: ${task.end_date}</span>
        </div>
    `;

    taskList.appendChild(taskCard);
    
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
        console.log('Assignment response:', data);        if (data.success) {
            // Remove task from unassigned list
            const taskCard = document.querySelector(`.task-list .task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.remove();
            }
            
            // Add to resource assignments
            location.reload(); // Refresh to show new assignment
        } else {
            showNotification(data.error || 'Failed to assign task', 'error');
        }    } catch (error) {
        console.error('Assignment error:', error);
        showNotification('Failed to assign task', 'error');
    }
}

// Utility function to get CSRF token
function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    console.log(`Notification (${type}):`, message);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
    
    // Close button handler
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
}
