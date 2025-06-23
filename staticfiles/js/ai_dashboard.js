/**
 * AI Dashboard Features JavaScript - Simplified Version
 * Handles AI-powered dashboard analyst and recommendation system
 */

// Global state
let currentQuery = '';
let nliTimeout = null;
let nliInitialized = false;  // Flag to prevent multiple initialization

// EMERGENCY SAFETY: Prevent page freezing from AI recommendations
let modalCreationInProgress = false;

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

// Backup initialization for allocation page (in case allocation JS doesn't load)
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const searchInput = document.getElementById('nliSearchInput');
        if (searchInput && !nliInitialized) {
            console.log('=== Backup NLI Initialization ===');
            initializeNLISearch();
        }
    }, 1000);
});

/**
 * Initialize all AI features
 */
function initializeAIFeatures() {
    // Safety check: ensure page scroll is enabled on initialization
    restorePageScroll();
    
    initializeAIAnalyst();
    initializeNLISearch();
    
    // For allocation page, also try to initialize after a short delay
    // to handle cases where allocation-specific JS loads later
    if (window.location.pathname.includes('/allocation/')) {
        setTimeout(() => {
            if (!nliInitialized) {
                console.log('Retrying NLI initialization for allocation page...');
                initializeNLISearch();
            }
        }, 500);
    }
    
    // Set up event delegation for recommendation buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-recommendations')) {
            e.preventDefault();
            const button = e.target.closest('.btn-recommendations');
            const riskId = button.dataset.riskId;
            const riskTitle = button.dataset.riskTitle;
            
            if (riskId && riskId !== '' && riskId !== 'None') {
                getRiskRecommendations(riskId, riskTitle);
            } else {
                console.error('No valid risk ID found for recommendations');
                showRecommendationsModal(riskTitle || 'Unknown Risk', 'error', 'Invalid risk ID. Please try refreshing the page.');
            }
        }
    });
    
    // Auto-refresh AI analysis every 30 minutes (but only if user explicitly wants it)
    // Removed auto-refresh to prevent constant layout changes
    console.log('AI Dashboard initialized - auto-refresh disabled to maintain stable layout');
      // Add safety interval to check for stuck modals/scroll issues
    setInterval(function() {
        const modal = document.getElementById('recommendationsModal');
        const bodyOverflow = document.body.style.overflow;
        
        // Check for stuck scroll without modal
        if (!modal && bodyOverflow === 'hidden') {
            console.warn('🚨 Detected stuck scroll state, restoring...');
            restorePageScroll();
        }
        
        // Check for modals that have been open too long
        if (modal) {
            const modalAge = Date.now() - (modal._createdAt || Date.now());
            if (modalAge > 30000) { // 30 seconds
                console.warn('🚨 Detected stuck modal, auto-closing...');
                closeRecommendationsModal();
            } else if (!modal._createdAt) {
                modal._createdAt = Date.now();
            }
        }
    }, 2000); // Check every 2 seconds
}

/**
 * Initialize AI Analyst widget
 */
function initializeAIAnalyst() {
    // Only refresh on explicit user action, not automatically
    // Remove auto-refresh behavior to prevent layout changes
    
    // Check if we already have content rendered from the server
    const widget = document.querySelector('.ai-analyst-widget');
    if (widget && widget.querySelector('.ai-content')) {
        console.log('AI widget already rendered from server, skipping auto-refresh');
        return; // Don't replace server-rendered content
    }
    
    // Only load if no content exists
    if (widget && !widget.querySelector('.ai-content')) {
        console.log('Loading AI analysis for empty widget');
        refreshAIAnalysis(false);
    }
}

/**
 * AI Dashboard Analyst Functions
 */
