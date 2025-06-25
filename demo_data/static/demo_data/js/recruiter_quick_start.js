/**
 * Recruiter Quick Start System
 * Provides one-click demo loading and guided tour for recruiters
 */

class RecruiterQuickStart {
    constructor() {
        this.isLoading = false;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkDemoStatus();
    }
    
    bindEvents() {
        // Quick start button in showcase
        const quickStartBtn = document.getElementById('quickStartBtn');
        if (quickStartBtn) {
            quickStartBtn.addEventListener('click', () => this.quickStart());
        }
        
        // Demo helper buttons
        const loadDemoBtn = document.getElementById('loadDemoDataBtn');
        if (loadDemoBtn) {
            loadDemoBtn.addEventListener('click', () => this.loadDemoData());
        }
        
        const startTourBtn = document.getElementById('startTourBtn');
        if (startTourBtn) {
            startTourBtn.addEventListener('click', () => this.startGuidedTour());
        }
    }
    
    async checkDemoStatus() {
        try {
            const response = await fetch('/demo-data/api/status/');
            const data = await response.json();
            
            if (data.success) {
                this.updateDemoStatus(data.data);
            }
        } catch (error) {
            console.error('Error checking demo status:', error);
        }
    }
    
    updateDemoStatus(status) {
        // Update status indicator in demo helper
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        
        if (statusIndicator && statusText) {
            if (status.has_data) {
                statusIndicator.className = 'status-indicator status-loaded';
                statusText.textContent = `Demo data loaded (${status.counts.Resources} resources, ${status.counts.Projects} projects)`;
            } else {
                statusIndicator.className = 'status-indicator status-empty';
                statusText.textContent = 'No demo data loaded';
            }
        }
        
        // Update metrics in showcase page
        this.updateShowcaseMetrics(status.counts);
    }
    
    updateShowcaseMetrics(counts) {
        const elements = {
            'resourceCount': counts.Resources || 0,
            'projectCount': counts.Projects || 0,
            'taskCount': counts.Tasks || 0
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Update utilization rate (calculated)
        const utilizationElement = document.getElementById('utilizationRate');
        if (utilizationElement && counts.Resources > 0) {
            utilizationElement.textContent = '78%'; // Mock realistic utilization
        }
    }
    
    async quickStart() {
        if (this.isLoading) return;
        
        const btn = document.getElementById('quickStartBtn');
        if (!btn) return;
        
        const originalText = btn.innerHTML;
        this.isLoading = true;
        
        try {
            // Step 1: Load demo data
            btn.innerHTML = '⏳ Loading enterprise demo data...';
            btn.disabled = true;
            
            const loadResult = await this.loadDemoData(false);
            
            if (!loadResult.success) {
                throw new Error(loadResult.error || 'Failed to load demo data');
            }
            
            // Step 2: Show success and prepare for tour
            btn.innerHTML = '✅ Demo loaded! Starting guided tour...';
            
            // Wait a moment for user to see success
            await this.delay(1500);
            
            // Step 3: Start the guided tour
            this.startExecutiveTour();
            
        } catch (error) {
            console.error('Quick start error:', error);
            btn.innerHTML = '❌ Error - Please try again';
            btn.disabled = false;
            
            // Show user-friendly error
            this.showNotification('Failed to start demo. Please try again or contact support.', 'error');
            
            // Reset button after a moment
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                this.isLoading = false;
            }, 3000);
        }
    }
    
    async loadDemoData(showNotification = true) {
        try {
            const response = await fetch('/demo-data/api/load-scenario/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    scenario: 'techcorp_enterprise'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (showNotification) {
                    this.showNotification('Demo data loaded successfully!', 'success');
                }
                
                // Update status
                await this.checkDemoStatus();
            }
            
            return result;
            
        } catch (error) {
            console.error('Error loading demo data:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    startGuidedTour() {
        // Check which page we're on and start appropriate tour
        const path = window.location.pathname;
        
        if (path.includes('/dashboard/')) {
            this.startDashboardTour();
        } else if (path.includes('/allocation/')) {
            this.startAllocationTour();
        } else if (path.includes('/analytics/')) {
            this.startAnalyticsTour();
        } else {
            // Default: navigate to dashboard and start tour
            window.location.href = '/dashboard/?tour=true';
        }
    }
      startExecutiveTour() {
        // Executive summary tour for recruiters
        const tour = new GuidedTour({
            name: 'Executive Demo',
            type: 'executive',
            steps: [
                {
                    title: 'Welcome to ResourcePro',
                    content: `
                        <div class="tour-welcome">
                            <h3>🎯 Executive Demo Tour</h3>
                            <p>This 3-minute tour showcases ResourcePro's key features that make it perfect for enterprise resource management.</p>
                            <p><strong>What you'll see:</strong></p>
                            <ul>
                                <li>Real-time resource utilization dashboard</li>
                                <li>AI-powered recommendations</li>
                                <li>Predictive analytics and forecasting</li>
                                <li>Smart resource allocation</li>
                            </ul>
                            <p><em>At the end, you'll get a completion summary perfect for sharing with your team!</em></p>
                        </div>
                    `,
                    position: 'center',
                    showNext: true,
                    nextAction: () => {
                        window.location.href = '/dashboard/?tour=continue';
                    }
                },
                // Additional steps will be handled on specific pages
            ],
            onComplete: () => {
                // Redirect to completion summary
                window.location.href = '/demo-data/completion/';
            }
        });
        
        tour.start();
    }
    
    startDashboardTour() {
        // Dashboard-specific tour
        const tour = new GuidedTour({
            name: 'Dashboard Tour',
            type: 'dashboard',
            steps: [
                {
                    title: 'Resource Utilization Overview',
                    target: '.utilization-overview, .dashboard-metrics',
                    content: `
                        <h4>📊 Real-Time Metrics</h4>
                        <p>Get instant visibility into your team's capacity and workload.</p>
                        <ul>
                            <li><strong>Green:</strong> Healthy utilization (70-90%)</li>
                            <li><strong>Yellow:</strong> High utilization (90-100%)</li>
                            <li><strong>Red:</strong> Overallocated (>100%)</li>
                        </ul>
                    `,
                    position: 'bottom'
                },
                {
                    title: 'AI-Powered Insights',
                    target: '.ai-analyst-widget, .ai-briefing',
                    content: `
                        <h4>🤖 AI Daily Briefing</h4>
                        <p>Our AI analyzes your data and provides actionable insights:</p>
                        <ul>
                            <li>Resource bottlenecks and conflicts</li>
                            <li>Project risk assessments</li>
                            <li>Optimization recommendations</li>
                        </ul>
                        <p><em>Try clicking on the recommendations!</em></p>
                    `,
                    position: 'top'
                }
            ]
        });
        
        tour.start();
    }
    
    startAllocationTour() {
        // Allocation board tour
        console.log('Starting allocation tour...');
    }
    
    startAnalyticsTour() {
        // Analytics dashboard tour
        console.log('Starting analytics tour...');
    }
    
    // Utility methods
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    showNotification(message, type = 'info') {
        // Create or update notification
        let notification = document.getElementById('demo-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'demo-notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                max-width: 400px;
                transition: all 0.3s ease;
                transform: translateX(100%);
            `;
            document.body.appendChild(notification);
        }
        
        // Set type-specific styling
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            info: '#3B82F6',
            warning: '#F59E0B'
        };
        
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;
        
        // Animate in
        notification.style.transform = 'translateX(0)';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.recruiterQuickStart = new RecruiterQuickStart();
});

// Export for global access
window.RecruiterQuickStart = RecruiterQuickStart;
