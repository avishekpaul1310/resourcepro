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
    console.log('=== DOM Content Loaded ===');
    try {
        initializeAIFeatures();
        console.log('AI Features initialized successfully');
    } catch (error) {
        console.error('Error initializing AI features:', error);
    }
});

/**
 * Initialize all AI features
 */
function initializeAIFeatures() {
    initializeNLISearch();
    initializeInterventionSimulator();
    initializeAIAnalyst();
      // Set up event delegation for recommendation buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-recommendations')) {
            e.preventDefault();
            const button = e.target.closest('.btn-recommendations');
            const riskId = button.dataset.riskId;
            const riskTitle = button.dataset.riskTitle;
            
            if (riskId) {
                getRiskRecommendations(riskId, riskTitle);
            } else {
                console.error('No risk ID found for recommendations');
            }
        }
    });
    
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
        ` : ''}        <div class="risk-actions">
            <button class="btn-recommendations" data-risk-id="${risk.id || ''}" data-risk-title="${risk.title}">
                <i class="fas fa-lightbulb"></i> Get AI Recommendations
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
let interventionSimulatorInitialized = false;

function initializeInterventionSimulator() {
    // Prevent duplicate initialization
    if (interventionSimulatorInitialized) {
        console.log('Intervention simulator already initialized, skipping...');
        return;
    }
    
    console.log('Initializing intervention simulator...');
    
    // Add event listeners for scenario cards
    document.addEventListener('click', function(e) {
        if (e.target.closest('.scenario-card')) {
            console.log('Scenario card clicked:', e.target.closest('.scenario-card').dataset.scenario);
            selectScenario(e.target.closest('.scenario-card'));
        }
    });
    
    // Add event listener for run simulation button
    document.addEventListener('click', function(e) {
        if (e.target.id === 'runSimulationBtn' || e.target.closest('#runSimulationBtn')) {
            e.preventDefault();
            console.log('Run simulation button clicked via event listener');
            if (typeof runSimulation === 'function') {
                runSimulation();
            } else {
                console.error('runSimulation function not available');
                if (typeof window.runSimulation === 'function') {
                    console.log('Calling window.runSimulation instead');
                    window.runSimulation();
                } else {
                    console.error('window.runSimulation also not available');                }
            }
        }
    });
    
    // Mark as initialized
    interventionSimulatorInitialized = true;
    console.log('Intervention simulator initialized successfully');
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
    
    // Store risk data for context-aware scenario loading
    if (riskData) {
        modal.dataset.riskData = JSON.stringify(riskData);
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
    console.log('selectScenario called with card:', card, 'scenario:', card.dataset.scenario);
    
    // Remove previous selection
    document.querySelectorAll('.scenario-card').forEach(c => {
        c.classList.remove('selected');
    });
    
    // Select new card
    card.classList.add('selected');
    selectedScenario = card.dataset.scenario;
    
    console.log('Selected scenario:', selectedScenario);
    
    // Enable next button
    const nextBtn = document.getElementById('nextToConfig');
    if (nextBtn) {
        nextBtn.disabled = false;
        console.log('Next button enabled');
    } else {
        console.log('Next button not found');
    }
}

function generateConfigurationForm() {
    const configContainer = document.getElementById('configurationForm');
    if (!configContainer) return;
    
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
                    <select id="newResourceRole" class="form-control" required>
                        <option value="">Select role...</option>
                        <!-- Roles will be populated dynamically -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="newResourceSkills">Required Skills</label>
                    <select id="newResourceSkills" class="form-control" multiple>
                        <!-- Skills will be populated dynamically -->
                    </select>
                    <small class="form-text text-muted">Hold Ctrl/Cmd to select multiple skills</small>
                </div>
                <div class="form-group">
                    <label for="newResourceCost">Estimated Cost (per month)</label>
                    <input type="number" id="newResourceCost" class="form-control" min="0" placeholder="8000">
                </div>
                <div class="form-group">
                    <label for="newResourceStartDate">Expected Start Date</label>
                    <input type="date" id="newResourceStartDate" class="form-control">
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
                    <input type="range" id="scopeReduction" class="form-control" min="5" max="50" value="20" 
                           oninput="updateScopeValue(this.value)">
                    <div class="d-flex justify-content-between">
                        <small>5%</small>
                        <span id="scopeValue">20%</span>
                        <small>50%</small>
                    </div>
                </div>
                <div class="form-group">
                    <label for="tasksToDefer">Tasks/Features to Remove or Defer</label>
                    <select id="tasksToDefer" class="form-control" multiple>
                        <!-- Tasks will be populated dynamically -->
                    </select>
                    <small class="form-text text-muted">Select tasks that can be removed or deferred</small>
                </div>
                <div class="form-group">
                    <label for="reducedFeatures">Custom Features Description</label>
                    <textarea id="reducedFeatures" class="form-control" rows="3" placeholder="Describe any additional features or requirements to remove..."></textarea>
                </div>
            `;
            break;
            
        case 'training':
            formHTML = `
                <div class="form-group">
                    <label for="trainingType">Training Type</label>
                    <select id="trainingType" class="form-control" required>
                        <option value="">Select training type...</option>
                        <option value="technical_skills">Technical Skills</option>
                        <option value="soft_skills">Soft Skills</option>
                        <option value="leadership">Leadership Development</option>
                        <option value="process_training">Process Training</option>
                        <option value="tool_training">Tool/Technology Training</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="trainingTargets">Target Resources</label>
                    <select id="trainingTargets" class="form-control" multiple required>
                        <!-- Populated dynamically -->
                    </select>
                    <small class="form-text text-muted">Select team members who need training</small>
                </div>
                <div class="form-group">
                    <label for="trainingDuration">Training Duration (days)</label>
                    <input type="number" id="trainingDuration" class="form-control" min="1" max="30" value="5" required>
                </div>
                <div class="form-group">
                    <label for="trainingBudget">Training Budget ($)</label>
                    <input type="number" id="trainingBudget" class="form-control" min="0" step="100" value="2000">
                </div>
            `;
            break;
            
        case 'external_resource':
            formHTML = `
                <div class="form-group">
                    <label for="consultantType">Consultant Type</label>
                    <select id="consultantType" class="form-control" required>
                        <option value="">Select consultant type...</option>
                        <option value="technical_expert">Technical Expert</option>
                        <option value="project_manager">Project Manager</option>
                        <option value="business_analyst">Business Analyst</option>
                        <option value="qa_specialist">QA Specialist</option>
                        <option value="domain_expert">Domain Expert</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="consultantSkills">Required Skills</label>
                    <textarea id="consultantSkills" class="form-control" rows="3" 
                              placeholder="List specific skills or expertise needed..."></textarea>
                </div>
                <div class="form-group">
                    <label for="engagementDuration">Engagement Duration (weeks)</label>
                    <input type="number" id="engagementDuration" class="form-control" min="1" max="52" value="4">
                </div>
                <div class="form-group">
                    <label for="consultantBudget">Budget ($)</label>
                    <input type="number" id="consultantBudget" class="form-control" min="0" step="500" value="8000">
                </div>
            `;
            break;
            
        case 'process_improvement':
            formHTML = `
                <div class="form-group">
                    <label for="processArea">Process Area</label>
                    <select id="processArea" class="form-control" required>
                        <option value="">Select process area...</option>
                        <option value="communication">Communication</option>
                        <option value="development">Development Workflow</option>
                        <option value="testing">Testing Process</option>
                        <option value="deployment">Deployment Process</option>
                        <option value="project_management">Project Management</option>
                        <option value="quality_assurance">Quality Assurance</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="currentIssues">Current Issues</label>
                    <textarea id="currentIssues" class="form-control" rows="3" 
                              placeholder="Describe the current process issues..."></textarea>
                </div>
                <div class="form-group">
                    <label for="proposedSolution">Proposed Solution</label>
                    <textarea id="proposedSolution" class="form-control" rows="3" 
                              placeholder="Describe the proposed improvement..."></textarea>
                </div>
                <div class="form-group">
                    <label for="implementationTime">Implementation Time (weeks)</label>
                    <input type="number" id="implementationTime" class="form-control" min="1" max="12" value="3">
                </div>
            `;
            break;
            
        case 'technology_upgrade':
            formHTML = `
                <div class="form-group">
                    <label for="technologyType">Technology Type</label>
                    <select id="technologyType" class="form-control" required>
                        <option value="">Select technology type...</option>
                        <option value="development_tools">Development Tools</option>
                        <option value="project_management">Project Management Tools</option>
                        <option value="communication">Communication Tools</option>
                        <option value="testing_tools">Testing Tools</option>
                        <option value="infrastructure">Infrastructure</option>
                        <option value="automation">Automation Tools</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="currentTechnology">Current Technology</label>
                    <input type="text" id="currentTechnology" class="form-control" 
                           placeholder="Current tools/technology being used">
                </div>
                <div class="form-group">
                    <label for="proposedTechnology">Proposed Technology</label>
                    <input type="text" id="proposedTechnology" class="form-control" 
                           placeholder="Proposed new tools/technology">
                </div>
                <div class="form-group">
                    <label for="migrationTime">Migration Time (weeks)</label>
                    <input type="number" id="migrationTime" class="form-control" min="1" max="24" value="6">
                </div>
                <div class="form-group">
                    <label for="technologyBudget">Budget ($)</label>
                    <input type="number" id="technologyBudget" class="form-control" min="0" step="500" value="5000">
                </div>
            `;
            break;
            
        case 'risk_mitigation':
            formHTML = `
                <div class="form-group">
                    <label for="riskType">Risk Type</label>
                    <select id="riskType" class="form-control" required>
                        <option value="">Select risk type...</option>
                        <option value="technical">Technical Risk</option>
                        <option value="external">External Dependency</option>
                        <option value="team">Team Risk</option>
                        <option value="business">Business Risk</option>
                        <option value="operational">Operational Risk</option>
                        <option value="financial">Financial Risk</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="riskDescription">Risk Description</label>
                    <textarea id="riskDescription" class="form-control" rows="3" 
                              placeholder="Describe the specific risk..."></textarea>
                </div>
                <div class="form-group">
                    <label for="mitigationStrategy">Mitigation Strategy</label>
                    <textarea id="mitigationStrategy" class="form-control" rows="3" 
                              placeholder="Describe the mitigation approach..."></textarea>
                </div>
                <div class="form-group">
                    <label for="contingencyPlan">Contingency Plan</label>
                    <textarea id="contingencyPlan" class="form-control" rows="2" 
                              placeholder="Backup plan if mitigation fails..."></textarea>
                </div>
            `;
            break;
            
        case 'stakeholder_engagement':
            formHTML = `
                <div class="form-group">
                    <label for="stakeholderType">Stakeholder Type</label>
                    <select id="stakeholderType" class="form-control" required>
                        <option value="">Select stakeholder type...</option>
                        <option value="client">Client/Customer</option>
                        <option value="management">Management</option>
                        <option value="team">Team Members</option>
                        <option value="vendor">Vendor/Supplier</option>
                        <option value="end_users">End Users</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="engagementIssue">Engagement Issue</label>
                    <textarea id="engagementIssue" class="form-control" rows="3" 
                              placeholder="Describe the stakeholder issue..."></textarea>
                </div>
                <div class="form-group">
                    <label for="engagementStrategy">Engagement Strategy</label>
                    <textarea id="engagementStrategy" class="form-control" rows="3" 
                              placeholder="How will you re-engage the stakeholder..."></textarea>
                </div>
                <div class="form-group">
                    <label for="successMetrics">Success Metrics</label>
                    <textarea id="successMetrics" class="form-control" rows="2" 
                              placeholder="How will you measure successful engagement..."></textarea>
                </div>
            `;
            break;
            
        case 'quality_assurance':
            formHTML = `
                <div class="form-group">
                    <label for="qualityArea">Quality Area</label>
                    <select id="qualityArea" class="form-control" required>
                        <option value="">Select quality area...</option>
                        <option value="code_quality">Code Quality</option>
                        <option value="testing">Testing Coverage</option>
                        <option value="documentation">Documentation</option>
                        <option value="standards">Standards Compliance</option>
                        <option value="performance">Performance</option>
                        <option value="security">Security</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="qualityIssues">Current Quality Issues</label>
                    <textarea id="qualityIssues" class="form-control" rows="3" 
                              placeholder="Describe current quality problems..."></textarea>
                </div>
                <div class="form-group">
                    <label for="qualityMeasures">Proposed QA Measures</label>
                    <textarea id="qualityMeasures" class="form-control" rows="3" 
                              placeholder="Describe additional QA measures..."></textarea>
                </div>
                <div class="form-group">
                    <label for="qualityTimeline">Implementation Timeline (weeks)</label>
                    <input type="number" id="qualityTimeline" class="form-control" min="1" max="8" value="2">
                </div>
            `;
            break;
            
        case 'communication_plan':
            formHTML = `
                <div class="form-group">
                    <label for="communicationIssue">Communication Issue</label>
                    <select id="communicationIssue" class="form-control" required>
                        <option value="">Select issue type...</option>
                        <option value="unclear_requirements">Unclear Requirements</option>
                        <option value="poor_coordination">Poor Team Coordination</option>
                        <option value="stakeholder_disconnect">Stakeholder Disconnect</option>
                        <option value="information_silos">Information Silos</option>
                        <option value="feedback_delays">Feedback Delays</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="communicationSolution">Communication Solution</label>
                    <textarea id="communicationSolution" class="form-control" rows="3" 
                              placeholder="Describe the communication improvement plan..."></textarea>
                </div>
                <div class="form-group">
                    <label for="communicationTools">Tools/Methods</label>
                    <input type="text" id="communicationTools" class="form-control" 
                           placeholder="Slack, daily standups, documentation tools, etc.">
                </div>
                <div class="form-group">
                    <label for="communicationFrequency">Communication Frequency</label>
                    <select id="communicationFrequency" class="form-control">
                        <option value="daily">Daily</option>
                        <option value="twice_weekly">Twice Weekly</option>
                        <option value="weekly">Weekly</option>
                        <option value="bi_weekly">Bi-weekly</option>
                    </select>
                </div>
            `;
            break;
            
        case 'ai_suggested':
            // Handle AI-suggested custom interventions
            formHTML = generateAISuggestedForm();
            break;
            
        // ...existing cases...
    }
    
    if (formHTML) {
        configContainer.innerHTML = formHTML;
        // Populate dropdowns with real data if needed
        if (['training', 'external_resource'].includes(selectedScenario)) {
            populateResourceDropdowns();
        }
    }
}

