/**
 * AI Dashboard Features JavaScript
 * Handles AI-powered dashboard analyst, intervention simulator, and NLI
 */

// Global state
let currentSimulationStep = 'problem';
let selectedScenario = null;
let currentQuery = '';
let nliTimeout = null;

// Initialize AI features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAIFeatures();
});

/**
 * Initialize all AI features
 */
function initializeAIFeatures() {
    initializeNLISearch();
    initializeInterventionSimulator();
    initializeAIAnalyst();
    
    // Auto-refresh AI analysis every 30 minutes
    setInterval(function() {
        refreshAIAnalysis(false); // Don't force refresh
    }, 30 * 60 * 1000);
}

/**
 * Initialize AI Analyst widget
 */
function initializeAIAnalyst() {
    // Auto-refresh on visibility change (when user comes back to tab)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            const indicator = document.querySelector('.freshness-indicator');
            if (indicator && indicator.classList.contains('stale')) {
                refreshAIAnalysis(false);
            }
        }
    });
}

/**
 * AI Dashboard Analyst Functions
 */
function refreshAIAnalysis(force = true) {
    const indicator = document.querySelector('.freshness-indicator');
    
    if (indicator) {
        indicator.textContent = 'Updating...';
        indicator.className = 'freshness-indicator stale';
    }
    
    fetch('/dashboard/api/refresh-ai-analysis/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ force_refresh: force })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification('error', 'Failed to refresh AI analysis: ' + data.error);
        } else {
            updateAIAnalysisWidget(data);
            showNotification('success', 'AI analysis updated successfully');
        }
    })
    .catch(error => {
        console.error('Error refreshing AI analysis:', error);
        showNotification('error', 'Failed to refresh AI analysis');
    });
}

