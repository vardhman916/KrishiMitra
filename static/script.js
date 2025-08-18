// Loading Screen Management
        document.addEventListener('DOMContentLoaded', function() {
            const loadingScreen = document.getElementById('loadingScreen');
            
            // Hide loading screen after 2 seconds or when page is fully loaded
            window.addEventListener('load', function() {
                setTimeout(() => {
                    loadingScreen.classList.add('hidden');
                    initializeWebsite();
                }, 2000);
            });
        });

        // Initialize all website functionality
        function initializeWebsite() {
            initParticles();
            initScrollAnimations();
            initNavigation();
            initChatInterface();
            initCountUpAnimations();
             initScrollableSections();
        }

        // Particle System
        function initParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 50;

            for (let i = 0; i < particleCount; i++) {
                createParticle(particlesContainer);
            }
        }
        
        function createParticle(container) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random position
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            
            // Random animation delay and duration
            particle.style.animationDelay = Math.random() * 8 + 's';
            particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
            
            container.appendChild(particle);
        }

        // Scroll Animations
        function initScrollAnimations() {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, observerOptions);

            // Observe all elements with animation classes
            document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right').forEach(el => {
                observer.observe(el);
            });
        }

        // Navigation Functionality
        function initNavigation() {
            const navbar = document.getElementById('navbar');
            const mobileToggle = document.getElementById('mobileToggle');
            const mobileMenu = document.getElementById('mobileMenu');
            
            // Navbar scroll effect
            window.addEventListener('scroll', function() {
                if (window.scrollY > 100) {
                    navbar.classList.add('nav-scrolled');
                } else {
                    navbar.classList.remove('nav-scrolled');
                }
            });

            // Mobile menu toggle
            mobileToggle.addEventListener('click', function() {
                mobileMenu.classList.toggle('active');
            });

            // Close mobile menu when clicking on links
            document.querySelectorAll('.mobile-nav-links a').forEach(link => {
                link.addEventListener('click', function() {
                    mobileMenu.classList.remove('active');
                });
            });

            // Smooth scroll for navigation links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        }

//         function initLanguageSelector() {
//     const languageBtn = document.getElementById('languageBtn');
//     const languageOptions = document.getElementById('languageOptions');
//     const selectedLanguageSpan = document.getElementById('selectedLanguage');
//     const languageSelector = document.querySelector('.language-selector');
    
//     let selectedLanguage = 'en-IN'; // Default language
//     let isDropdownOpen = false;

//     // Initially hide language selector (starts in text mode)
//     updateLanguageSelectorVisibility('text');

//     // Toggle dropdown on button click
//     languageBtn.addEventListener('click', function(e) {
//         e.preventDefault();
//         e.stopPropagation();
        
//         // Only allow toggle if in voice mode
//         if (currentMode !== 'voice') {
//             return;
//         }
        
//         toggleDropdown();
//     });

//     // Handle language option selection
//     languageOptions.addEventListener('click', function(e) {
//         const option = e.target.closest('.language-option');
//         if (option) {
//             const langCode = option.getAttribute('data-lang');
//             const langName = option.getAttribute('data-name');
            
//             selectLanguage(langCode, langName, option);
//             closeDropdown();
//         }
//     });

//     // Close dropdown when clicking outside
//     document.addEventListener('click', function(e) {
//         if (!languageBtn.contains(e.target) && !languageOptions.contains(e.target)) {
//             closeDropdown();
//         }
//     });

//     // Close dropdown on escape key
//     document.addEventListener('keydown', function(e) {
//         if (e.key === 'Escape') {
//             closeDropdown();
//         }
//     });

//     function toggleDropdown() {
//         if (isDropdownOpen) {
//             closeDropdown();
//         } else {
//             openDropdown();
//         }
//     }

//     function openDropdown() {
//         if (currentMode !== 'voice') return; // Safety check
        
//         languageOptions.classList.add('show');
//         languageBtn.classList.add('active');
//         isDropdownOpen = true;
        
//         // Animate chevron
//         const chevron = languageBtn.querySelector('.fa-chevron-down');
//         if (chevron) {
//             chevron.style.transform = 'rotate(180deg)';
//         }
//     }

//     function closeDropdown() {
//         languageOptions.classList.remove('show');
//         languageBtn.classList.remove('active');
//         isDropdownOpen = false;
        
//         // Reset chevron
//         const chevron = languageBtn.querySelector('.fa-chevron-down');
//         if (chevron) {
//             chevron.style.transform = 'rotate(0deg)';
//         }
//     }

//     function selectLanguage(langCode, langName, optionElement) {
//         selectedLanguage = langCode;
//         selectedLanguageSpan.textContent = langName;
        
//         // Update selected state in UI
//         document.querySelectorAll('.language-option').forEach(opt => {
//             opt.classList.remove('selected');
//         });
//         optionElement.classList.add('selected');
        
//         // You can add code here to actually change the voice recognition language
//         console.log('Language changed to:', langCode, langName);
        
//         // Update processing status to reflect language change
//         if (currentMode === 'voice') {
//             const processingStatus = document.getElementById('processingStatus');
//             processingStatus.textContent = `Language set to ${langName}. Click microphone to speak.`;
            
//             // Clear message after 3 seconds
//             setTimeout(() => {
//                 if (currentMode === 'voice') {
//                     processingStatus.textContent = 'Click the microphone to start speaking';
//                 }
//             }, 3000);
//         }
//     }

//     // Function to update language selector visibility based on mode
//     function updateLanguageSelectorVisibility(mode) {
//         if (mode === 'voice') {
//             // Show and enable language selector
//             languageSelector.style.display = 'block';
//             languageSelector.style.opacity = '1';
//             languageBtn.style.pointerEvents = 'auto';
//             languageBtn.style.opacity = '1';
//         } else {
//             // Hide and disable language selector
//             languageSelector.style.display = 'none';
//             languageSelector.style.opacity = '0.5';
//             languageBtn.style.pointerEvents = 'none';
//             closeDropdown(); // Close if open
//         }
//     }

//     // Return the function so it can be called from mode switchers
//     return { updateLanguageSelectorVisibility, getSelectedLanguage: () => selectedLanguage };
// }

//         // UPDATED: Enhanced Chat Interface with Voice/Text Mode Controls
//         function initChatInterface() {
//             let languageController; // Add this variable at the top of initChatInterface
//             const chatInput = document.getElementById('chatInput');
//             const submitBtn = document.getElementById('submitBtn'); // NEW: Submit button
//             const centralMicContainer = document.getElementById('centralMicContainer'); // NEW: Central mic container
//             const centralMicIcon = document.getElementById('centralMicIcon'); // NEW: Central mic icon
//             const stopVoiceBtn = document.getElementById('stopVoiceBtn'); // NEW: Stop button
//             const processingStatus = document.getElementById('processingStatus'); // NEW: Processing status
//             const chatResponse = document.getElementById('chatResponse');
//             const responseContent = document.getElementById('responseContent');
//             const textModeBtn = document.getElementById('textMode');
//             const voiceModeBtn = document.getElementById('voiceMode');
//             const inputContainer = document.getElementById('inputContainer'); // NEW: Input container reference
            
//             let currentMode = 'text';
//             let isProcessing = false;
//             let recognition = null; // NEW: Speech recognition instance
//             let isListening = false; // NEW: Listening state
//             let currentUtterance = null; // NEW: Current speech synthesis utterance

//             languageController = initLanguageSelector();
//             // UPDATED: Mode switching with UI changes
//             // UPDATED: Text mode button handler
//         textModeBtn.addEventListener('click', function() {
//             currentMode = 'text';
//             textModeBtn.classList.add('active');
//             voiceModeBtn.classList.remove('active');
            
//             // Show input container, hide central mic
//             inputContainer.style.display = 'flex';
//             inputContainer.classList.remove('voice-mode');
//             centralMicContainer.classList.remove('active');
            
//             chatInput.placeholder = "Ask me about farming, weather, crops, market prices...";
//             processingStatus.textContent = ''; // Clear any processing status
            
//             // Hide/disable language selector
//             languageController.updateLanguageSelectorVisibility('text');
            
//             // Stop any ongoing speech recognition
//             stopVoiceRecognition();
//         });

//         // UPDATED: Voice mode button handler  
//         voiceModeBtn.addEventListener('click', function() {
//             currentMode = 'voice';
//             voiceModeBtn.classList.add('active');
//             textModeBtn.classList.remove('active');
            
//             // Hide input container, show central mic
//             inputContainer.style.display = 'none';
//             inputContainer.classList.add('voice-mode');
//             centralMicContainer.classList.add('active');
            
//             // Show/enable language selector
//             languageController.updateLanguageSelectorVisibility('voice');
            
//             processingStatus.textContent = 'Click the microphone to start speaking';
//         });

//             // UPDATED: Handle text input with submit button
//             chatInput.addEventListener('keypress', function(e) {
//                 if (e.key === 'Enter' && !isProcessing) {
//                     handleUserInput(this.value, 'text');
//                 }
//             });

//             // NEW: Submit button functionality
//             submitBtn.addEventListener('click', function() {
//                 if (!isProcessing && chatInput.value.trim()) {
//                     handleUserInput(chatInput.value, 'text');
//                 }
//             });

//             // Central microphone click handler - calls backend
//             centralMicIcon.addEventListener('click', function() {
//         console.log('🎤 Mic clicked - calling backend!');
        
//         if (!isProcessing) {
//             if (!isListening) {
//                 startBackendVoiceRecognition();
//             } else {
//                 stopBackendVoiceRecognition();
//             }
//         }
// });

//             // NEW: Stop voice button handler
//             stopVoiceBtn.addEventListener('click', function() {
//                 stopBackendVoiceRecognition();
//             });

                        
//             // Backend voice recognition functions
// function startBackendVoiceRecognition() {
//     if (isListening) return;
    
//     isListening = true;
//     centralMicIcon.classList.add('listening');
//     processingStatus.textContent = 'Listening... Speak now';
    
//     // Call your Flask backend
//     fetch('/voice_input', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         }
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success && data.transcript) {
//             processingStatus.textContent = data.transcript;
//             // Process the transcript
//             handleUserInput(data.transcript, 'voice');
//         } else {
//             processingStatus.textContent = data.error || 'No speech detected';
//             setTimeout(() => {
//                 processingStatus.textContent = 'Click the microphone to start speaking';
//             }, 3000);
//         }
//     })
//     .catch(error => {
//         console.error('Voice input error:', error);
//         processingStatus.textContent = 'Voice recognition failed. Please try again.';
//         setTimeout(() => {
//             processingStatus.textContent = 'Click the microphone to start speaking';
//         }, 3000);
//     })
//     .finally(() => {
//         stopBackendVoiceRecognition();
//     });
// }

// function stopBackendVoiceRecognition() {
//     isListening = false;
//     centralMicIcon.classList.remove('listening');
//     if (!isProcessing) {
//         processingStatus.textContent = 'Click the microphone to start speaking';
//     }
// }

//             // UPDATED: Enhanced user input handler
//             async function handleUserInput(input, mode) {
//                 if (!input.trim()) return;
                
//                 isProcessing = true;
//                 if (mode === 'text') {
//                     chatInput.value = '';
//                     submitBtn.style.opacity = '0.5'; // Disable submit button
//                 }
                
//                 // Update UI based on mode
//                 if (mode === 'voice') {
//                     centralMicIcon.classList.add('processing');
//                     centralMicIcon.classList.remove('listening');
//                     processingStatus.textContent = 'Processing your request...';
//                 } else {
//                     showLoadingIndicator();
//                 }
                
//                 try {
//                     const response = await fetch('/process_query', {
//                         method: 'POST',
//                         headers: {
//                             'Content-Type': 'application/json',
//                         },
//                         body: JSON.stringify({
//                             query: input,
//                             mode: mode
//                         })
//                     });
                    
//                     const data = await response.json();
                    
//                     if (data.success) {
//                         showResponse(data.response);
//                     } else {
//                         showResponse("Sorry, I encountered an error processing your request. Please try again.");
//                     }
//                 } catch (error) {
//                     console.error('Error:', error);
//                     showResponse("Sorry, I'm having trouble connecting. Please check your internet connection and try again.");
//                 } finally {
//                     isProcessing = false;
                    
//                     // Reset UI
//                     if (mode === 'text') {
//                         submitBtn.style.opacity = '1'; // Re-enable submit button
//                     } else {
//                         centralMicIcon.classList.remove('processing');
//                         processingStatus.textContent = 'Click the microphone to start speaking';
//                     }
//                 }
//             }

//             function showLoadingIndicator(message = "Processing your query...") {
//     responseContent.innerHTML = `
//         <div style="display: block; text-align: center;">
//             <div class="spinner"></div>
//             <div style="margin-top: 1rem; color: #4caf50; font-size: 1.1rem;">${message}</div>
//         </div>
//     `;
//     chatResponse.classList.add('visible');
// }

//             // UPDATED: Show response with new audio control button
//             function showResponse(response) {
//                 responseContent.innerHTML = response;
//                 chatResponse.classList.add('visible');
//                 // NEW: Add audio control button (play/pause icon)
//                 const audioButton = document.createElement('button');
//                 audioButton.className = 'audio-control-btn';
//                 audioButton.innerHTML = '<i class="fas fa-play"></i>';
//                 audioButton.setAttribute('aria-label', 'Play audio response');
                
//                 audioButton.addEventListener('click', () => {
//                     toggleAudio(response, audioButton);
//                 });
                
//                 responseContent.appendChild(audioButton);
//             }

//             // NEW: Toggle audio playback with play/pause functionality
//             function toggleAudio(text, button) {
//                 if ('speechSynthesis' in window) {
//                     if (currentUtterance && !speechSynthesis.paused) {
//                         // Currently playing - stop it
//                         speechSynthesis.cancel();
//                         button.innerHTML = '<i class="fas fa-play"></i>';
//                         button.classList.remove('playing');
//                         button.setAttribute('aria-label', 'Play audio response');
//                         currentUtterance = null;
//                     } else {
//                         // Start playing
//                         speechSynthesis.cancel(); // Cancel any existing speech
                        
//                         currentUtterance = new SpeechSynthesisUtterance(text);
//                         currentUtterance.rate = 0.8;
//                         currentUtterance.pitch = 1;
//                         currentUtterance.volume = 0.8;
                        
//                         button.innerHTML = '<i class="fas fa-pause"></i>';
//                         button.classList.add('playing');
//                         button.setAttribute('aria-label', 'Stop audio playback');
                        
//                         currentUtterance.onend = () => {
//                             button.innerHTML = '<i class="fas fa-play"></i>';
//                             button.classList.remove('playing');
//                             button.setAttribute('aria-label', 'Play audio response');
//                             currentUtterance = null;
//                         };
                        
//                         currentUtterance.onerror = () => {
//                             button.innerHTML = '<i class="fas fa-play"></i>';
//                             button.classList.remove('playing');
//                             button.setAttribute('aria-label', 'Play audio response');
//                             currentUtterance = null;
//                             console.error('Speech synthesis error');
//                         };
                        
//                         speechSynthesis.speak(currentUtterance);
//                     }
//                 } else {
//                     console.warn('Speech synthesis not supported');
//                     // Could show a message to user that audio is not supported
//                 }
//             }

//             // Backend voice recognition is ready - no setup needed
//             console.log('Backend voice recognition initialized');
//         }

        // Language Dropdown Functionality



        // Count Up Animations
        
        


        // UPDATED: Enhanced Chat Interface with Voice/Text Mode Controls
function initChatInterface() {
    const chatInput = document.getElementById('chatInput');
    const submitBtn = document.getElementById('submitBtn');
    const centralMicContainer = document.getElementById('centralMicContainer');
    const centralMicIcon = document.getElementById('centralMicIcon');
    const stopVoiceBtn = document.getElementById('stopVoiceBtn');
    const processingStatus = document.getElementById('processingStatus');
    const chatResponse = document.getElementById('chatResponse');
    const responseContent = document.getElementById('responseContent');
    const textModeBtn = document.getElementById('textMode');
    const voiceModeBtn = document.getElementById('voiceMode');
    const inputContainer = document.getElementById('inputContainer');
    
    // Language selector elements
    const languageBtn = document.getElementById('languageBtn');
    const languageOptions = document.getElementById('languageOptions');
    const selectedLanguageSpan = document.getElementById('selectedLanguage');
    const languageSelector = document.querySelector('.language-selector');
    
    let currentMode = 'text';
    let isProcessing = false;
    let recognition = null;
    let isListening = false;
    let currentUtterance = null;
    
    // Language selector variables
    let selectedLanguage = 'en-IN';
    let isDropdownOpen = false;

    // Initialize language selector
    initLanguageDropdown();

    function initLanguageDropdown() {
        // Initially hide language selector (starts in text mode)
        updateLanguageSelectorVisibility('text');

        // Toggle dropdown on button click
        if (languageBtn) {
            languageBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Only allow toggle if in voice mode
                if (currentMode !== 'voice') {
                    return;
                }
                
                toggleDropdown();
            });
        }

        // Handle language option selection
        if (languageOptions) {
            languageOptions.addEventListener('click', function(e) {
                const option = e.target.closest('.language-option');
                if (option) {
                    const langCode = option.getAttribute('data-lang');
                    const langName = option.getAttribute('data-name');
                    
                    selectLanguage(langCode, langName, option);
                    closeDropdown();
                }
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (languageBtn && languageOptions && 
                !languageBtn.contains(e.target) && !languageOptions.contains(e.target)) {
                closeDropdown();
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDropdown();
            }
        });
    }

    function toggleDropdown() {
        if (isDropdownOpen) {
            closeDropdown();
        } else {
            openDropdown();
        }
    }

    function openDropdown() {
        if (currentMode !== 'voice') return;
        
        if (languageOptions && languageBtn) {
            languageOptions.classList.add('show');
            languageBtn.classList.add('active');
            isDropdownOpen = true;
            
            // Animate chevron
            const chevron = languageBtn.querySelector('.fa-chevron-down');
            if (chevron) {
                chevron.style.transform = 'rotate(180deg)';
            }
        }
    }

    function closeDropdown() {
        if (languageOptions && languageBtn) {
            languageOptions.classList.remove('show');
            languageBtn.classList.remove('active');
            isDropdownOpen = false;
            
            // Reset chevron
            const chevron = languageBtn.querySelector('.fa-chevron-down');
            if (chevron) {
                chevron.style.transform = 'rotate(0deg)';
            }
        }
    }

    function selectLanguage(langCode, langName, optionElement) {
        selectedLanguage = langCode;
        if (selectedLanguageSpan) {
            selectedLanguageSpan.textContent = langName;
        }
        // Update selected state in UI
        document.querySelectorAll('.language-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        optionElement.classList.add('selected');

        // Send selected language to backend (per user session)
        fetch('/set_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: langCode })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Failed to set language in backend:', data.error);
            }
        })
        .catch(err => {
            console.error('Error sending language to backend:', err);
        });

        console.log('Language changed to:', langCode, langName);
        // Update processing status to reflect language change
        if (currentMode === 'voice' && processingStatus) {
            processingStatus.textContent = `Language set to ${langName}. Click microphone to speak.`;
            // Clear message after 3 seconds
            setTimeout(() => {
                if (currentMode === 'voice') {
                    processingStatus.textContent = 'Click the microphone to start speaking';
                }
            }, 3000);
        }
    }

    function updateLanguageSelectorVisibility(mode) {
        if (languageSelector) {
            if (mode === 'voice') {
                // Show and enable language selector
                languageSelector.style.display = 'block';
                languageSelector.style.opacity = '1';
                if (languageBtn) {
                    languageBtn.style.pointerEvents = 'auto';
                    languageBtn.style.opacity = '1';
                }
            } else {
                // Hide and disable language selector
                languageSelector.style.display = 'none';
                languageSelector.style.opacity = '0.5';
                if (languageBtn) {
                    languageBtn.style.pointerEvents = 'none';
                }
                closeDropdown(); // Close if open
            }
        }
    }

    // Mode switching with language selector control
    textModeBtn.addEventListener('click', function() {
        currentMode = 'text';
        textModeBtn.classList.add('active');
        voiceModeBtn.classList.remove('active');
        
        // Show input container, hide central mic
        inputContainer.style.display = 'flex';
        inputContainer.classList.remove('voice-mode');
        centralMicContainer.classList.remove('active');
        
        chatInput.placeholder = "Ask me about farming, weather, crops, market prices...";
        processingStatus.textContent = '';
        
        // Hide/disable language selector
        updateLanguageSelectorVisibility('text');
        
        // Stop any ongoing speech recognition
        if (typeof stopVoiceRecognition === 'function') {
            stopVoiceRecognition();
        }
    });

    voiceModeBtn.addEventListener('click', function() {
        currentMode = 'voice';
        voiceModeBtn.classList.add('active');
        textModeBtn.classList.remove('active');
        
        // Hide input container, show central mic
        inputContainer.style.display = 'none';
        inputContainer.classList.add('voice-mode');
        centralMicContainer.classList.add('active');
        
        // Show/enable language selector
        updateLanguageSelectorVisibility('voice');
        
        processingStatus.textContent = 'Click the microphone to start speaking';
    });

    // Handle text input with submit button
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !isProcessing) {
            handleUserInput(this.value, 'text');
        }
    });

    // Submit button functionality
    submitBtn.addEventListener('click', function() {
        if (!isProcessing && chatInput.value.trim()) {
            handleUserInput(chatInput.value, 'text');
        }
    });

    // Central microphone click handler - calls backend
    centralMicIcon.addEventListener('click', function() {
        console.log('🎤 Mic clicked - calling backend!');
        
        if (!isProcessing) {
            if (!isListening) {
                startBackendVoiceRecognition();
            } else {
                stopBackendVoiceRecognition();
            }
        }
    });

    // Stop voice button handler
    stopVoiceBtn.addEventListener('click', function() {
        stopBackendVoiceRecognition();
    });

    // Backend voice recognition functions
    function startBackendVoiceRecognition() {
        if (isListening) return;
        
        isListening = true;
        centralMicIcon.classList.add('listening');
        processingStatus.textContent = 'Listening... Speak now';
        
        // Call your Flask backend with selected language
        fetch('/voice_input', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                language: selectedLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.transcript) {
                processingStatus.textContent = data.transcript;
                // Process the transcript
                handleUserInput(data.transcript, 'voice');
            } else {
                processingStatus.textContent = data.error || 'No speech detected';
                setTimeout(() => {
                    processingStatus.textContent = 'Click the microphone to start speaking';
                }, 3000);
            }
        })
        .catch(error => {
            console.error('Voice input error:', error);
            processingStatus.textContent = 'Voice recognition failed. Please try again.';
            setTimeout(() => {
                processingStatus.textContent = 'Click the microphone to start speaking';
            }, 3000);
        })
        .finally(() => {
            stopBackendVoiceRecognition();
        });
    }

    function stopBackendVoiceRecognition() {
        isListening = false;
        centralMicIcon.classList.remove('listening');
        if (!isProcessing) {
            processingStatus.textContent = 'Click the microphone to start speaking';
        }
    }

    // Enhanced user input handler
    async function handleUserInput(input, mode) {
        if (!input.trim()) return;
        
        isProcessing = true;
        if (mode === 'text') {
            chatInput.value = '';
            submitBtn.style.opacity = '0.5';
        }
        
        // Update UI based on mode
        if (mode === 'voice') {
            centralMicIcon.classList.add('processing');
            centralMicIcon.classList.remove('listening');
            processingStatus.textContent = 'Processing your request...';
        } else {
            showLoadingIndicator();
        }
        
        try {
            const response = await fetch('/process_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: input,
                    mode: mode,
                    language: selectedLanguage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showResponse(data.response);
            } else {
                showResponse("Sorry, I encountered an error processing your request. Please try again.");
            }
        } catch (error) {
            console.error('Error:', error);
            showResponse("Sorry, I'm having trouble connecting. Please check your internet connection and try again.");
        } finally {
            isProcessing = false;
            
            // Reset UI
            if (mode === 'text') {
                submitBtn.style.opacity = '1';
            } else {
                centralMicIcon.classList.remove('processing');
                processingStatus.textContent = 'Click the microphone to start speaking';
            }
        }
    }
 
    function showLoadingIndicator(message = "Processing your query...") {
        responseContent.innerHTML = `
            <div style="display: block; text-align: center;">
                <div class="spinner"></div>
                <div style="margin-top: 1rem; color: #4caf50; font-size: 1.1rem;">${message}</div>
            </div>
        `;
        chatResponse.classList.add('visible');
    }

    // Show response with new audio control button
    function showResponse(response) {
        responseContent.innerHTML = response;
        chatResponse.classList.add('visible');
        // Add audio control button (play/pause icon)
        const audioButton = document.createElement('button');
        audioButton.className = 'audio-control-btn';
        audioButton.innerHTML = '<i class="fas fa-play"></i>';
        audioButton.setAttribute('aria-label', 'Play audio response');
        
        audioButton.addEventListener('click', () => {
            toggleAudio(response, audioButton);
        });
        
        responseContent.appendChild(audioButton);
    }

    // Toggle audio playback with play/pause functionality
    function toggleAudio(text, button) {
        if ('speechSynthesis' in window) {
            if (currentUtterance && !speechSynthesis.paused) {
                // Currently playing - stop it
                speechSynthesis.cancel();
                button.innerHTML = '<i class="fas fa-play"></i>';
                button.classList.remove('playing');
                button.setAttribute('aria-label', 'Play audio response');
                currentUtterance = null;
            } else {
                // Start playing
                speechSynthesis.cancel(); // Cancel any existing speech
                
                currentUtterance = new SpeechSynthesisUtterance(text);
                currentUtterance.rate = 0.8;
                currentUtterance.pitch = 1;
                currentUtterance.volume = 0.8;
                
                button.innerHTML = '<i class="fas fa-pause"></i>';
                button.classList.add('playing');
                button.setAttribute('aria-label', 'Stop audio playback');
                
                currentUtterance.onend = () => {
                    button.innerHTML = '<i class="fas fa-play"></i>';
                    button.classList.remove('playing');
                    button.setAttribute('aria-label', 'Play audio response');
                    currentUtterance = null;
                };
                
                currentUtterance.onerror = () => {
                    button.innerHTML = '<i class="fas fa-play"></i>';
                    button.classList.remove('playing');
                    button.setAttribute('aria-label', 'Play audio response');
                    currentUtterance = null;
                    console.error('Speech synthesis error');
                };
                
                speechSynthesis.speak(currentUtterance);
            }
        } else {
            console.warn('Speech synthesis not supported');
        }
    }

    console.log('Chat interface and language selector initialized');
}

        
        function initCountUpAnimations() {
            const counters = document.querySelectorAll('.stat-number');
            const observerOptions = {
                threshold: 0.5
            };

            const counterObserver = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const counter = entry.target;
                        const target = parseInt(counter.getAttribute('data-count'));
                        animateCounter(counter, target);
                        counterObserver.unobserve(counter);
                    }
                });
            }, observerOptions);

            counters.forEach(counter => {
                counterObserver.observe(counter);
            });
        }

        function animateCounter(element, target) {
            let current = 0;
            const increment = target / 100;
            const timer = setInterval(() => {
                current += increment;
                element.textContent = Math.floor(current);
                
                if (current >= target) {
                    element.textContent = target; // FIXED: typo in original code
                    clearInterval(timer);
                }
            }, 20);
        }

        // Initialize individual scrollable sections
        function initScrollableSections() {
            const scrollContainers = document.querySelectorAll('.feature-items-scroll');
            
            scrollContainers.forEach(container => {
                // Add smooth scroll behavior
                container.style.scrollBehavior = 'smooth';
                
                // Add mouse wheel horizontal scrolling
                container.addEventListener('wheel', function(e) {
                    if (e.deltaY !== 0) {
                        e.preventDefault();
                        this.scrollLeft += e.deltaY;
                    }
                });
                
                // Add touch scrolling for mobile
                let isDown = false;
                let startX;
                let scrollLeft;
                
                container.addEventListener('mousedown', (e) => {
                    isDown = true;
                    container.style.cursor = 'grabbing';
                    startX = e.pageX - container.offsetLeft;
                    scrollLeft = container.scrollLeft;
                });
                
                container.addEventListener('mouseleave', () => {
                    isDown = false;
                    container.style.cursor = 'grab';
                });
                
                container.addEventListener('mouseup', () => {
                    isDown = false;
                    container.style.cursor = 'grab';
                });
                
                container.addEventListener('mousemove', (e) => {
                    if (!isDown) return;
                    e.preventDefault();
                    const x = e.pageX - container.offsetLeft;
                    const walk = (x - startX) * 2;
                    container.scrollLeft = scrollLeft - walk;
                });
                
                // Set initial cursor
                container.style.cursor = 'grab';
            });
        }

        // Add some interactive hover effects
        document.addEventListener('DOMContentLoaded', function() {
            // Feature cards hover effect
            document.querySelectorAll('.feature-card, .feature-category').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-10px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });

            // Contact items click effect
            document.querySelectorAll('.contact-item a').forEach(link => {
                link.addEventListener('click', function(e) {
                    // Add ripple effect
                    const ripple = document.createElement('span');
                    ripple.style.cssText = `
                        position: absolute;
                        border-radius: 50%;
                        background: rgba(76, 175, 80, 0.6);
                        transform: scale(0);
                        animation: ripple 0.6s linear;
                        pointer-events: none;
                    `;
                    
                    this.parentElement.appendChild(ripple);
                    setTimeout(() => ripple.remove(), 600);
                });
            });
        });

        // Add CSS animation for ripple effect
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);