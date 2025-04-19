document.addEventListener('DOMContentLoaded', function() {
    initializeImagePreview();
    initializeGenreSelection();
    initializeFormValidation();
    initializeDatePicker();
    handleFormSubmission();
});

function initializeImagePreview() {
    const fileInput = document.querySelector('input[type="file"]');
    const previewContainer = document.getElementById('coverPreview');
    const coverPlaceholder = document.querySelector('.cover-placeholder');
    
    if (!fileInput) return;

    fileInput.addEventListener('change', function(e) {
        const file = this.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.classList.add('cover-preview', 'img-fluid', 'rounded');
            
            if (coverPlaceholder) {
                coverPlaceholder.style.display = 'none';
            }
            
            previewContainer.innerHTML = '';
            previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
}

function initializeGenreSelection() {
    const genreOptions = document.querySelectorAll('.form-check-inline');
    
    genreOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            if (e.target.tagName === 'LABEL') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                e.preventDefault();
            }
        });
    });
}

function initializeFormValidation() {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });
}

function initializeDatePicker() {
    const dateInputs = document.querySelectorAll('.datepicker');
    if (!dateInputs.length) return;

    dateInputs.forEach(input => {
        flatpickr(input, {
            dateFormat: "Y-m-d",
            allowInput: true
        });
    });
}

function handleFormSubmission() {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', function() {
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.querySelector('.submit-text').classList.add('d-none');
        submitBtn.querySelector('.spinner-border').classList.remove('d-none');
        submitBtn.disabled = true;
    });
}