function refreshAIAnalysis(force = true) {
    const widget = document.querySelector('.ai-analyst-widget');
    if (!widget) return;
    
    // Show loading state
    if (force) {
        widget.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Analyzing dashboard data...</div>';
    }
    
    const apiCall = force ? 
        fetch('/dashboard/api/refresh-ai-analysis/', { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } }) :
        fetch('/dashboard/api/refresh-ai-analysis/', { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
    
    apiCall
        .then(response => response.json())
        .then(data => {
            updateAIAnalysisWidget(data);
        })
        .catch(error => {
            console.error('Error refreshing AI analysis:', error);
            widget.innerHTML = '<div class="error-message">Failed to load AI analysis</div>';
        });
}

function updateAIAnalysisWidget(data) {
    const widget = document.querySelector('.ai-analyst-widget');
    if (!widget) return;
    
    widget.innerHTML = `
        <div class="ai-analysis-content">
            <div class="analysis-summary">
                <h4><i class="fas fa-brain"></i> AI Analysis</h4>
                <p>${data.summary || 'No analysis available'}</p>
                <div class="confidence-indicator">
                    <span>Confidence: </span>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${(data.confidence_score || 0) * 100}%"></div>
                    </div>
                    <span class="confidence-value">${Math.round((data.confidence_score || 0) * 100)}%</span>
                </div>
            </div>
            
            <div class="analysis-sections">
                <div class="ai-risks">
                    <h5><i class="fas fa-exclamation-triangle"></i> Key Risks</h5>
                    <div class="risks-container"></div>
                </div>
                
                <div class="ai-recommendations">
                    <h5><i class="fas fa-lightbulb"></i> Recommendations</h5>
                    <div class="recommendations-container"></div>
                </div>
            </div>
              <div class="analysis-meta">
                <small>Last updated: ${new Date(data.created_at).toLocaleString()}</small>
            </div>
        </div>
    `;
    
    // Update sections
    updateRisksSection(data.risks || []);
    updateRecommendationsSection(data.recommendations || []);
    updateConfidenceDisplay(data.confidence_score || 0);
}

function updateRisksSection(risks) {
    const riskContainer = document.querySelector('.risks-container');
    if (!riskContainer || !risks) return;
    
    riskContainer.innerHTML = '';
    
    risks.forEach(risk => {
        const riskElement = createRiskElement(risk);
        riskContainer.appendChild(riskElement);
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
    `;
    
    return div;
}

function updateRecommendationsSection(recommendations) {
    const recContainer = document.querySelector('.recommendations-container');
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
        confidenceValue.textContent = `${Math.round(confidence * 100)}%`;
    }
}

/**
 * Get AI recommendations for a specific risk
 */
function getRiskRecommendations(riskId, riskTitle) {
    console.log(`Getting recommendations for risk: ${riskTitle} (ID: ${riskId})`);
    
    // Validate inputs
    if (!riskId || riskId === '' || riskId === 'None') {
        console.error('Invalid risk ID:', riskId);
        showRecommendationsModal(riskTitle, 'error', 'Invalid risk ID. Please try refreshing the page.');
        return;
    }
    
    // Show loading state
    showRecommendationsModal(riskTitle, 'loading');
    
    // Set a timeout for the request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
        console.error('Request timed out');
        showRecommendationsModal(riskTitle, 'error', 'Request timed out. Please try again.');
        restorePageScroll();
    }, 15000); // 15 second timeout
    
    fetch('/dashboard/api/get-risk-recommendations/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            risk_id: riskId
        }),
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        console.log('API Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('API Response data:', data);
        
        if (data.error) {
            showRecommendationsModal(riskTitle, 'error', data.error);
        } else if (data.recommendations && Array.isArray(data.recommendations)) {
            showRecommendationsModal(riskTitle, 'success', null, data.recommendations);
        } else {
            // Handle unexpected response format
            console.warn('Unexpected response format:', data);
            showRecommendationsModal(riskTitle, 'error', 'Received unexpected response format. Please try again.');
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        console.error('Error getting recommendations:', error);
        
        if (error.name === 'AbortError') {
            showRecommendationsModal(riskTitle, 'error', 'Request was cancelled due to timeout.');
        } else {
            showRecommendationsModal(riskTitle, 'error', `Failed to get recommendations: ${error.message}`);
        }
        
        // Ensure scroll is restored in case of error
        setTimeout(() => {
            restorePageScroll();
        }, 100);
    });
}

/**
 * Show recommendations modal
 */
function showRecommendationsModal(riskTitle, state, errorMessage = null, recommendations = null) {
    // Use setTimeout to ensure this doesn't block the UI thread
    setTimeout(() => {
        try {
            console.log(`Showing recommendations modal: ${state} for ${riskTitle}`);
            
            // Remove existing modal first
            const existingModal = document.getElementById('recommendationsModal');
            if (existingModal) {
                existingModal.remove();
                restorePageScroll(); // Ensure scroll is restored
            }

            // Create modal
            const modal = document.createElement('div');
            modal.id = 'recommendationsModal';
            modal.className = 'modal-overlay';
            modal.style.display = 'flex';
            modal._createdAt = Date.now(); // Add timestamp for monitoring

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
                        <p><small>This may take a few seconds...</small></p>
                    </div>
                </div>
            </div>
        `;
        
        // Auto-close loading modal after 20 seconds as a safety net
        setTimeout(() => {
            const loadingModal = document.getElementById('recommendationsModal');
            if (loadingModal && loadingModal.innerHTML.includes('loading-spinner')) {
                console.warn('Auto-closing stuck loading modal');
                closeRecommendationsModal();
                showRecommendationsModal(riskTitle, 'error', 'Request took too long. Please try again.');
            }
        }, 20000);
        
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
                        <div style="margin-top: 15px;">
                            <button class="btn btn-secondary" onclick="closeRecommendationsModal()">Close</button>
                            <button class="btn btn-primary" onclick="closeRecommendationsModal(); setTimeout(() => getRiskRecommendations('${riskTitle.replace(/'/g, '\\\'').replace(/"/g, '\\"')}', '${riskTitle.replace(/'/g, '\\\'').replace(/"/g, '\\"')}'), 500);" style="margin-left: 10px;">Try Again</button>
                        </div>
                    </div>
                </div>
            </div>
        `;    } else if (state === 'success' && recommendations) {
        // SIMPLIFIED: Just show the first recommendation with basic formatting
        let recommendationContent = '';
        try {
            console.log('Processing simplified recommendations:', recommendations);
            
            if (Array.isArray(recommendations) && recommendations.length > 0) {
                const rec = recommendations[0]; // Just take the first one
                const title = rec.title || 'Recommendation';
                const description = rec.description || 'No description available';
                
                recommendationContent = `
                    <div class="recommendation-simple">
                        <h4>${title}</h4>
                        <p>${description}</p>
                    </div>
                `;
            } else {
                recommendationContent = '<p>No recommendations available.</p>';
            }
            
            console.log('Successfully processed simple recommendation');
            
        } catch (error) {
            console.error('Error processing recommendation:', error);
            recommendationContent = '<p>Error loading recommendation. Please try again.</p>';
        }
          modalContent = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-lightbulb"></i> AI Recommendation</h3>
                    <button class="modal-close" onclick="closeRecommendationsModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="recommendations-content">
                        <div class="risk-context">
                            <h4>Risk: ${riskTitle}</h4>
                            <p>Here is an AI-generated recommendation to address this risk:</p>
                        </div>
                        <div class="recommendation-simple">
                            ${recommendationContent}
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
    
    // Disable page scroll only after successful modal creation
    disablePageScroll();
    
    // Add click outside to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeRecommendationsModal();
        }
    });
    
    // Add escape key to close
    const escapeHandler = function(e) {
        if (e.key === 'Escape') {
            closeRecommendationsModal();
            document.removeEventListener('keydown', escapeHandler);        }
    };
    document.addEventListener('keydown', escapeHandler);
    
        } catch (error) {
            console.error('Error showing recommendations modal:', error);
            // Fallback: show simple alert
            alert(`Error showing recommendations: ${error.message}`);
            restorePageScroll();
        }
    }, 10); // Small delay to ensure UI thread doesn't block
}

/**
 * Close recommendations modal
 */
function closeRecommendationsModal() {
    const modal = document.getElementById('recommendationsModal');
    if (modal) {
        modal.remove();
    }
    restorePageScroll();
}

/**
 * Safely disable page scroll
 */
function disablePageScroll() {
    try {
        document.body.style.overflow = 'hidden';
        console.log('Page scroll disabled');
    } catch (error) {
        console.error('Error disabling page scroll:', error);
    }
}

/**
 * Safely restore page scroll
 */
function restorePageScroll() {
    try {
        document.body.style.overflow = '';
        console.log('Page scroll restored');
    } catch (error) {
        console.error('Error restoring page scroll:', error);
    }
}

/**
 * Natural Language Interface Functions
 */
function initializeNLISearch() {
    // Prevent multiple initialization
    if (nliInitialized) {
        console.log('NLI Search already initialized, skipping...');
        return;
    }
    
    const searchInput = document.getElementById('nliSearchInput');
    const clearBtn = document.getElementById('clearBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    
    // Only initialize if the search elements exist
    if (!searchInput) {
        console.log('NLI Search elements not found on this page, skipping initialization');
        return;
    }
    
    console.log('Initializing NLI Search...');
    
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
            if (query && searchInput) {
                searchInput.value = query;
                processNLIQuery(query);
            }
        }
        
        // Close results when clicking outside
        if (!e.target.closest('.nli-search-container')) {
            closeNLIResults();
        }
    });
    
    nliInitialized = true;
    console.log('NLI Search initialized successfully');
}

function handleNLIInput(e) {
    const query = e.target.value.trim();
    currentQuery = query;
    
    // Update clear button visibility
    updateClearButtonVisibility();
    
    // Clear existing timeout
    if (nliTimeout) {
        clearTimeout(nliTimeout);
    }
    
    // Set new timeout for delayed search
    if (query.length > 2) {
        nliTimeout = setTimeout(() => {
            processNLIQuery(query);
        }, 800);
    } else {
        hideNLIResults();
    }
}

function hideNLIResults() {
    const resultsContainer = document.getElementById('nliResults');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

function handleNLIKeydown(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const query = e.target.value.trim();
        if (query.length > 2) {
            processNLIQuery(query);
        }
    }
}

function processNLIQuery(query) {
    if (!query || query.length < 3) return;
    
    showNLILoading();
    
    fetch('/api/ai-search/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        displayNLIResults(data);
    })
    .catch(error => {
        console.error('Error processing NLI query:', error);
        hideNLIResults();
    });
}

function showNLILoading() {
    const resultsContainer = document.getElementById('nliResults');
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = '<div class="nli-loading"><i class="fas fa-spinner fa-spin"></i> Processing...</div>';
    }
}

function displayNLIResults(data) {
    const resultsContainer = document.getElementById('nliResults');
    if (!resultsContainer) return;
    
    if (data.error) {
        resultsContainer.innerHTML = `
            <div class="results-header">
                <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                <button class="btn-close-results" onclick="closeNLIResults()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="nli-error">
                <i class="fas fa-exclamation-circle"></i>
                Error: ${data.error}
            </div>
        `;
        resultsContainer.style.display = 'block';
        return;
    }
    
    const response = data.response || {};
    const responseText = response.text || response.answer || 'No response available';
    const hasData = response.data && Array.isArray(response.data) && response.data.length > 0;
    
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        <div class="results-header">
            <h4><i class="fas fa-robot"></i> AI Assistant Response</h4>
            <button class="btn-close-results" onclick="closeNLIResults()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="nli-response">
            <div class="nli-answer">
                <div class="answer-text">${formatResponseText(responseText)}</div>
                ${response.confidence ? `
                    <div class="nli-confidence">
                        <i class="fas fa-chart-line"></i>
                        <span>Confidence: ${response.confidence}%</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${response.confidence}%"></div>
                        </div>
                    </div>
                ` : ''}
            </div>
            ${hasData ? formatStructuredData(response.data, response.type) : ''}        </div>
    `;
}

/**
 * Format response text with proper line breaks and styling
 */
function formatResponseText(text) {
    if (!text) return 'No response available';
    
    // Convert newlines to proper HTML breaks
    return text
        .replace(/\n/g, '<br>')
        .replace(/•/g, '<i class="fas fa-circle bullet-point"></i>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold text
}

/**
 * Format structured data based on type
 */
function formatStructuredData(data, type) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        return '';
    }
    
    // Filter out any null/undefined items
    const validData = data.filter(item => item && typeof item === 'object');
    
    if (validData.length === 0) {
        return '';
    }
    
    switch (type) {
        case 'availability_list':
            return formatAvailabilityData(validData);
        case 'deadline_list':
            return formatDeadlineData(validData);
        case 'utilization_list':
            return formatUtilizationData(validData);
        case 'project_list':
            return formatProjectData(validData);
        case 'task_list':
            return formatTaskData(validData);
        case 'activity_list':
            return formatActivityData(validData);
        case 'resource_list':
            return formatResourceData(validData);
        default:
            return formatGenericData(validData);
    }
}

