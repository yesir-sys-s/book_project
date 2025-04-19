document.addEventListener('DOMContentLoaded', function() {
    // Initialize file upload handling
    const fileInput = document.getElementById('cover-image-input');
    const coverPreview = document.getElementById('coverPreview');
    const coverPlaceholder = document.querySelector('.cover-placeholder');

    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.classList.add('cover-preview', 'img-fluid', 'rounded');
                    
                    if (coverPlaceholder) {
                        coverPlaceholder.style.display = 'none';
                    }
                    
                    coverPreview.innerHTML = '';
                    coverPreview.appendChild(img);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Initialize flatpickr for date input
    flatpickr(".datepicker", {
        dateFormat: "Y-m-d",
        allowInput: true
    });

    // Form validation and submission handling
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.querySelector('.submit-text').classList.add('d-none');
            submitBtn.querySelector('.spinner-border').classList.remove('d-none');
            submitBtn.disabled = true;
        });
    }
});
