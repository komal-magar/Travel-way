/**
 * Travel & Tourism Portal - JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // ==================== NAVBAR SCROLL EFFECT ====================
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
            } else {
                navbar.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }
        });
    }

    // ==================== FORM VALIDATION ====================
    
    // Login Form Validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username');
            const password = document.getElementById('password');
            let isValid = true;

            if (!username.value.trim()) {
                showError(username, 'Username is required');
                isValid = false;
            } else {
                removeError(username);
            }

            if (!password.value) {
                showError(password, 'Password is required');
                isValid = false;
            } else {
                removeError(password);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Register Form Validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username');
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirmPassword');
            let isValid = true;

            // Username validation
            if (!username.value.trim()) {
                showError(username, 'Username is required');
                isValid = false;
            } else if (username.value.trim().length < 3) {
                showError(username, 'Username must be at least 3 characters');
                isValid = false;
            } else {
                removeError(username);
            }

            // Email validation
            if (!email.value.trim()) {
                showError(email, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            } else {
                removeError(email);
            }

            // Password validation
            if (!password.value) {
                showError(password, 'Password is required');
                isValid = false;
            } else if (password.value.length < 6) {
                showError(password, 'Password must be at least 6 characters');
                isValid = false;
            } else {
                removeError(password);
            }

            // Confirm password validation
            if (!confirmPassword.value) {
                showError(confirmPassword, 'Please confirm your password');
                isValid = false;
            } else if (password.value !== confirmPassword.value) {
                showError(confirmPassword, 'Passwords do not match');
                isValid = false;
            } else {
                removeError(confirmPassword);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Booking Form Validation
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            const date = document.getElementById('date');
            const persons = document.getElementById('persons');
            let isValid = true;

            if (!date.value) {
                showError(date, 'Please select a date');
                isValid = false;
            } else {
                const selectedDate = new Date(date.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate < today) {
                    showError(date, 'Please select a future date');
                    isValid = false;
                } else {
                    removeError(date);
                }
            }

            if (!persons.value) {
                showError(persons, 'Please enter number of persons');
                isValid = false;
            } else if (persons.value < 1) {
                showError(persons, 'At least 1 person is required');
                isValid = false;
            } else if (persons.value > 20) {
                showError(persons, 'Maximum 20 persons allowed');
                isValid = false;
            } else {
                removeError(persons);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Calculate total price dynamically
        const personsInput = document.getElementById('persons');
        const pricePerPerson = document.getElementById('pricePerPerson');
        const totalPrice = document.getElementById('totalPrice');
        
        if (personsInput && pricePerPerson && totalPrice) {
            const price = parseFloat(pricePerPerson.value);
            personsInput.addEventListener('input', function() {
                const persons = parseInt(this.value) || 0;
                const total = price * persons;
                totalPrice.textContent = '$' + total.toFixed(2);
            });
        }
    }

    // Contact Form Validation
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const message = document.getElementById('message');
            let isValid = true;

            if (!name.value.trim()) {
                showError(name, 'Name is required');
                isValid = false;
            } else {
                removeError(name);
            }

            if (!email.value.trim()) {
                showError(email, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            } else {
                removeError(email);
            }

            if (!message.value.trim()) {
                showError(message, 'Message is required');
                isValid = false;
            } else if (message.value.trim().length < 10) {
                showError(message, 'Message must be at least 10 characters');
                isValid = false;
            } else {
                removeError(message);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Destination Form Validation
    const destinationForm = document.getElementById('destinationForm');
    if (destinationForm) {
        destinationForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name');
            const location = document.getElementById('location');
            const description = document.getElementById('description');
            const price = document.getElementById('price');
            let isValid = true;

            if (!name.value.trim()) {
                showError(name, 'Destination name is required');
                isValid = false;
            } else {
                removeError(name);
            }

            if (!location.value.trim()) {
                showError(location, 'Location is required');
                isValid = false;
            } else {
                removeError(location);
            }

            if (!description.value.trim()) {
                showError(description, 'Description is required');
                isValid = false;
            } else {
                removeError(description);
            }

            if (!price.value) {
                showError(price, 'Price is required');
                isValid = false;
            } else if (price.value <= 0) {
                showError(price, 'Price must be greater than 0');
                isValid = false;
            } else {
                removeError(price);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // ==================== SEARCH FUNCTIONALITY ====================
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        const searchInput = document.getElementById('searchInput');
        const clearSearch = document.getElementById('clearSearch');
        
        if (searchInput && searchInput.value) {
            if (clearSearch) {
                clearSearch.style.display = 'inline-block';
            }
        }

        if (searchInput) {
            searchInput.addEventListener('input', function() {
                if (clearSearch) {
                    clearSearch.style.display = this.value ? 'inline-block' : 'none';
                }
            });
        }

        if (clearSearch) {
            clearSearch.addEventListener('click', function() {
                searchInput.value = '';
                this.style.display = 'none';
                window.location.href = window.location.pathname;
            });
        }
    }

    // ==================== PACKAGE FILTER ====================
    const packageFilter = document.getElementById('packageFilter');
    if (packageFilter) {
        packageFilter.addEventListener('change', function() {
            const url = new URL(window.location.href);
            url.searchParams.set('type', this.value);
            window.location.href = url.toString();
        });
    }

    // ==================== CONFIRM DELETE ====================
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // ==================== BOOKING DELETE CONFIRM ====================
    const deleteBookingBtns = document.querySelectorAll('.delete-booking');
    deleteBookingBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this booking?')) {
                e.preventDefault();
            }
        });
    });

    // ==================== AUTO HIDE ALERTS ====================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // ==================== SMOOTH SCROLL ====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ==================== IMAGE ERROR HANDLING ====================
    const images = document.querySelectorAll('.card-img-top, .about-img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.src = 'https://via.placeholder.com/400x300?text=No+Image';
        });
    });

    // ==================== PHONE NUMBER FORMAT ====================
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = value;
                } else if (value.length <= 6) {
                    value = value.slice(0, 3) + '-' + value.slice(3);
                } else {
                    value = value.slice(0, 3) + '-' + value.slice(3, 6) + '-' + value.slice(6, 10);
                }
            }
            e.target.value = value;
        });
    });

    // ==================== DATE PICKER MIN DATE ====================
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
    });
});

// ==================== HELPER FUNCTIONS ====================

function showError(input, message) {
    const formGroup = input.closest('.form-group') || input.parentElement;
    let errorElement = formGroup.querySelector('.error-message');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message text-danger small mt-1';
        formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    input.classList.add('is-invalid');
}

function removeError(input) {
    const formGroup = input.closest('.form-group') || input.parentElement;
    const errorElement = formGroup.querySelector('.error-message');
    
    if (errorElement) {
        errorElement.remove();
    }
    
    input.classList.remove('is-invalid');
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function isValidPhone(phone) {
    const re = /^\d{3}-\d{3}-\d{4}$/;
    return re.test(phone);
}

// ==================== NUMBER FORMATTER ====================
function formatCurrency(amount) {
    return '$' + amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// ==================== DATE FORMATTER ====================
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showError,
        removeError,
        isValidEmail,
        isValidPhone,
        formatCurrency,
        formatDate
    };
}
