// The Like Function

function likedPost(postId) {
    // Get the like button and like count element for the specific post
    const likeButton = document.getElementById(`likeButton-${postId}`);
    const likeCountElement = document.getElementById(`likes-count-${postId}`);

    console.log('Like Button:', likeButton);
    console.log('Like Count Element:', likeCountElement);

    if (!likeButton || !likeCountElement) {
        console.error('Element not found');
        return;
    }

    // Send an AJAX request to like/unlike the post
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            post_id: postId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the like count
            likeCountElement.textContent = data.likes_count;

            // Change the heart icon based on the liked status
            if (data.liked) {
                likeButton.innerHTML = '<i class="fas fa-heart text-danger"></i> Liked';
            } else {
                likeButton.innerHTML = '<i class="far fa-heart"></i> Like';
            }
        } else {
            console.error('Failed to like/unlike the post');
        }
    });
}


    // JavaScript to toggle comment form visibility
    function toggleCommentForm(postId) {
        const commentForm = document.getElementById(`comment-form-${postId}`);
        commentForm.style.display = commentForm.style.display === 'none' ? 'block' : 'none';
    }


    // JavaScript to toggle reply form visibility
    function toggleReplyForm(commentId) {
        const replyForm = document.getElementById(`reply-form-${commentId}`);
        replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
    }


// Follow/Unfollow Function
    function followerUser(username) {
        fetch(`/follow/${username}/`)
            .then(response => response.json())
            .then(data => {
                location.reload(); 
            });
    }

// Media Preview Function

    document.addEventListener('DOMContentLoaded', () => {
        const previewItems = document.querySelectorAll('.media-preview-item');
    
        previewItems.forEach((item) => {
            item.addEventListener('click', () => {
                const modal = document.createElement('div');
                modal.style.position = 'fixed';
                modal.style.top = '0';
                modal.style.left = '0';
                modal.style.width = '100%';
                modal.style.height = '100%';
                modal.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                modal.style.display = 'flex';
                modal.style.justifyContent = 'center';
                modal.style.alignItems = 'center';
                modal.style.zIndex = '1000';
    
                const clonedElement = item.cloneNode(true);
                clonedElement.style.maxWidth = '90%';
                clonedElement.style.maxHeight = '90%';
    
                // Remove controls from video preview
                if (clonedElement.tagName === 'VIDEO') {
                    clonedElement.removeAttribute('controls');
                    clonedElement.setAttribute('autoplay', true);
                    clonedElement.setAttribute('loop', true);
                }
    
                modal.appendChild(clonedElement);
    
                // Close the modal on click
                modal.addEventListener('click', () => {
                    document.body.removeChild(modal);
                });
    
                document.body.appendChild(modal);
            });
        });
    });

// Notification Function
    document.addEventListener("DOMContentLoaded", function() {
        // Attach click event to each notification item
        const notificationItems = document.querySelectorAll('.notification-item');
        
        notificationItems.forEach(item => {
            item.addEventListener('click', function() {
                const notificationId = this.dataset.notificationId;

                fetch(`/notifications/mark_read/${notificationId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Mark the specific notification as read by changing its style
                            this.classList.add('read'); // Optionally add a 'read' class to indicate it
                            
                            // Update notification count dynamically
                            updateNotificationCount();
                        }
                    });
            });
        });
        
        // Function to update the notification count
        function updateNotificationCount() {
            fetch('/notifications/unread/')
                .then(response => response.json())
                .then(data => {
                    const countElement = document.getElementById('notification-count');
                    if (data.unread_count > 0) {
                        countElement.style.display = 'inline-block';
                        countElement.textContent = data.unread_count;
                    } else {
                        countElement.style.display = 'none';
                    }
                });
        }
    });

      // Function to fetch and display unread notification count
    function fetchUnreadNotifications() {
        fetch('/notifications/unread/')
            .then(response => response.json())
            .then(data => {
                const countElement = document.getElementById('notification-count');
                if (countElement) { // Check if the element exists
                    if (data.unread_count > 0) {
                        countElement.style.display = 'inline-block';
                        countElement.textContent = data.unread_count;
                    } else {
                        countElement.style.display = 'none';
                    }
                } else {
                    console.warn('Notification count element not found');
                }
            })
            .catch(error => {
                console.error('Error fetching unread notifications:', error);
            });
    }
    

    // Call the function to fetch unread notifications on page load
    document.addEventListener("DOMContentLoaded", function() {
        fetchUnreadNotifications();
    });



    
    