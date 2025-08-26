// Authentication UI Handler
function initAuthUI() {
    const userAvatar = document.getElementById('userAvatar');
    const userMenu = document.getElementById('userMenu');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    const loginOption = document.getElementById('loginOption');
    const signupOption = document.getElementById('signupOption');
    
    // Forms
    const loginForm = document.getElementById('loginForm');
    const emailSignupForm = document.getElementById('emailSignupForm');
    const mobileSignupForm = document.getElementById('mobileSignupForm');
    
    // Close buttons
    const closeLoginModal = document.getElementById('closeLoginModal');
    const closeSignupModal = document.getElementById('closeSignupModal');
    const cancelLogin = document.getElementById('cancelLogin');
    const cancelSignup = document.getElementById('cancelSignup');
    const cancelSignupMobile = document.getElementById('cancelSignupMobile');

    // Initialize dropdown behavior for user avatar
    if (userAvatar) {
        userAvatar.addEventListener('click', (e) => {
            e.stopPropagation();
            userMenu.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userAvatar.contains(e.target)) {
                userMenu.classList.remove('active');
            }
        });
    }

    // Login option click handler
    if (loginOption) {
        loginOption.addEventListener('click', () => {
            userMenu.classList.remove('active');
            signupModal.classList.remove('active');
            loginModal.classList.add('active');
        });
    }

    // Signup option click handler
    if (signupOption) {
        signupOption.addEventListener('click', () => {
            userMenu.classList.remove('active');
            loginModal.classList.remove('active');
            signupModal.classList.add('active');
            showSignupForm('email'); // Default to email signup
        });
    }

    // Modal close handlers
    if (closeLoginModal) {
        closeLoginModal.addEventListener('click', () => loginModal.classList.remove('active'));
    }
    if (closeSignupModal) {
        closeSignupModal.addEventListener('click', () => signupModal.classList.remove('active'));
    }
    if (cancelLogin) {
        cancelLogin.addEventListener('click', () => loginModal.classList.remove('active'));
    }
    if (cancelSignup) {
        cancelSignup.addEventListener('click', () => signupModal.classList.remove('active'));
    }
    if (cancelSignupMobile) {
        cancelSignupMobile.addEventListener('click', () => signupModal.classList.remove('active'));
    }

    // Handle signup options
    const signupOptions = document.querySelectorAll('.signup-option');
    signupOptions.forEach(option => {
        option.addEventListener('click', () => {
            const type = option.getAttribute('data-type');
            showSignupForm(type);
            
            // Update selected state
            signupOptions.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
        });
    });

    // Initialize state and district dropdowns
    initializeLocationDropdowns();

    // Form submission handlers
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (emailSignupForm) {
        emailSignupForm.addEventListener('submit', handleEmailSignup);
    }
    if (mobileSignupForm) {
        mobileSignupForm.addEventListener('submit', handleMobileSignup);
    }

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) {
            loginModal.classList.remove('active');
        }
        if (e.target === signupModal) {
            signupModal.classList.remove('active');
        }
    });

    // Close modals with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            loginModal.classList.remove('active');
            signupModal.classList.remove('active');
            userMenu.classList.remove('active');
        }
    });
}

// Show appropriate signup form
function showSignupForm(type) {
    const emailForm = document.getElementById('emailSignupForm');
    const mobileForm = document.getElementById('mobileSignupForm');

    if (type === 'email') {
        emailForm.style.display = 'block';
        mobileForm.style.display = 'none';
    } else {
        emailForm.style.display = 'none';
        mobileForm.style.display = 'block';
    }
}

// Initialize state and district dropdowns
function initializeLocationDropdowns() {
    const states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ];

    // Helper function to populate state dropdowns
    function populateStates(selectElement) {
        states.forEach(state => {
            const option = document.createElement('option');
            option.value = state.toLowerCase().replace(/\s+/g, '-');
            option.textContent = state;
            selectElement.appendChild(option);
        });
    }

    // Populate both state dropdowns
    const stateSelects = ['farmerState', 'farmerStateMobile'].map(id => document.getElementById(id));
    stateSelects.forEach(select => {
        if (select) {
            populateStates(select);
            // Add district population on state change
            select.addEventListener('change', function() {
                const districtId = this.id.includes('Mobile') ? 'farmerDistrictMobile' : 'farmerDistrict';
                populateDistricts(this.value, districtId);
            });
        }
    });
}

// Populate districts based on selected state
function populateDistricts(state, districtSelectId) {
    const districtSelect = document.getElementById(districtSelectId);
    if (!districtSelect) return;

    // Clear existing options
    districtSelect.innerHTML = '<option value="">Select District</option>';

    // This would typically fetch districts from an API
    // For now, adding some example districts
    const districts = [
        "District 1", "District 2", "District 3", "District 4", "District 5"
    ];

    districts.forEach(district => {
        const option = document.createElement('option');
        option.value = district.toLowerCase().replace(/\s+/g, '-');
        option.textContent = district;
        districtSelect.appendChild(option);
    });
}

// Form submission handlers
async function handleLogin(e) {
    e.preventDefault();
    const emailMobile = document.getElementById('loginEmailMobile').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ emailMobile, password }),
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('loginModal').classList.remove('active');
            updateUserUI(data.user);
        } else {
            alert(data.message || 'Login failed. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred. Please try again.');
    }
}

async function handleEmailSignup(e) {
    e.preventDefault();
    const formData = {
        email: document.getElementById('signupEmail').value,
        password: document.getElementById('signupPassword').value,
        name: document.getElementById('farmerName').value,
        state: document.getElementById('farmerState').value,
        district: document.getElementById('farmerDistrict').value,
        farmingType: document.getElementById('farmingType').value
    };

    try {
        const response = await fetch('/api/signup/email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('signupModal').classList.remove('active');
            document.getElementById('loginModal').classList.add('active');
            alert('Signup successful! Please log in.');
        } else {
            alert(data.message || 'Signup failed. Please try again.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('An error occurred. Please try again.');
    }
}

async function handleMobileSignup(e) {
    e.preventDefault();
    const formData = {
        mobile: document.getElementById('signupMobile').value,
        name: document.getElementById('farmerNameMobile').value,
        state: document.getElementById('farmerStateMobile').value,
        district: document.getElementById('farmerDistrictMobile').value
    };

    try {
        const response = await fetch('/api/signup/mobile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        if (data.success) {
            alert('OTP sent! Please verify your mobile number.');
            showOTPVerification(formData.mobile);
        } else {
            alert(data.message || 'Failed to send OTP. Please try again.');
        }
    } catch (error) {
        console.error('Mobile signup error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Update UI after successful login
function updateUserUI(user) {
    const userAvatar = document.getElementById('userAvatar');
    const userMenu = document.getElementById('userMenu');

    if (userAvatar && userMenu) {
        // Update avatar
        userAvatar.innerHTML = user.profilePicture 
            ? `<img src="${user.profilePicture}" alt="${user.name}">`
            : `<div class="user-initial">${user.name.charAt(0).toUpperCase()}</div>`;

        // Update menu items
        userMenu.innerHTML = `
            <div class="user-menu-item">
                <span class="user-name">${user.name}</span>
            </div>
            <div class="user-menu-item">
                <a href="#" onclick="handleLogout()">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        `;
    }
}

// Handle logout
async function handleLogout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
        });

        const data = await response.json();
        if (data.success) {
            window.location.reload();
        } else {
            alert('Logout failed. Please try again.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Initialize authentication UI when the document is ready
document.addEventListener('DOMContentLoaded', initAuthUI);
