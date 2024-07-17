function toggleLike(post_id) {
    fetch(`/like/${post_id}`, {
        method: "POST"
    })
    .then(response => response.json())
    .then(result => {
        if (result.stat === 'Success') {
            var likeButton = `
            <button class="like-btn" onclick="toggleLike('${post_id}');">
                Like
                <label class="like-count" id="like-no-${post_id}">${result.likes}</label>
            </button>`;
            
            document.getElementById(`like-btn-${post_id}`).innerHTML = likeButton;
        }
    })
    .catch(error => console.warn('Error occurred:', error));
    return false;
}

function editPost(post_id) {
    var postContent = document.getElementById(`post-text-${post_id}`);
    var originalContent = postContent.innerHTML.trim(); 

    postContent.dataset.originalContent = originalContent;

    postContent.innerHTML = '';  

    var textarea = document.createElement('textarea');
    textarea.value = originalContent;
    textarea.style.width = '100%';
    textarea.setAttribute('id', `edit-${post_id}`);
    postContent.appendChild(textarea);
    postContent.appendChild(document.createElement("br"));

    var submitButton = document.createElement('button');
    submitButton.className = "btn btn-dark";
    submitButton.innerHTML = "Update";
    submitButton.addEventListener('click', function () {
        var editedText = document.getElementById(`edit-${post_id}`).value;
        if (editedText.trim() === '') {
            alert("Content cannot be empty");
            return false;
        }
        fetch(`/edit/${post_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                edited: editedText 
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log("Response received: ", result);
            if (result.stat === "Success") {
                if (typeof result.post !== 'undefined') {
                    console.log("Updating post content: ", result.post);
                    postContent.innerHTML = result.post;  
                } else {
                    console.error("Updated post content is undefined");
                    postContent.innerHTML = originalContent;  
                }
            } else {
                postContent.innerHTML = originalContent;  
                alert("You don't have permission to edit this post");
            }
        })
        .catch(error => {
            console.error("Error updating post:", error);
            postContent.innerHTML = originalContent;  
        });
    });
    postContent.appendChild(submitButton);

    var cancelButton = document.createElement('button');
    cancelButton.className = "btn btn-dark";
    cancelButton.style.marginLeft = '5px';
    cancelButton.innerHTML = "Cancel"; 
    cancelButton.addEventListener('click', function () {
        postContent.innerHTML = postContent.dataset.originalContent;  
    });
    postContent.appendChild(cancelButton);
}

function follow_user(user_id) {
    fetch(`/user/${user_id}/page/1`, {
        method: "POST"
    })
    .then(response => response.json())
    .then(result => {
        if (result.stat === 'Follow' || result.stat === 'Unfollow') {
            
            document.getElementById("follow-btn").innerText = result.stat;

            document.getElementById("follow-data").innerText = `Followers: ${result.followers} | Following: ${result.following}`;
        }
    })
    .catch(error => {
        console.error('Error occurred:', error);
    });
    return false; 
}






