function voteReview(reviewId, isHelpful) {
    fetch(`/review/${reviewId}/vote/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ is_helpful: isHelpful })
    });
}

function updateReadingProgress(listItemId, progress) {
    fetch(`/reading-list/item/${listItemId}/progress/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ progress: progress })
    });
}

function followUser(userId) {
    fetch(`/user/${userId}/follow/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
}

// CSRF token helper
function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