/**
 * Format availability data
 */
function formatAvailabilityData(data) {
    const items = data.slice(0, 10); // Show max 10 items
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-users"></i> Available Resources</h5>
            <div class="data-grid">
                ${items.map(item => `
                    <div class="data-card availability-card">
                        <div class="card-header">
                            <h6>${item.name || 'Unknown'}</h6>
                            <span class="role-badge">${item.role || 'N/A'}</span>
                        </div>
                        <div class="availability-bar">
                            <div class="availability-fill" style="width: ${item.availability || 0}%"></div>
                            <span class="availability-text">${(item.availability || 0).toFixed(1)}% Available</span>
                        </div>
                    </div>
                `).join('')}
            </div>
            ${data.length > 10 ? `<p class="show-more">... and ${data.length - 10} more resources</p>` : ''}
        </div>
    `;
}

/**
 * Format deadline data
 */
function formatDeadlineData(data) {
    const items = data.slice(0, 10);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-calendar-alt"></i> Upcoming Deadlines</h5>
            <div class="data-list">
                ${items.map(item => {
                    const urgencyClass = item.days_until <= 1 ? 'urgent' : item.days_until <= 3 ? 'warning' : 'normal';
                    const urgencyIcon = item.days_until <= 1 ? 'fas fa-exclamation-triangle' : 'fas fa-clock';
                    
                    return `
                        <div class="data-item deadline-item ${urgencyClass}">
                            <div class="item-icon">
                                <i class="${urgencyIcon}"></i>
                            </div>
                            <div class="item-content">
                                <h6>${item.task || 'Unknown Task'}</h6>
                                <p class="project-name">${item.project || 'Unknown Project'}</p>
                                <div class="deadline-info">
                                    <span class="days-until">${item.days_until} day${item.days_until !== 1 ? 's' : ''}</span>
                                    <span class="status-badge ${item.status}">${item.status || 'unknown'}</span>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            ${data.length > 10 ? `<p class="show-more">... and ${data.length - 10} more deadlines</p>` : ''}
        </div>
    `;
}

/**
 * Format utilization data
 */
function formatUtilizationData(data) {
    const items = data.slice(0, 10);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-chart-pie"></i> Resource Utilization</h5>
            <div class="data-list">
                ${items.map(item => {
                    const utilizationClass = item.utilization >= 100 ? 'overallocated' : item.utilization >= 80 ? 'high' : 'normal';
                    
                    return `
                        <div class="data-item utilization-item ${utilizationClass}">
                            <div class="item-content">
                                <h6>${item.name || 'Unknown'}</h6>
                                <p class="role-name">${item.role || 'Unknown Role'}</p>
                                <div class="utilization-info">
                                    <div class="utilization-bar">
                                        <div class="utilization-fill" style="width: ${Math.min(item.utilization || 0, 100)}%"></div>
                                    </div>
                                    <span class="utilization-text">${(item.utilization || 0).toFixed(1)}%</span>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            ${data.length > 10 ? `<p class="show-more">... and ${data.length - 10} more resources</p>` : ''}
        </div>
    `;
}

/**
 * Format project data
 */
function formatProjectData(data) {
    const items = data.slice(0, 8);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-project-diagram"></i> Projects</h5>
            <div class="data-grid">
                ${items.map(item => `
                    <div class="data-card project-card">
                        <div class="card-header">
                            <h6>${item.name || 'Unknown Project'}</h6>
                            <span class="status-badge ${item.status}">${item.status || 'unknown'}</span>
                        </div>
                        <div class="project-details">
                            ${item.completion !== undefined ? `
                                <div class="completion-info">
                                    <span>Progress: ${item.completion}%</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${item.completion}%"></div>
                                    </div>
                                </div>
                            ` : ''}
                            ${item.deadline ? `<p class="deadline">Due: ${item.deadline}</p>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
            ${data.length > 8 ? `<p class="show-more">... and ${data.length - 8} more projects</p>` : ''}
        </div>
    `;
}

/**
 * Format task data
 */
function formatTaskData(data) {
    const items = data.slice(0, 10);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-tasks"></i> Tasks</h5>
            <div class="data-list">
                ${items.map(item => `
                    <div class="data-item task-item">
                        <div class="item-content">
                            <h6>${item.name || 'Unknown Task'}</h6>
                            <p class="project-name">${item.project || 'Unknown Project'}</p>
                            <div class="task-info">
                                <span class="status-badge ${item.status}">${item.status || 'unknown'}</span>
                                ${item.assignee ? `<span class="assignee">Assigned to: ${item.assignee}</span>` : ''}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            ${data.length > 10 ? `<p class="show-more">... and ${data.length - 10} more tasks</p>` : ''}
        </div>
    `;
}

/**
 * Format activity data
 */
function formatActivityData(data) {
    const items = data.slice(0, 10);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-chart-line"></i> Resource Activity</h5>
            <div class="data-list">
                ${items.map(item => {
                    const activityLevel = item.activity_score >= 80 ? 'high' : item.activity_score >= 50 ? 'medium' : 'low';
                    
                    return `
                        <div class="data-item activity-item ${activityLevel}">
                            <div class="item-content">
                                <h6>${item.name || 'Unknown'}</h6>
                                <p class="role-name">${item.role || 'Unknown Role'} ${item.department ? `• ${item.department}` : ''}</p>
                                <div class="activity-info">
                                    <div class="activity-stats">
                                        <span class="stat-item">
                                            <i class="fas fa-percentage"></i>
                                            Utilization: ${(item.utilization || 0).toFixed(1)}%
                                        </span>
                                        <span class="stat-item">
                                            <i class="fas fa-tasks"></i>
                                            Active: ${item.active_assignments || 0}
                                        </span>
                                        ${item.activity_score ? `
                                            <span class="stat-item">
                                                <i class="fas fa-fire"></i>
                                                Activity: ${item.activity_score.toFixed(1)}
                                            </span>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            ${data.length > 10 ? `<p class="show-more">... and ${data.length - 10} more resources</p>` : ''}
        </div>
    `;
}

/**
 * Format resource data
 */
function formatResourceData(data) {
    const items = data.slice(0, 10);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-users"></i> Resources</h5>
            <div class="data-grid">
                ${items.map(item => {
                    const statusClass = item.utilization >= 90 ? 'busy' : item.utilization >= 70 ? 'active' : 'available';
                    
                    return `
                        <div class="data-card resource-card ${statusClass}">
                            <div class="card-header">
                                <h6>${item.name || 'Unknown'}</h6>
                                <span class="role-badge">${item.role || 'N/A'}</span>
                            </div>
                            <div class="resource-details">
                                ${item.department ? `<p class="department">${item.department}</p>` : ''}
                                ${item.utilization !== undefined ? `
                                    <div class="utilization-info">
                                        <span>Utilization: ${item.utilization.toFixed(1)}%</span>
                                        <div class="utilization-bar">
                                            <div class="utilization-fill" style="width: ${Math.min(item.utilization, 100)}%"></div>
                                        </div>
                                    </div>
                                ` : ''}
                                ${item.skills ? `
                                    <div class="skills-list">
                                        <small>Skills: ${Array.isArray(item.skills) ? item.skills.join(', ') : item.skills}</small>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            ${data.length > 10 ? `<p class="show-more">... and ${data.length - 10} more resources</p>` : ''}
        </div>
    `;
}

/**
 * Format generic data when type is unknown
 */
function formatGenericData(data) {
    const items = data.slice(0, 5);
    
    return `
        <div class="structured-data">
            <h5><i class="fas fa-info-circle"></i> Additional Information</h5>
            <div class="data-list">
                ${items.map(item => {
                    // Try to extract meaningful information from the object
                    const mainField = item.name || item.title || item.task || item.resource || Object.values(item)[0];
                    const subFields = Object.entries(item)
                        .filter(([key, value]) => key !== 'name' && key !== 'title' && key !== 'task' && key !== 'resource')
                        .slice(0, 3);
                    
                    return `
                        <div class="data-item generic-item">
                            <div class="item-content">
                                <h6>${mainField || 'Item'}</h6>
                                ${subFields.map(([key, value]) => `
                                    <p class="item-detail"><strong>${key}:</strong> ${value}</p>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            ${data.length > 5 ? `<p class="show-more">... and ${data.length - 5} more items</p>` : ''}
        </div>
    `;
}

function hideNLIResults() {
    const resultsContainer = document.getElementById('nli-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
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

/**
 * Update only the AI content without changing the layout structure
 */
function updateAIContentOnly(data) {
    // Update summary
    const summaryElement = document.querySelector('.ai-summary');
    if (summaryElement && data.summary) {
        summaryElement.textContent = data.summary;
    }
    
    // Update confidence
    const confidenceFill = document.querySelector('.confidence-fill');
    const confidenceValue = document.querySelector('.confidence-value');
    if (confidenceFill && data.confidence_score !== undefined) {
        confidenceFill.style.width = `${Math.round(data.confidence_score * 100)}%`;
    }
    if (confidenceValue && data.confidence_score !== undefined) {
        confidenceValue.textContent = `${Math.round(data.confidence_score * 100)}%`;
    }
    
    // Update timestamp
    const timestampElement = document.querySelector('.ai-timestamp small');
    if (timestampElement && data.created_at) {
        const date = new Date(data.created_at);
        timestampElement.innerHTML = `<i class="fas fa-clock"></i> Updated: ${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    }
    
    // Update risks section if it exists
    const risksContainer = document.querySelector('.ai-risks');
    if (risksContainer && data.risks) {
        updateRisksInTemplate(data.risks);
    }
}

/**
 * Update risks while maintaining the template structure
 */
function updateRisksInTemplate(risks) {
    const risksContainer = document.querySelector('.ai-risks');
    if (!risksContainer) return;
    
    // Clear existing risks but keep the structure
    const existingRisks = risksContainer.querySelectorAll('.ai-risk-item');
    existingRisks.forEach(risk => risk.remove());
    
    // Add new risks in the template format
    risks.forEach(risk => {
        const riskElement = document.createElement('div');
        riskElement.className = `ai-risk-item risk-${risk.priority || 'medium'}`;
        riskElement.innerHTML = `
            <div class="risk-header">
                <span class="risk-title">${risk.title}</span>
                <span class="risk-priority priority-${risk.priority || 'medium'}">${(risk.priority || 'medium').charAt(0).toUpperCase() + (risk.priority || 'medium').slice(1)}</span>
            </div>
            <p class="risk-description">${risk.description || ''}</p>
            ${risk.affected_items ? `<small class="risk-affects">Affects: ${risk.affected_items.join(', ')}</small>` : ''}
        `;
        risksContainer.appendChild(riskElement);
    });
}

/**
 * Voice Search Functions
 */
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
 * Quick Suggestions Functions
 */
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

/**
 * Clear NLI Search
 */
function clearNLISearch() {
    const searchInput = document.getElementById('nliSearchInput');
    const clearBtn = document.getElementById('clearBtn');
    const results = document.getElementById('nliResults');
    
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
    
    if (clearBtn) {
        clearBtn.style.display = 'none';
    }
    
    if (results) {
        results.style.display = 'none';
    }
    
    currentQuery = '';
}

/**
 * Close NLI Results
 */
function closeNLIResults() {
    const results = document.getElementById('nliResults');
    if (results) {
        results.style.display = 'none';
    }
}

/**
 * Show notification to user
 */
function showNotification(type, message) {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        document.body.appendChild(notification);
    }
    
    // Set notification style based on type
    if (type === 'error') {
        notification.style.background = '#ef4444';
    } else if (type === 'success') {
        notification.style.background = '#10b981';
    } else {
        notification.style.background = '#3b82f6';
    }
    
    notification.textContent = message;
    
    // Show notification
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Hide notification after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
    }, 4000);
}

/**
 * Update clear button visibility
 */
function updateClearButtonVisibility() {
    const searchInput = document.getElementById('nliSearchInput');
    const clearBtn = document.getElementById('clearBtn');
    
    if (searchInput && clearBtn) {
        if (searchInput.value.trim().length > 0) {
            clearBtn.style.display = 'flex';
        } else {
            clearBtn.style.display = 'none';
        }
    }
}