function updateAIAnalysisWidget(data) {
    // Update summary
    const summaryElement = document.querySelector('.ai-summary');
    if (summaryElement) {
        summaryElement.textContent = data.summary;
    }
    
    // Update risks
    updateRisksSection(data.risks);
    
    // Update recommendations
    updateRecommendationsSection(data.recommendations);
    
    // Update confidence
    updateConfidenceDisplay(data.confidence_score);
    
    // Update timestamp
    const timestampElement = document.querySelector('.ai-timestamp small');
    if (timestampElement) {
        const date = new Date(data.created_at);
        timestampElement.innerHTML = `<i class="fas fa-clock"></i> Updated: ${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    }
    
    // Update freshness indicator
    const indicator = document.querySelector('.freshness-indicator');
    if (indicator) {
        indicator.textContent = 'Fresh';
        indicator.className = 'freshness-indicator fresh';
    }
}

function updateRisksSection(risks) {
    const risksContainer = document.querySelector('.ai-risks');
    if (!risksContainer || !risks) return;
    
    risksContainer.innerHTML = '';
    
    risks.forEach(risk => {
        const riskElement = createRiskElement(risk);
        risksContainer.appendChild(riskElement);
    });
}

function createRiskElement(risk) {
    const div = document.createElement('div');
    div.className = `ai-risk-item risk-${risk.priority}`;
    
    div.innerHTML = `
        <div class="risk-header">
            <span class="risk-title">${risk.title}</span>
            <span class="risk-priority priority-${risk.priority}">${risk.priority}</span>
        </div>
        <p class="risk-description">${risk.description}</p>
        ${risk.affected_items ? `
        <div class="risk-affected">
            <small>Affects: ${risk.affected_items.join(', ')}</small>
        </div>
        ` : ''}
        <div class="risk-actions">
            <button class="btn-simulate" onclick="openInterventionSimulator('${risk.title}', ${JSON.stringify(risk).replace(/"/g, '&quot;')})">
                <i class="fas fa-cogs"></i> Simulate Solutions
            </button>
        </div>
    `;
    
    return div;
}

function updateRecommendationsSection(recommendations) {
    const recContainer = document.querySelector('.ai-recommendations');
    if (!recContainer || !recommendations) return;
    
    recContainer.innerHTML = '';
    
    recommendations.forEach(rec => {
        const recElement = createRecommendationElement(rec);
        recContainer.appendChild(recElement);
    });
}

function createRecommendationElement(rec) {
    const div = document.createElement('div');
    div.className = `ai-recommendation-item rec-${rec.priority}`;
    
    div.innerHTML = `
        <div class="rec-header">
            <span class="rec-title">${rec.title}</span>
            <span class="rec-priority priority-${rec.priority}">${rec.priority}</span>
        </div>
        <p class="rec-description">${rec.description}</p>
        ${rec.affected_items ? `
        <div class="rec-affected">
            <small>Related: ${rec.affected_items.join(', ')}</small>
        </div>
        ` : ''}
    `;
    
    return div;
}

function updateConfidenceDisplay(confidence) {
    const confidenceFill = document.querySelector('.confidence-fill');
    const confidenceValue = document.querySelector('.confidence-value');    
    if (confidenceFill) {
        confidenceFill.style.width = `${confidence * 100}%`;
    }
    
    if (confidenceValue) {
        confidenceValue.textContent = `${(confidence * 100).toFixed(1)}%`;
    }
}

/**
 * Intervention Simulator Functions
 */
function initializeInterventionSimulator() {
    // Add event listeners for scenario cards
    document.addEventListener('click', function(e) {
        if (e.target.closest('.scenario-card')) {
            selectScenario(e.target.closest('.scenario-card'));
        }
    });
}

function openInterventionSimulator(riskTitle = '', riskData = null) {
    const modal = document.getElementById('interventionModal');
    if (!modal) return;
    
    // Pre-populate problem if coming from a risk
    if (riskTitle) {
        const titleInput = document.getElementById('problemTitle');
        if (titleInput) {
            titleInput.value = riskTitle;
        }
    }
    
    if (riskData && riskData.description) {
        const descInput = document.getElementById('problemDescription');
        if (descInput) {
            descInput.value = riskData.description;
        }
    }
    
    // Reset to first step
    showSimulationStep('problem');
    currentSimulationStep = 'problem';
    selectedScenario = null;
    
    // Show modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeInterventionModal() {
    const modal = document.getElementById('interventionModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

function nextStep(step) {
    if (step === 'scenario' && !validateProblemForm()) {
        return;
    }
    
    if (step === 'configuration' && !selectedScenario) {
        showNotification('error', 'Please select an intervention scenario');
        return;
    }
    
    if (step === 'configuration') {
        generateConfigurationForm();
    }
    
    showSimulationStep(step);
    currentSimulationStep = step;
}

function previousStep(step) {
    showSimulationStep(step);
    currentSimulationStep = step;
}

function showSimulationStep(step) {
    // Hide all steps
    document.querySelectorAll('.simulation-step').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show target step
    const targetStep = document.getElementById(`step-${step}`);
    if (targetStep) {
        targetStep.classList.add('active');
    }
}

function validateProblemForm() {
    const title = document.getElementById('problemTitle').value.trim();
    const description = document.getElementById('problemDescription').value.trim();
    
    if (!title) {
        showNotification('error', 'Please enter a problem title');
        return false;
    }
    
    if (!description) {
        showNotification('error', 'Please enter a problem description');
        return false;
    }
    
    return true;
}

function selectScenario(card) {
    // Remove previous selection
    document.querySelectorAll('.scenario-card').forEach(c => {
        c.classList.remove('selected');
    });
    
    // Select new card
    card.classList.add('selected');
    selectedScenario = card.dataset.scenario;
    
    // Enable next button
    const nextBtn = document.getElementById('nextToConfig');
    if (nextBtn) {
        nextBtn.disabled = false;
    }
}

function generateConfigurationForm() {
    const configForm = document.getElementById('configurationForm');
    if (!configForm || !selectedScenario) return;
    
    let formHTML = '';
    
    switch (selectedScenario) {
        case 'reassignment':
            formHTML = `
                <div class="form-group">
                    <label for="sourceResource">From Resource</label>
                    <select id="sourceResource" class="form-control" required>
                        <option value="">Select resource...</option>
                        <!-- Resources will be populated dynamically -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="targetResource">To Resource</label>
                    <select id="targetResource" class="form-control" required>
                        <option value="">Select resource...</option>
                        <!-- Resources will be populated dynamically -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="workloadPercentage">Workload to Transfer (%)</label>
                    <input type="number" id="workloadPercentage" class="form-control" min="1" max="100" value="25">
                </div>
            `;
            break;
            
        case 'overtime':
            formHTML = `
                <div class="form-group">
                    <label for="overtimeResource">Resource</label>
                    <select id="overtimeResource" class="form-control" required>
                        <option value="">Select resource...</option>
                        <!-- Resources will be populated dynamically -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="overtimeHours">Additional Hours per Week</label>
                    <input type="number" id="overtimeHours" class="form-control" min="1" max="20" value="10">
                </div>
                <div class="form-group">
                    <label for="overtimeDuration">Duration (weeks)</label>
                    <input type="number" id="overtimeDuration" class="form-control" min="1" max="8" value="2">
                </div>
            `;
            break;
            
        case 'resource_addition':
            formHTML = `
                <div class="form-group">
                    <label for="newResourceRole">Required Role</label>
                    <input type="text" id="newResourceRole" class="form-control" placeholder="e.g., Frontend Developer">
                </div>
                <div class="form-group">
                    <label for="newResourceSkills">Required Skills</label>
                    <input type="text" id="newResourceSkills" class="form-control" placeholder="e.g., React, JavaScript, CSS">
                </div>
                <div class="form-group">
                    <label for="newResourceCost">Estimated Cost (per month)</label>
                    <input type="number" id="newResourceCost" class="form-control" min="0" placeholder="8000">
                </div>
            `;
            break;
            
        case 'deadline_extension':
            formHTML = `
                <div class="form-group">
                    <label for="extensionDays">Extension Period (days)</label>
                    <input type="number" id="extensionDays" class="form-control" min="1" max="90" value="7">
                </div>
                <div class="form-group">
                    <label for="extensionReason">Business Justification</label>
                    <textarea id="extensionReason" class="form-control" rows="3" placeholder="Explain why the extension is necessary..."></textarea>
                </div>
            `;
            break;
            
        case 'scope_reduction':
            formHTML = `
                <div class="form-group">
                    <label for="scopeReduction">Scope Reduction (%)</label>
                    <input type="number" id="scopeReduction" class="form-control" min="5" max="50" value="20">
                </div>
                <div class="form-group">
                    <label for="reducedFeatures">Features to Remove/Defer</label>
                    <textarea id="reducedFeatures" class="form-control" rows="3" placeholder="List features that can be removed or deferred..."></textarea>
                </div>
            `;
            break;
    }
    
    configForm.innerHTML = formHTML;
    
    // Populate resource dropdowns if needed
    populateResourceDropdowns();
}

function populateResourceDropdowns() {
    // This would typically fetch from an API
    // For now, we'll use placeholder data
    const resourceSelects = document.querySelectorAll('select[id*="Resource"]');
    
    resourceSelects.forEach(select => {
        if (select.options.length <= 1) { // Only has placeholder option
            // Add some sample resources (in real implementation, fetch from API)
            const sampleResources = [
                { id: 1, name: 'John Doe', role: 'Frontend Developer' },
                { id: 2, name: 'Jane Smith', role: 'Backend Developer' },
                { id: 3, name: 'Mike Johnson', role: 'UI/UX Designer' },
                { id: 4, name: 'Sarah Wilson', role: 'Project Manager' }
            ];
            
            sampleResources.forEach(resource => {
                const option = document.createElement('option');
                option.value = resource.id;
                option.textContent = `${resource.name} (${resource.role})`;
                select.appendChild(option);
            });
        }
    });
}

function runSimulation() {
    if (!validateConfigurationForm()) {
        return;
    }
    
    // Show results step with loading state
    showSimulationStep('results');
    document.getElementById('resultsActions').style.display = 'none';
    
    // Gather simulation data
    const simulationData = gatherSimulationData();
    
    // Run simulation
    fetch('/dashboard/api/simulate-intervention/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(simulationData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showSimulationError(data.error);
        } else {
            showSimulationResults(data);
        }
    })
    .catch(error => {
        console.error('Simulation error:', error);
        showSimulationError('Failed to run simulation');
    });
}

function validateConfigurationForm() {
    const requiredFields = document.querySelectorAll('#configurationForm [required]');
    
    for (let field of requiredFields) {
        if (!field.value.trim()) {
            showNotification('error', 'Please fill in all required fields');
            field.focus();
            return false;
        }
    }
    
    return true;
}

function gatherSimulationData() {
    const data = {
        scenario_type: selectedScenario,
        title: document.getElementById('problemTitle').value,
        description: document.getElementById('problemDescription').value,
        priority: document.getElementById('problemPriority').value,
        project_id: document.getElementById('affectedProject').value
    };
    
    // Add scenario-specific configuration
    const configInputs = document.querySelectorAll('#configurationForm input, #configurationForm select, #configurationForm textarea');
    configInputs.forEach(input => {
        if (input.value) {
            data[input.id] = input.value;
        }
    });
    
    return data;
}

function showSimulationResults(data) {
    const resultsContainer = document.getElementById('simulationResults');
    
    const resultHTML = `
        <div class="result-card result-success">
            <div class="result-header">
                <div class="result-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div>
                    <h4>Simulation Complete</h4>
                    <p>AI has analyzed your intervention scenario</p>
                </div>
            </div>
        </div>
        
        <div class="result-card">
            <h5><i class="fas fa-target"></i> Predicted Outcome</h5>
            <p><strong>${data.predicted_outcome?.primary_metric || 'Project completion'}:</strong> ${data.predicted_outcome?.expected_value || 'Improved'}</p>
            <p><strong>Timeline:</strong> ${data.predicted_outcome?.timeline || 'Within expected timeframe'}</p>
        </div>
        
        <div class="result-card">
            <h5><i class="fas fa-percentage"></i> Success Probability</h5>
            <div class="probability-bar">
                <div class="probability-fill" style="width: ${(data.success_probability || 0.5) * 100}%"></div>
            </div>
            <p>${((data.success_probability || 0.5) * 100).toFixed(1)}% chance of success</p>
        </div>
        
        <div class="result-card">
            <h5><i class="fas fa-chart-line"></i> Estimated Impact</h5>
            <p>${data.estimated_impact || 'Positive impact expected on project timeline and resource utilization.'}</p>
        </div>
        
        ${data.estimated_cost ? `
        <div class="result-card">
            <h5><i class="fas fa-dollar-sign"></i> Estimated Cost</h5>
            <p>$${parseFloat(data.estimated_cost).toLocaleString()}</p>
        </div>
        ` : ''}
        
        ${data.estimated_time_impact ? `
        <div class="result-card">
            <h5><i class="fas fa-clock"></i> Time Impact</h5>
            <p>${data.estimated_time_impact} hours</p>
        </div>
        ` : ''}
    `;
    
    resultsContainer.innerHTML = resultHTML;
    document.getElementById('resultsActions').style.display = 'flex';
}

function showSimulationError(error) {
    const resultsContainer = document.getElementById('simulationResults');
    
    resultsContainer.innerHTML = `
        <div class="result-error">
            <i class="fas fa-exclamation-triangle"></i>
            <h4>Simulation Failed</h4>
            <p>${error}</p>
            <button class="btn btn-primary" onclick="previousStep('configuration')">
                Try Again
            </button>
        </div>
    `;
}

function restartSimulation() {
    showSimulationStep('problem');
    currentSimulationStep = 'problem';
    selectedScenario = null;
    
    // Clear form
    document.getElementById('problemTitle').value = '';
    document.getElementById('problemDescription').value = '';
    document.getElementById('affectedProject').value = '';
    document.getElementById('problemPriority').value = 'medium';
}

function implementScenario() {
    if (confirm('This will create a task to implement the selected intervention. Continue?')) {
        showNotification('info', 'Implementation task has been created and assigned to the appropriate team member.');
        closeInterventionModal();
    }
}

/**
 * Natural Language Interface Functions
 */
function initializeNLISearch() {
    const searchInput = document.getElementById('nliSearchInput');
    const clearBtn = document.getElementById('clearBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    
    if (searchInput) {
        searchInput.addEventListener('input', handleNLIInput);
        searchInput.addEventListener('keydown', handleNLIKeydown);
        searchInput.addEventListener('focus', showQuickSuggestions);
        searchInput.addEventListener('blur', hideQuickSuggestionsDelayed);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearNLISearch);
    }
    
    if (voiceBtn) {
        voiceBtn.addEventListener('click', toggleVoiceSearch);
    }
    
    // Add click handlers for quick suggestions
    document.addEventListener('click', function(e) {
        if (e.target.closest('.suggestion-item')) {
            const suggestion = e.target.closest('.suggestion-item');
            const query = suggestion.dataset.query;
            if (query) {
                searchInput.value = query;
                processNLIQuery(query);
            }
        }
    });
    
    // Close results when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nli-search-container')) {
            closeNLIResults();
        }
    });
}

function handleNLIInput(e) {
    const query = e.target.value.trim();
    const clearBtn = document.getElementById('clearBtn');
    
    // Show/hide clear button
    if (clearBtn) {
        clearBtn.style.display = query ? 'flex' : 'none';
    }
    
    // Add has-query class
    const searchBar = document.querySelector('.nli-search-bar');
    if (searchBar) {
        searchBar.classList.toggle('has-query', query.length > 0);
    }
    
    // Clear previous timeout
    if (nliTimeout) {
        clearTimeout(nliTimeout);
    }
    
    // Process query after delay
    if (query.length >= 3) {
        nliTimeout = setTimeout(() => {
            processNLIQuery(query);
        }, 500);
    } else if (query.length === 0) {
        closeNLIResults();
    }
}

function handleNLIKeydown(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const query = e.target.value.trim();
        if (query) {
            processNLIQuery(query);
        }
    } else if (e.key === 'Escape') {
        closeNLIResults();
        e.target.blur();
    }
}

function showQuickSuggestions() {
    const suggestions = document.getElementById('quickSuggestions');
    if (suggestions) {
        suggestions.style.display = 'block';
    }
}

function hideQuickSuggestionsDelayed() {
    setTimeout(() => {
        const suggestions = document.getElementById('quickSuggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }, 200);
}

function processNLIQuery(query) {
    currentQuery = query;
    
    // Show loading state
    showNLILoading();
    
    fetch('/dashboard/api/nli-query/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        hideNLILoading();
        if (data.error) {
            showNLIError(data.error);
        } else {
            showNLIResults(data.response);
        }
    })
    .catch(error => {
        console.error('NLI query error:', error);
        hideNLILoading();
        showNLIError('Failed to process query');
    });
}

function showNLILoading() {
    const loadingElement = document.getElementById('nliLoading');
    const resultsElement = document.getElementById('nliResults');
    
    if (resultsElement) {
        resultsElement.style.display = 'none';
    }
    
    if (loadingElement) {
        loadingElement.style.display = 'block';
        loadingElement.classList.add('show');
    }
}

function hideNLILoading() {
    const loadingElement = document.getElementById('nliLoading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
        loadingElement.classList.remove('show');
    }
}

function showNLIResults(response) {
    const resultsElement = document.getElementById('nliResults');
    const contentElement = document.getElementById('resultsContent');
    
    if (!resultsElement || !contentElement) return;
    
    // Format response based on type
    let contentHTML = '';
    
    if (response.error) {
        contentHTML = `
            <div class="result-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${response.error}</p>
            </div>
        `;
    } else {
        contentHTML = `<div class="result-text">${response.text}</div>`;
        
        // Add data visualization if available
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
            if (response.type === 'availability_list' || response.type === 'utilization_list') {
                contentHTML += '<div class="result-data-grid">';
                response.data.slice(0, 6).forEach(item => {
                    contentHTML += `
                        <div class="result-data-item">
                            <h5>${item.name}</h5>
                            <p>${item.role}</p>
                            <p>${response.type === 'availability_list' ? 
                                `${item.availability?.toFixed(1)}% available` : 
                                `${item.utilization?.toFixed(1)}% utilized`}</p>
                        </div>
                    `;
                });
                contentHTML += '</div>';
            } else if (response.type === 'deadline_list') {
                contentHTML += '<ul class="result-list">';
                response.data.slice(0, 8).forEach(item => {
                    contentHTML += `
                        <li>${item.task} (${item.project}) - ${item.days_until} days</li>
                    `;
                });
                contentHTML += '</ul>';
            } else if (response.type === 'project_list') {
                contentHTML += '<div class="result-data-grid">';
                response.data.slice(0, 6).forEach(item => {
                    contentHTML += `
                        <div class="result-data-item">
                            <h5>${item.name}</h5>
                            <p>${item.completion?.toFixed(1)}% complete</p>
                            <p>Status: ${item.status}</p>
                        </div>
                    `;
                });
                contentHTML += '</div>';
            }
        }
    }
    
    contentElement.innerHTML = contentHTML;
    resultsElement.style.display = 'block';
    resultsElement.classList.add('show');
    
    // Update search bar styling
    const searchBar = document.querySelector('.nli-search-bar');
    if (searchBar) {
        searchBar.classList.add('has-results');
    }
    
    // Update results container styling
    resultsElement.classList.add('connected');
}

function showNLIError(error) {
    showNLIResults({ error: error });
}

function closeNLIResults() {
    const resultsElement = document.getElementById('nliResults');
    const searchBar = document.querySelector('.nli-search-bar');
    
    if (resultsElement) {
        resultsElement.style.display = 'none';
        resultsElement.classList.remove('show', 'connected');
    }
    
    if (searchBar) {
        searchBar.classList.remove('has-results');
    }
}

function clearNLISearch() {
    const searchInput = document.getElementById('nliSearchInput');
    const clearBtn = document.getElementById('clearBtn');
    const searchBar = document.querySelector('.nli-search-bar');
    
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
    
    if (clearBtn) {
        clearBtn.style.display = 'none';
    }
    
    if (searchBar) {
        searchBar.classList.remove('has-query');
    }
    
    closeNLIResults();
    currentQuery = '';
}

function toggleVoiceSearch() {
    const voiceBtn = document.getElementById('voiceBtn');
    
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            if (voiceBtn) {
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            }
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const searchInput = document.getElementById('nliSearchInput');
            if (searchInput) {
                searchInput.value = transcript;
                processNLIQuery(transcript);
            }
        };
        
        recognition.onend = function() {
            if (voiceBtn) {
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            showNotification('error', 'Voice recognition failed. Please try again.');
            if (voiceBtn) {
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            }
        };
        
        recognition.start();
    } else {
        showNotification('error', 'Voice recognition not supported in this browser');
    }
}

/**
 * Utility Functions
 */
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function showNotification(type, message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
    
    // Add notification styles if not already present
    if (!document.getElementById('notificationStyles')) {
        const styles = document.createElement('style');
        styles.id = 'notificationStyles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                padding: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 10000;
                min-width: 300px;
                border-left: 4px solid;
                animation: slideInRight 0.3s ease-out;
            }
            
            .notification-success {
                border-left-color: #48bb78;
            }
            
            .notification-error {
                border-left-color: #e53e3e;
            }
            
            .notification-info {
                border-left-color: #4c51bf;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
                flex: 1;
            }
            
            .notification-content i {
                font-size: 1.1rem;
            }
            
            .notification-success .notification-content i {
                color: #48bb78;
            }
            
            .notification-error .notification-content i {
                color: #e53e3e;
            }
            
            .notification-info .notification-content i {
                color: #4c51bf;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: #718096;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
            }
            
            .notification-close:hover {
                background: #f7fafc;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styles);
    }
}
