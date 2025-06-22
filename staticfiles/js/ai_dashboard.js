/**
 * AI Dashboard Features JavaScript - Simplified Version
 * Handles AI-powered dashboard analyst and recommendation system
 */

// Global state
let currentQuery = '';
let nliTimeout = null;

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

/**
 * Initialize all AI features
 */
function initializeAIFeatures() {
    // Safety check: ensure page scroll is enabled on initialization
    restorePageScroll();
    
    initializeAIAnalyst();
    initializeNLISearch();
    
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
    const nliInput = document.getElementById('nli-input');
    if (!nliInput) return;
    
    nliInput.addEventListener('input', handleNLIInput);
    nliInput.addEventListener('keydown', handleNLIKeydown);
}

function handleNLIInput(e) {
    const query = e.target.value.trim();
    currentQuery = query;
    
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
    
    fetch('/dashboard/api/nli-query/', {
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
    const resultsContainer = document.getElementById('nli-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = '<div class="nli-loading"><i class="fas fa-spinner fa-spin"></i> Processing...</div>';
    }
}

function displayNLIResults(data) {
    const resultsContainer = document.getElementById('nli-results');
    if (!resultsContainer) return;
    
    if (data.error) {
        resultsContainer.innerHTML = `<div class="nli-error">Error: ${data.error}</div>`;
        return;
    }
    
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        <div class="nli-response">
            <div class="nli-answer">${data.response_text || 'No response available'}</div>
            ${data.response_data ? `
                <div class="nli-data">
                    <pre>${JSON.stringify(data.response_data, null, 2)}</pre>
                </div>
            ` : ''}
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