function generateAISuggestedForm() {
    // This would be populated based on AI analysis
    return `
        <div class="alert alert-info">
            <i class="fas fa-robot"></i>
            <strong>AI-Suggested Intervention</strong><br>
            This custom intervention was generated based on AI analysis of your specific risk pattern.
        </div>
        <div class="form-group">
            <label for="aiInterventionDetails">Intervention Details</label>
            <textarea id="aiInterventionDetails" class="form-control" rows="4" readonly></textarea>
        </div>
        <div class="form-group">
            <label for="aiImplementationPlan">Implementation Plan</label>
            <textarea id="aiImplementationPlan" class="form-control" rows="3" readonly></textarea>
        </div>
        <div class="form-group">
            <label for="aiSuccessMetrics">Success Metrics</label>
            <textarea id="aiSuccessMetrics" class="form-control" rows="2" readonly></textarea>
        </div>
    `;
}

function showAISuggestedScenario(interventions) {
    const aiScenario = document.getElementById('ai-suggested-scenario');
    if (aiScenario && interventions.length > 0) {
        const topIntervention = interventions[0];
        document.getElementById('ai-scenario-title').textContent = topIntervention.name || 'AI-Suggested Solution';
        document.getElementById('ai-scenario-description').textContent = 
            topIntervention.description || 'Custom intervention recommended by AI';
        aiScenario.style.display = 'block';
        
        // Store intervention data for form population
        aiScenario.dataset.interventionData = JSON.stringify(topIntervention);
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

function openInterventionSimulatorFromButton(button) {
    try {
        const riskTitle = button.dataset.riskTitle || '';
        let riskDataStr = button.dataset.riskData;
        let riskData = null;
        
        if (riskDataStr) {
            // Decode HTML entities if they exist
            const textArea = document.createElement('textarea');
            textArea.innerHTML = riskDataStr;
            riskDataStr = textArea.value;
            
            riskData = JSON.parse(riskDataStr);
        }
        
        openInterventionSimulator(riskTitle, riskData);
    } catch (error) {
        console.error('Error opening intervention simulator:', error);
        showNotification('error', 'Failed to open intervention simulator');
    }
}

// Make function globally available
window.openInterventionSimulatorFromButton = openInterventionSimulatorFromButton;

// Helper function to populate role dropdown for additional resource scenario
function populateRoleDropdown(resources) {
    const roleSelect = document.getElementById('newResourceRole');
    if (!roleSelect) return;
    
    // Extract unique roles from resources
    const roles = [...new Set(resources.map(r => r.role))];
    
    roles.forEach(role => {
        const option = document.createElement('option');
        option.value = role;
        option.textContent = role;
        roleSelect.appendChild(option);
    });
}

// Helper function to populate skills dropdown for additional resource scenario
function populateSkillsDropdown(resources) {
    const skillsSelect = document.getElementById('newResourceSkills');
    if (!skillsSelect) return;
    
    // Extract unique skills from all resources
    const allSkills = new Set();
    resources.forEach(resource => {
        if (resource.skills) {
            resource.skills.forEach(skill => allSkills.add(skill));
        }
    });
    
    [...allSkills].sort().forEach(skill => {
        const option = document.createElement('option');
        option.value = skill;
        option.textContent = skill;
        skillsSelect.appendChild(option);
    });
}

// Function to fetch project tasks for scope reduction scenario
function fetchProjectTasks(projectId) {
    const tasksSelect = document.getElementById('tasksToDefer');
    if (!tasksSelect) return;
    
    fetch(`/dashboard/api/project-tasks/?project_id=${projectId}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear existing options
            tasksSelect.innerHTML = '';
            
            // Add tasks as options
            data.tasks.forEach(task => {
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = `${task.name} (${task.status}, ${task.completion_percentage}% complete)`;
                tasksSelect.appendChild(option);
            });
        } else {
            console.error('Failed to fetch project tasks:', data.error);
        }
    })
    .catch(error => {
        console.error('Error fetching project tasks:', error);
    });
}

// Function to update scope reduction percentage display
function updateScopeValue(value) {
    const scopeValueElement = document.getElementById('scopeValue');
    if (scopeValueElement) {
        scopeValueElement.textContent = value + '%';
    }
}

/**
 * Get AI recommendations for a specific risk
 */
function getRiskRecommendations(riskId, riskTitle) {
    console.log(`Getting recommendations for risk: ${riskTitle} (ID: ${riskId})`);
    
    // Show loading state
    showRecommendationsModal(riskTitle, 'loading');
    
    fetch('/dashboard/api/get-risk-recommendations/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            risk_id: riskId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showRecommendationsModal(riskTitle, 'error', data.error);
        } else {
            showRecommendationsModal(riskTitle, 'success', null, data.recommendations);
        }
    })
    .catch(error => {
        console.error('Error getting recommendations:', error);
        showRecommendationsModal(riskTitle, 'error', 'Failed to get recommendations');
    });
}

/**
 * Show recommendations modal
 */
function showRecommendationsModal(riskTitle, state, errorMessage = null, recommendations = null) {
    // Remove existing modal
    const existingModal = document.getElementById('recommendationsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal
    const modal = document.createElement('div');
    modal.id = 'recommendationsModal';
    modal.className = 'modal-overlay';
    modal.style.display = 'flex';
    
    let modalContent = '';
    
    if (state === 'loading') {
        modalContent = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-lightbulb"></i> AI Recommendations</h3>
                    <button class="modal-close" onclick="closeRecommendationsModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin"></i>
                        <p>Generating AI recommendations for: <strong>${riskTitle}</strong></p>
                    </div>
                </div>
            </div>
        `;
    } else if (state === 'error') {
        modalContent = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-exclamation-triangle"></i> Error</h3>
                    <button class="modal-close" onclick="closeRecommendationsModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="error-message">
                        <p><strong>Failed to generate recommendations</strong></p>
                        <p>${errorMessage}</p>
                        <button class="btn btn-secondary" onclick="closeRecommendationsModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
    } else if (state === 'success' && recommendations) {
        const recommendationsList = recommendations.map((rec, index) => `
            <div class="recommendation-card">
                <div class="recommendation-header">
                    <h4>${rec.title}</h4>
                    <div class="success-score">
                        <span class="score-label">Success Rate:</span>
                        <span class="score-value">${rec.success_probability}%</span>
                    </div>
                </div>
                <p class="recommendation-description">${rec.description}</p>
                <div class="recommendation-meta">
                    <span class="effort-level">Effort: ${rec.implementation_effort || 'Medium'}</span>
                    <span class="timeframe">Timeline: ${rec.timeframe || 'Short-term'}</span>
                </div>
            </div>
        `).join('');
        
        modalContent = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-lightbulb"></i> AI Recommendations</h3>
                    <button class="modal-close" onclick="closeRecommendationsModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="recommendations-content">
                        <div class="risk-context">
                            <h4>Risk: ${riskTitle}</h4>
                            <p>Here are AI-generated recommendations to address this risk:</p>
                        </div>
                        <div class="recommendations-list">
                            ${recommendationsList}
                        </div>
                        <div class="modal-actions">
                            <button class="btn btn-primary" onclick="closeRecommendationsModal()">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

/**
 * Close recommendations modal
 */
function closeRecommendationsModal() {
    const modal = document.getElementById('recommendationsModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

/**
 * Get CSRF token for API calls
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
