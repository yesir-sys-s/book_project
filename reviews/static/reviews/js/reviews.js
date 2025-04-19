// Star rating functionality
function initializeRating() {
    const ratingInputs = document.querySelectorAll('.rating-input input');
    ratingInputs.forEach(input => {
        input.addEventListener('change', function() {
            const stars = this.closest('.rating-input').querySelectorAll('.star');
            stars.forEach((star, index) => {
                star.classList.toggle('active', index < this.value);
            });
        });
    });
}

// Form validation
function initializeFormValidation() {
    const form = document.querySelector('form.needs-validation');
    if (!form) return;

    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeRating();
    initializeFormValidation();
});
