// Main JavaScript functions for Task Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
    
    // Fix modal flickering issue
    const taskDetailsModals = document.querySelectorAll('.task-details-modal');
    taskDetailsModals.forEach(modal => {
        // Override Bootstrap's fade transition
        modal.style.transition = 'none';
        
        // Disable animations for smoother rendering
        modal.classList.add('no-transition');
        
        // Listen for modal events to manage rendering
        modal.addEventListener('show.bs.modal', function(event) {
            // Force hardware acceleration
            this.style.transform = 'translateZ(0)';
            this.style.willChange = 'transform';
            this.style.backfaceVisibility = 'hidden';
            
            // Override Bootstrap's default opacity animation
            document.body.classList.add('modal-open');
            
            // Prevent default Bootstrap animation
            event.preventDefault();
            this.style.display = 'block';
            this.style.opacity = '1';
            
            // Add modal-open class to body without any transition
            setTimeout(() => {
                this.classList.add('show');
                document.querySelector('.modal-backdrop')?.classList.add('no-transition');
            }, 10);
        });
        
        // Handle modal close event
        modal.addEventListener('hide.bs.modal', function(event) {
            // Prevent default hiding animation
            event.preventDefault();
            
            // Immediately hide without animation
            this.classList.remove('show');
            this.style.display = 'none';
            
            // Remove backdrop
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            
            // Remove body classes if no other modals are open
            if (!document.querySelector('.modal.show')) {
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        });
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('.file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileListElement = document.getElementById(this.dataset.fileList);
            if (!fileListElement) return;
            
            fileListElement.innerHTML = '';
            
            if (this.files.length > 0) {
                for (let i = 0; i < this.files.length; i++) {
                    const file = this.files[i];
                    const fileSize = formatFileSize(file.size);
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${fileSize}</div>
                    `;
                    fileListElement.appendChild(fileItem);
                }
            }
        });
    });
    
    // Password strength check
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('password-strength');
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('keyup', checkPasswordStrength);
    }
    
    // Password confirmation check
    const confirmPasswordInput = document.getElementById('confirm-password');
    const passwordMatch = document.getElementById('password-match');
    if (confirmPasswordInput && passwordMatch) {
        confirmPasswordInput.addEventListener('keyup', checkPasswordMatch);
    }
});

// Format file size into readable format
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Check password strength
function checkPasswordStrength() {
    const password = document.getElementById('password').value;
    const strengthElement = document.getElementById('password-strength');
    
    // Password strength criteria
    const hasLowerCase = /[a-z]/.test(password);
    const hasUpperCase = /[A-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const isLongEnough = password.length >= 8;
    
    let strength = 0;
    if (hasLowerCase) strength++;
    if (hasUpperCase) strength++;
    if (hasNumber) strength++;
    if (hasSpecialChar) strength++;
    if (isLongEnough) strength++;
    
    // Update UI based on strength
    if (password === '') {
        strengthElement.innerHTML = '';
        strengthElement.className = '';
    } else if (strength < 2) {
        strengthElement.innerHTML = 'Weak';
        strengthElement.className = 'text-danger';
    } else if (strength < 4) {
        strengthElement.innerHTML = 'Moderate';
        strengthElement.className = 'text-warning';
    } else {
        strengthElement.innerHTML = 'Strong';
        strengthElement.className = 'text-success';
    }
}

// Check if passwords match
function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const matchElement = document.getElementById('password-match');
    
    if (confirmPassword === '') {
        matchElement.innerHTML = '';
        matchElement.className = '';
    } else if (password === confirmPassword) {
        matchElement.innerHTML = 'Passwords match';
        matchElement.className = 'text-success';
    } else {
        matchElement.innerHTML = 'Passwords do not match';
        matchElement.className = 'text-danger';
    }
}