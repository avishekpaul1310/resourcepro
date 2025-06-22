/**
 * Voice Search Debugging Script
 * Run this in the browser console to test voice search functionality
 */

console.log('=== Voice Search Debug Test ===');

// Check if elements exist
console.log('1. Checking DOM elements...');
const searchInput = document.getElementById('nliSearchInput');
const voiceBtn = document.getElementById('voiceBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsContainer = document.getElementById('nliResults');

console.log('Search Input:', searchInput ? '✅ Found' : '❌ Missing');
console.log('Voice Button:', voiceBtn ? '✅ Found' : '❌ Missing');
console.log('Clear Button:', clearBtn ? '✅ Found' : '❌ Missing');
console.log('Results Container:', resultsContainer ? '✅ Found' : '❌ Missing');

// Check if event listeners are attached
console.log('\n2. Checking event listeners...');
if (voiceBtn) {
    console.log('Voice button exists, checking click handler...');
    voiceBtn.click();
} else {
    console.log('❌ Voice button not found - cannot test click handler');
}

// Check Speech Recognition support
console.log('\n3. Checking browser support...');
const speechSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
console.log('Speech Recognition Support:', speechSupported ? '✅ Supported' : '❌ Not supported');

if (speechSupported) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    console.log('Speech Recognition constructor:', SpeechRecognition);
}

// Check AI functions
console.log('\n4. Checking AI functions...');
console.log('toggleVoiceSearch function:', typeof toggleVoiceSearch);
console.log('processNLIQuery function:', typeof processNLIQuery);
console.log('initializeNLISearch function:', typeof initializeNLISearch);

// Test basic search functionality
console.log('\n5. Testing search functionality...');
if (searchInput) {
    searchInput.value = 'test query';
    console.log('Set test query in search input');
    
    // Update clear button visibility
    if (typeof updateClearButtonVisibility === 'function') {
        updateClearButtonVisibility();
        console.log('Called updateClearButtonVisibility');
    }
    
    if (clearBtn) {
        console.log('Clear button display:', clearBtn.style.display);
    }
}

// Check CSRF token
console.log('\n6. Checking CSRF token...');
const csrfToken = getCookie ? getCookie('csrftoken') : 'getCookie function not found';
console.log('CSRF Token:', csrfToken ? '✅ Available' : '❌ Missing');

console.log('\n=== Voice Search Debug Test Complete ===');
