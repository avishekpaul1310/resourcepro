/**
 * Guided Tour System for ResourcePro Demo
 * Implements the tour scenarios described in Curated Demo Scenario.md
 */

class GuidedTour {
    constructor(config) {
        this.config = config;
        this.currentStep = 0;
        this.isActive = false;
        this.overlay = null;
        this.tourBox = null;
        
        this.init();
    }
    
    init() {
        this.createTourElements();
        this.bindEvents();
        
        // Check if tour should auto-start
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('tour') === 'true') {
            setTimeout(() => this.start(), 1000); // Start after page loads
        }
    }
    
    createTourElements() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tour-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 9998;
            display: none;
            transition: opacity 0.3s ease;
        `;
        
        // Create tour box
        this.tourBox = document.createElement('div');
        this.tourBox.className = 'tour-box';
        this.tourBox.style.cssText = `
            position: fixed;
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 400px;
            z-index: 9999;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            display: none;
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.tourBox);
    }
    
    bindEvents() {
        // Close on overlay click
        this.overlay.addEventListener('click', () => this.end());
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) {
                this.end();
            }
        });
    }
    
    start() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.currentStep = 0;
        
        // Show overlay
        this.overlay.style.display = 'block';
        setTimeout(() => {
            this.overlay.style.opacity = '1';
        }, 10);
        
        // Show first step
        this.showStep(0);
        
        // Track tour start
        this.trackEvent('tour_started', {
            tour_name: this.config.name,
            tour_type: this.config.type || 'executive'
        });
    }
    
    showStep(stepIndex) {
        if (stepIndex >= this.config.steps.length) {
            this.end();
            return;
        }
        
        const step = this.config.steps[stepIndex];
        this.currentStep = stepIndex;
        
        // Highlight target element
        this.highlightElement(step.selector);
        
        // Position and show tour box
        this.positionTourBox(step);
        this.updateTourContent(step);
        
        // Show tour box
        this.tourBox.style.display = 'block';
        
        // Execute step action if any
        if (step.action) {
            this.executeStepAction(step.action);
        }
        
        // Track step view
        this.trackEvent('tour_step_viewed', {
            step_index: stepIndex,
            step_title: step.title
        });
    }
    
    highlightElement(selector) {
        // Remove previous highlights
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
        
        if (selector) {
            const element = document.querySelector(selector);
            if (element) {
                element.classList.add('tour-highlight');
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Add highlight styles
                const highlightStyle = document.createElement('style');
                highlightStyle.textContent = `
                    .tour-highlight {
                        position: relative;
                        z-index: 9997;
                        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.8) !important;
                        border-radius: 8px !important;
                        transition: all 0.3s ease !important;
                    }
                `;
                
                if (!document.querySelector('#tour-highlight-styles')) {
                    highlightStyle.id = 'tour-highlight-styles';
                    document.head.appendChild(highlightStyle);
                }
            }
        }
    }
    
    positionTourBox(step) {
        const element = step.selector ? document.querySelector(step.selector) : null;
        
        if (element) {
            const rect = element.getBoundingClientRect();
            const boxRect = this.tourBox.getBoundingClientRect();
            
            let top = rect.bottom + 20;
            let left = rect.left;
            
            // Adjust if too close to edges
            if (left + 400 > window.innerWidth) {
                left = window.innerWidth - 420;
            }
            if (top + boxRect.height > window.innerHeight) {
                top = rect.top - boxRect.height - 20;
            }
            
            this.tourBox.style.top = `${Math.max(20, top)}px`;
            this.tourBox.style.left = `${Math.max(20, left)}px`;
        } else {
            // Center on screen if no target element
            this.tourBox.style.top = '50%';
            this.tourBox.style.left = '50%';
            this.tourBox.style.transform = 'translate(-50%, -50%)';
        }
    }
    
    updateTourContent(step) {
        const totalSteps = this.config.steps.length;
        const currentNum = this.currentStep + 1;
        
        let highlights = '';
        if (step.highlights) {
            highlights = `
                <ul class="tour-highlights">
                    ${step.highlights.map(highlight => `<li>✅ ${highlight}</li>`).join('')}
                </ul>
            `;
        }
        
        let metrics = '';
        if (step.metrics) {
            metrics = `
                <div class="tour-metrics">
                    ${Object.entries(step.metrics).map(([key, value]) => 
                        `<div class="metric"><strong>${key}:</strong> ${value}</div>`
                    ).join('')}
                </div>
            `;
        }
        
        this.tourBox.innerHTML = `
            <div class="tour-header">
                <h4>${step.title}</h4>
                <span class="tour-progress">${currentNum}/${totalSteps}</span>
            </div>
            
            <div class="tour-content">
                <p>${step.content}</p>
                ${highlights}
                ${metrics}
            </div>
            
            <div class="tour-footer">
                <div class="tour-duration">
                    ⏱️ ${step.duration || 30}s
                </div>
                <div class="tour-controls">
                    ${currentNum > 1 ? '<button class="btn-tour-prev">Previous</button>' : ''}
                    ${currentNum < totalSteps ? '<button class="btn-tour-next">Next</button>' : '<button class="btn-tour-finish">Finish Tour</button>'}
                    <button class="btn-tour-skip">Skip Tour</button>
                </div>
            </div>
        `;
        
        // Bind control events
        this.bindTourControls();
        
        // Add tour styles
        this.addTourStyles();
    }
    
    bindTourControls() {
        const nextBtn = this.tourBox.querySelector('.btn-tour-next');
        const prevBtn = this.tourBox.querySelector('.btn-tour-prev');
        const finishBtn = this.tourBox.querySelector('.btn-tour-finish');
        const skipBtn = this.tourBox.querySelector('.btn-tour-skip');
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevStep());
        }
        if (finishBtn) {
            finishBtn.addEventListener('click', () => this.end());
        }
        if (skipBtn) {
            skipBtn.addEventListener('click', () => this.end());
        }
    }
    
    addTourStyles() {
        if (document.querySelector('#tour-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'tour-styles';
        styles.textContent = `
            .tour-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .tour-header h4 {
                margin: 0;
                color: #1f2937;
                font-size: 18px;
                font-weight: 600;
            }
            
            .tour-progress {
                background: #3b82f6;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }
            
            .tour-content p {
                color: #4b5563;
                line-height: 1.5;
                margin-bottom: 12px;
            }
            
            .tour-highlights {
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 6px;
                padding: 12px;
                margin: 12px 0;
                list-style: none;
            }
            
            .tour-highlights li {
                color: #0c4a6e;
                margin: 4px 0;
                font-size: 14px;
            }
            
            .tour-metrics {
                background: #f8fafc;
                border-radius: 6px;
                padding: 12px;
                margin: 12px 0;
            }
            
            .tour-metrics .metric {
                margin: 4px 0;
                font-size: 14px;
                color: #374151;
            }
            
            .tour-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 16px;
                padding-top: 12px;
                border-top: 1px solid #e5e7eb;
            }
            
            .tour-duration {
                font-size: 12px;
                color: #6b7280;
                font-style: italic;
            }
            
            .tour-controls {
                display: flex;
                gap: 8px;
            }
            
            .tour-controls button {
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .btn-tour-next, .btn-tour-finish {
                background: #3b82f6;
                color: white;
            }
            
            .btn-tour-next:hover, .btn-tour-finish:hover {
                background: #2563eb;
            }
            
            .btn-tour-prev {
                background: #f3f4f6;
                color: #374151;
            }
            
            .btn-tour-prev:hover {
                background: #e5e7eb;
            }
            
            .btn-tour-skip {
                background: transparent;
                color: #6b7280;
                text-decoration: underline;
            }
            
            .btn-tour-skip:hover {
                color: #374151;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    nextStep() {
        this.showStep(this.currentStep + 1);
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    executeStepAction(action) {
        switch (action) {
            case 'highlight_ai_modal':
                // Trigger AI recommendations modal if available
                const aiButton = document.querySelector('[data-action="ai-suggestions"]');
                if (aiButton) {
                    aiButton.scrollIntoView({ behavior: 'smooth' });
                }
                break;
                
            case 'auto_scroll_forecast':
                // Scroll through forecast data
                const forecastSection = document.querySelector('.forecasting-section');
                if (forecastSection) {
                    forecastSection.scrollIntoView({ behavior: 'smooth' });
                }
                break;
        }
    }
    
    end() {
        this.isActive = false;
        
        // Hide elements
        this.overlay.style.opacity = '0';
        this.tourBox.style.display = 'none';
        
        setTimeout(() => {
            this.overlay.style.display = 'none';
        }, 300);
        
        // Remove highlights
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
        
        // Track tour completion
        this.trackEvent('tour_completed', {
            tour_name: this.config.name,
            steps_completed: this.currentStep + 1,
            total_steps: this.config.steps.length
        });
    }
    
    trackEvent(eventName, data) {
        // Send analytics event (implement based on your analytics setup)
        if (window.gtag) {
            window.gtag('event', eventName, data);
        }
        
        // Console log for development
        console.log(`Tour Event: ${eventName}`, data);
    }
}

// Global initialization function
window.initializeGuidedTour = function(config) {
    return new GuidedTour(config);
};

// Auto-start tour based on URL parameters
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const tourType = urlParams.get('tour');
    
    if (tourType) {
        // Load tour configuration (this would come from the server)
        fetch(`/demo/tour-config/${tourType}/`)
            .then(response => response.json())
            .then(config => {
                if (config.success) {
                    window.guidedTour = new GuidedTour(config.tour_config);
                    setTimeout(() => window.guidedTour.start(), 1000);
                }
            })
            .catch(error => {
                console.error('Failed to load tour configuration:', error);
            });
    }
});
