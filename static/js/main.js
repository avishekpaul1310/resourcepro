/**
 * ResourcePro - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Close alert messages when the close button is clicked
    const closeButtons = document.querySelectorAll('.alert .close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    setTimeout(() => {
        alerts.forEach(alert => {
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s';
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.parentElement.removeChild(alert);
                    }
                }, 500);
            }
        });
    }, 5000);
    
    // Toggle mobile menu
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Handle form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const requiredFields = form.querySelectorAll('[required]');
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    // Mark field as invalid
                    field.classList.add('border-red-500');
                    
                    // Add error message if it doesn't exist
                    const errorEl = field.parentElement.querySelector('.error');
                    if (!errorEl) {
                        const error = document.createElement('div');
                        error.className = 'error';
                        error.textContent = 'This field is required';
                        field.parentElement.appendChild(error);
                    }
                } else {
                    // Mark field as valid
                    field.classList.remove('border-red-500');
                    
                    // Remove error message if it exists
                    const errorEl = field.parentElement.querySelector('.error');
                    if (errorEl) {
                        errorEl.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});