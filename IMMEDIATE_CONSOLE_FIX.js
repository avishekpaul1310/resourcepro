/* 
 * IMMEDIATE FIX - Paste this in browser console NOW
 * =================================================
 * 
 * Copy this entire block and paste it in your console to fix the stuck scroll immediately:
 */

// Immediate scroll restoration
console.log('🔧 Running immediate scroll fix...');

// 1. Force restore scroll
document.body.style.overflow = '';
document.body.style.position = '';
document.body.style.height = '';
document.documentElement.style.overflow = '';

// 2. Remove any stuck modals
document.querySelectorAll('#recommendationsModal, .modal-overlay').forEach(modal => {
    console.log('Removing modal:', modal);
    modal.remove();
});

// 3. Clear any intervals that might be interfering
const highestId = window.setTimeout(() => {}, 0);
for (let i = 0; i < highestId; i++) {
    window.clearTimeout(i);
    window.clearInterval(i);
}

// 4. Force a scroll test
window.scrollTo(0, 0);
setTimeout(() => window.scrollTo(0, 100), 100);
setTimeout(() => window.scrollTo(0, 0), 200);

console.log('✅ Immediate fix applied! Try scrolling now.');

// 5. Add a temporary better click handler
document.addEventListener('click', function(e) {
    if (e.target.closest('.btn-recommendations')) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Recommendations button clicked - showing simple alert instead');
        alert('AI Recommendations feature is temporarily disabled to prevent scroll issues. Please refresh the page to restore functionality.');
        return false;
    }
}, true);
