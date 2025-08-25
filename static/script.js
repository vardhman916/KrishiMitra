// Loading Screen Management

// Loading Screen Management
document.addEventListener('DOMContentLoaded', function() {
    const loadingScreen = document.getElementById('loadingScreen');

    // Hide loading screen after 2 seconds or when page is fully loaded
    window.addEventListener('load', function() {
        setTimeout(() => {
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
            }
            // Always call initializeWebsite after hiding loading screen
            try {
                initializeWebsite();
            } catch (e) {
                console.error('Error initializing website:', e);
            }
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

    const imageModeBtn = document.getElementById('imageMode');
    const imageModeContainer = document.getElementById('imageModeContainer');
    const photoLibraryBtn = document.getElementById('photoLibraryBtn');
    const takePhotoBtn = document.getElementById('takePhotoBtn');
    const chooseFileBtn = document.getElementById('chooseFileBtn');
    const uploadDriveBtn = document.getElementById('uploadDriveBtn');
    const fileInput = document.getElementById('fileInput');
    const cameraInput = document.getElementById('cameraInput');
    const uploadStatus = document.getElementById('uploadStatus');
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
                // Hide and disable language selector for text/image modes
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

    // ADDED: Image Mode switching
    imageModeBtn.addEventListener('click', function() {
        currentMode = 'image';
        imageModeBtn.classList.add('active');
        textModeBtn.classList.remove('active');
        voiceModeBtn.classList.remove('active');
        
        // Hide other containers, show image container
        inputContainer.style.display = 'none';
        centralMicContainer.classList.remove('active');
        imageModeContainer.classList.add('active');
        
        // Hide/disable language selector (only for voice mode)
        updateLanguageSelectorVisibility('image');
        
        processingStatus.textContent = '';
        
        // Stop any ongoing speech recognition
        if (typeof stopVoiceRecognition === 'function') {
            stopVoiceRecognition();
        }
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


// ADDED: Image Mode Functionality
    initImageMode();

// Initialize Memory Sidebar
    initMemorySidebar();
    initAuthSystem();
    
    console.log('Chat interface, language selector, and memory sidebar initialized');
}

// ADDED: Image Mode Initialization
function initImageMode() {
    const photoLibraryBtn = document.getElementById('photoLibraryBtn');
    const takePhotoBtn = document.getElementById('takePhotoBtn');
    const chooseFileBtn = document.getElementById('chooseFileBtn');
    const uploadDriveBtn = document.getElementById('uploadDriveBtn');
    const fileInput = document.getElementById('fileInput');
    const cameraInput = document.getElementById('cameraInput');
    const uploadStatus = document.getElementById('uploadStatus');

    // Photo Library - opens file picker for images
    photoLibraryBtn.addEventListener('click', function() {
        fileInput.accept = 'image/*';
        fileInput.click();
    });

    // Take Photo - opens camera
    takePhotoBtn.addEventListener('click', function() {
        openCameraModal();
    });

    // Choose File - opens file picker for all supported files
    chooseFileBtn.addEventListener('click', function() {
        fileInput.accept = 'image/*,.pdf';
        fileInput.click();
    });

    // Upload from Drive - placeholder for Google Drive integration
    uploadDriveBtn.addEventListener('click', function() {
        alert('Google Drive integration will be added in the next version.');
    });

    // Handle file selection from file input
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });

    // Handle file selection from camera input
    cameraInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });

    function handleFileUpload(file) {
        // Show uploading status
        uploadStatus.innerHTML = `
            <div class="upload-spinner"></div>
            <span>Uploading ${file.type.includes('pdf') ? 'PDF' : 'image'}...</span>
        `;
        uploadStatus.className = 'upload-status uploading';

        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_type', file.type);

        // Simulate upload process (replace with actual backend call)
        setTimeout(() => {
            // For now, show placeholder success message
            uploadStatus.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>Image successfully uploaded. Pest/Disease detection will be added in the next version.</span>
            `;
            uploadStatus.className = 'upload-status success';

            // Clear status after 5 seconds
            setTimeout(() => {
                uploadStatus.innerHTML = '';
                uploadStatus.className = 'upload-status';
            }, 5000);

            // Reset file inputs
            fileInput.value = '';
            cameraInput.value = '';
        }, 2000);

        // Uncomment and modify this when backend is ready:
        /*
        fetch('/upload_image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadStatus.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <span>${data.message || 'Image uploaded successfully!'}</span>
                `;
                uploadStatus.className = 'upload-status success';
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <span>Upload failed: ${error.message}</span>
            `;
            uploadStatus.className = 'upload-status error';
        })
        .finally(() => {
            // Clear status after 5 seconds
            setTimeout(() => {
                uploadStatus.innerHTML = '';
                uploadStatus.className = 'upload-status';
            }, 5000);
            
            // Reset file inputs
            fileInput.value = '';
            cameraInput.value = '';
        });
        */
    }

    // Add this line at the end with error handling:
    try {
        initCameraControls();
    } catch (error) {
        console.log('Camera controls initialization failed:', error);
        // Continue without camera functionality
    }
    console.log('Image mode and camera initialized');
}

// Camera functionality - Add after initImageMode()
function openCameraModal() {
    const cameraModal = document.getElementById('cameraModal');
    const cameraVideo = document.getElementById('cameraVideo');
    
    cameraModal.classList.add('active');
    cameraVideo.style.display = 'block'; // Ensure video is visible

    // Request camera access
    navigator.mediaDevices.getUserMedia({
        video: true // Use default camera
    })
    .then(stream => {
        window.currentCameraStream = stream;
        cameraVideo.srcObject = stream;
        cameraVideo.play();
        console.log('Camera stream started:', stream);
    })
    .catch(error => {
        console.error('Camera access error:', error);
        alert('Could not access camera. Please allow camera permissions and try again.');
        cameraModal.classList.remove('active');
    });
}

function closeCameraModal() {
    const cameraModal = document.getElementById('cameraModal');
    const cameraVideo = document.getElementById('cameraVideo');
    
    // Stop camera stream
    if (window.currentCameraStream) {
        window.currentCameraStream.getTracks().forEach(track => track.stop());
        window.currentCameraStream = null;
    }
    
    // Hide modal
    cameraModal.classList.remove('active');
    cameraVideo.srcObject = null;
}

function capturePhoto() {
    const cameraVideo = document.getElementById('cameraVideo');
    const cameraCanvas = document.getElementById('cameraCanvas');
    
    // Set canvas size to match video
    cameraCanvas.width = cameraVideo.videoWidth;
    cameraCanvas.height = cameraVideo.videoHeight;
    
    // Draw video frame to canvas
    const context = cameraCanvas.getContext('2d');
    context.drawImage(cameraVideo, 0, 0);
    
    // Convert to blob and create file
    cameraCanvas.toBlob(function(blob) {
        const file = new File([blob], `camera-photo-${Date.now()}.jpg`, { type: 'image/jpeg' });
        
        // Close camera
        closeCameraModal();
        
        // Process the captured file
        handleFileUpload(file);
        
    }, 'image/jpeg', 0.9);
}

// Initialize camera controls - Add to your initImageMode() function
function initCameraControls() {
    const captureBtn = document.getElementById('captureBtn');
    const closeCameraBtn = document.getElementById('closeCameraBtn');
    const cameraModal = document.getElementById('cameraModal');
    
    // Capture button
    captureBtn.addEventListener('click', capturePhoto);
    
    // Close button
    closeCameraBtn.addEventListener('click', closeCameraModal);
    
    // Close when clicking outside modal
    cameraModal.addEventListener('click', function(e) {
        if (e.target === cameraModal) {
            closeCameraModal();
        }
    });
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && cameraModal.classList.contains('active')) {
            closeCameraModal();
        }
    });
}

// Add this entire function after the initChatInterface() function:
function initMemorySidebar() {
    const memoryToggle = document.getElementById('memoryToggle');
    const memorySidebar = document.getElementById('memorySidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const closeSidebar = document.getElementById('closeSidebar');
    const addMemoryBtn = document.getElementById('addMemoryBtn');
    const clearMemoryBtn = document.getElementById('clearMemoryBtn');
    const addMemoryModal = document.getElementById('addMemoryModal');
    const closeModal = document.getElementById('closeModal');
    const cancelModal = document.getElementById('cancelModal');
    const saveMemory = document.getElementById('saveMemory');
    const memoryInput = document.getElementById('memoryInput');
    
    // Toggle sidebar
    memoryToggle.addEventListener('click', () => {
        memorySidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        loadMemoryData();
    });
    
    // Close sidebar
    function closeSidebarFunc() {
        memorySidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    }
    
    closeSidebar.addEventListener('click', closeSidebarFunc);
    sidebarOverlay.addEventListener('click', closeSidebarFunc);
    
    // Add memory modal
    addMemoryBtn.addEventListener('click', () => {
        addMemoryModal.classList.add('active');
    });
    
    // Close modal
    function closeModalFunc() {
        addMemoryModal.classList.remove('active');
        memoryInput.value = '';
    }
    
    closeModal.addEventListener('click', closeModalFunc);
    cancelModal.addEventListener('click', closeModalFunc);
    
    // Save memory
    saveMemory.addEventListener('click', () => {
        const memoryText = memoryInput.value.trim();
        if (memoryText) {
            addToMemory(memoryText);
            closeModalFunc();
        }
    });
    
    // Clear memory
    clearMemoryBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all memory? This cannot be undone.')) {
            clearAllMemory();
        }
    });
    
    // Load memory data from backend
    function loadMemoryData() {
        fetch('/get_memory')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateMemoryDisplay(data.memory);
                }
            })
            .catch(error => {
                console.error('Error loading memory:', error);
            });
    }
    
    // Add memory to backend
    function addToMemory(memoryText) {
        fetch('/add_memory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ memory: memoryText })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadMemoryData(); // Refresh memory display
            } else {
                alert('Failed to add memory: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error adding memory:', error);
            alert('Error adding memory');
        });
    }
    
    // Clear all memory
    function clearAllMemory() {
        fetch('/clear_memory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadMemoryData(); // Refresh memory display
            } else {
                alert('Failed to clear memory: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error clearing memory:', error);
            alert('Error clearing memory');
        });
    }
    
    // Update memory display
    function updateMemoryDisplay(memoryData) {
        const memoryFacts = document.getElementById('memoryFacts');
        const conversationHistory = document.getElementById('conversationHistory');
        
        // Update facts
        if (memoryData.facts && memoryData.facts.length > 0) {
            memoryFacts.innerHTML = memoryData.facts.map(fact => 
                `<div class="memory-item">${fact}</div>`
            ).join('');
        } else {
            memoryFacts.innerHTML = '<p class="no-memory">No information remembered yet</p>';
        }
        
        // Update conversation history
        if (memoryData.conversation && memoryData.conversation.length > 0) {
            conversationHistory.innerHTML = memoryData.conversation.map(item => 
                `<div class="history-item ${item.type}">
                    <div class="history-label">${item.type === 'user' ? 'You' : 'KrishiMitra'}</div>
                    <div class="history-text">${item.content}</div>
                </div>`
            ).join('');
        } else {
            conversationHistory.innerHTML = '<p class="no-history">No conversation history</p>';
        }
    }
}


function initAuthSystem() {
    const userAvatar = document.getElementById('userAvatar');
    const userMenu = document.getElementById('userMenu');
    const loginOption = document.getElementById('loginOption');
    const signupOption = document.getElementById('signupOption');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    
    // Load states and districts data
    let statesData = {};
    loadStatesData();
    
    // Avatar dropdown toggle
    userAvatar.addEventListener('click', (e) => {
        e.stopPropagation();
        userMenu.classList.toggle('active');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
        userMenu.classList.remove('active');
    });
    
    // Login option
    loginOption.addEventListener('click', () => {
        userMenu.classList.remove('active');
        loginModal.classList.add('active');
    });
    
    // Signup option
    signupOption.addEventListener('click', () => {
        userMenu.classList.remove('active');
        signupModal.classList.add('active');
    });
    
    // Close modals
    document.getElementById('closeLoginModal').addEventListener('click', () => {
        loginModal.classList.remove('active');
    });
    
    document.getElementById('closeSignupModal').addEventListener('click', () => {
        signupModal.classList.remove('active');
    });
    
    document.getElementById('cancelLogin').addEventListener('click', () => {
        loginModal.classList.remove('active');
    });
    
    document.getElementById('cancelSignup').addEventListener('click', () => {
        signupModal.classList.remove('active');
    });
    
    document.getElementById('cancelSignupMobile').addEventListener('click', () => {
        signupModal.classList.remove('active');
    });
    
    // Signup option selection
    document.querySelectorAll('.signup-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.signup-option').forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            
            const type = option.getAttribute('data-type');
            document.querySelectorAll('.signup-form').forEach(form => form.classList.remove('active'));
            
            if (type === 'email') {
                document.getElementById('emailSignupForm').classList.add('active');
            } else {
                document.getElementById('mobileSignupForm').classList.add('active');
            }
        });
    });
    
    // State-District handling
    function setupStateDistrictDropdowns(stateId, districtId) {
        const stateSelect = document.getElementById(stateId);
        const districtSelect = document.getElementById(districtId);
        
        stateSelect.addEventListener('change', () => {
            const selectedState = stateSelect.value;
            districtSelect.innerHTML = '<option value="">Select District</option>';
            
            if (selectedState && statesData[selectedState]) {
                statesData[selectedState].forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtSelect.appendChild(option);
                });
            }
        });
    }
    
    setupStateDistrictDropdowns('farmerState', 'farmerDistrict');
    setupStateDistrictDropdowns('farmerStateMobile', 'farmerDistrictMobile');
    
    // Load states data
    function loadStatesData() {
        // You can replace this with actual fetch to your states-and-districts.json
        fetch('/static/states-and-districts.json')
        .then(response => response.json())
        .then(data => {
         // Convert your JSON structure to the expected format
        statesData = {};
         data.states.forEach(stateObj => {
        statesData[stateObj.state] = stateObj.districts;
         });
   
            populateStates();
        })
        .catch(error => {
            console.error('Error loading states data:', error);
            // Fallback data
            statesData = {
                "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari"],
                "Karnataka": ["Bangalore Urban", "Belgaum", "Bellary"],
                "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore"]
            };
            populateStates();
        });
    }
    
    function populateStates() {
        const stateSelects = ['farmerState', 'farmerStateMobile'];
        stateSelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            Object.keys(statesData).forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                select.appendChild(option);
            });
        });
    }
    
    // Form submissions
    document.getElementById('loginForm').addEventListener('submit', (e) => {
        e.preventDefault();
        // Handle login logic here
        console.log('Login submitted');
        loginModal.classList.remove('active');
    });
    
    document.getElementById('emailSignupForm').addEventListener('submit', (e) => {
        e.preventDefault();
        // Handle email signup logic here
        console.log('Email signup submitted');
        signupModal.classList.remove('active');
    });
    
    document.getElementById('mobileSignupForm').addEventListener('submit', (e) => {
        e.preventDefault();
        // Handle mobile signup logic here
        console.log('Mobile signup submitted');
        signupModal.classList.remove('active');
    });
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