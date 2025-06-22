/* 
 * Emergency Dashboard Scroll Fix
 * ==============================
 * 
 * If your dashboard is still frozen after clicking "Get AI Recommendations",
 * copy and paste this code into your browser's JavaScript console:
 * 
 * 1. Press F12 (or right-click -> Inspect)
 * 2. Go to Console tab
 * 3. Paste this entire block and press Enter
 */

(function() {
    console.log('🚨 Emergency scroll fix starting...');
    
    // 1. Remove any stuck modals
    const stuckModals = document.querySelectorAll('#recommendationsModal, .modal-overlay');
    stuckModals.forEach(modal => {
        console.log('Removing stuck modal:', modal);
        modal.remove();
    });
    
    // 2. Restore page scroll
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.height = '';
    document.documentElement.style.overflow = '';
    
    // 3. Remove any event listeners that might be stuck
    document.removeEventListener('keydown', arguments.callee);
    
    // 4. Log success
    console.log('✅ Page scroll restored!');
    console.log('✅ Stuck modals removed!');
    console.log('✅ You should now be able to scroll normally.');
    
    // 5. Test scroll
    const testScroll = () => {
        const canScroll = document.body.scrollHeight > window.innerHeight;
        const scrollEnabled = document.body.style.overflow !== 'hidden';
        console.log('Can scroll:', canScroll, 'Scroll enabled:', scrollEnabled);
        return canScroll && scrollEnabled;
    };
    
    if (testScroll()) {
        console.log('🎉 Emergency fix successful! Dashboard should be working normally now.');
    } else {
        console.log('⚠️ If you still can\'t scroll, try refreshing the page.');
    }
})();
