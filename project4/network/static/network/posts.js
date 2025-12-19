document.addEventListener("DOMContentLoaded", () => {
    posts = document.querySelectorAll(".post");
    posts.forEach(post => {
        editor = post.querySelector("button.edit-button");
        if (editor != null) {
            editor.addEventListener("click", () => edit_post(post));
        }

        like_button = post.querySelector("p.like-button");
        if (like_button != null) {
            like_button.addEventListener("click", () => like_post(post));
        }
    });
})

function like_post(post) {
    const postId = post.querySelector("input.post-id").value;
    fetch(`/posts/${postId}`, {
        method: "PUT",
        body: JSON.stringify({
            "like": true,
        })
    })
    .then(response => response.json())
    .then(updatedPost => {
        // Print post
        console.log(updatedPost);
        post.querySelector("span.likes-count").innerHTML = updatedPost.likes;
    });
}

function edit_post(post) {
    // Get id of post, content and user url 
    const postId = post.querySelector("input.post-id").value;
    let content = post.querySelector("#post-content").innerHTML;
    let url = post.querySelector("h4");
    console.log(content);
    // Save innerhtml of post
    let post_original = post.innerHTML;

    post.innerHTML = `
    <form class="mb-1">
        <h4>${url.innerHTML}</h4>
        {% csrf_token %}
        <textarea id="new-content" rows="2" class="form form-control mb-2">${content.trim()}</textarea>
        <button id="save-edit" type="button" class="btn btn-primary">Save</button>
        <button id="cancel-edit" type="button" class="btn btn-secondary">Cancel</button>
    </form>`;

    // Enable save edits button only if there is text in the textarea
    post.querySelector('#new-content').onkeyup = () => {
        if (post.querySelector('#new-content').value.length > 0)
            post.querySelector('#save-edit').disabled = false;
        else
            post.querySelector('#save-edit').disabled = true;
    };

    // If user presses the cancel edit button, set innerhtml back to the original value
    post.querySelector("#cancel-edit").addEventListener("click", () => {
        post.innerHTML = post_original;
        post.querySelector(".edit-button").addEventListener("click", () => edit_post(post));
    });

    // If user saves edits, load original post html but change the content as well
    post.querySelector("#save-edit").addEventListener("click", () => {
        newContent = post.querySelector("#new-content").value.trim();
        console.log(newContent);
        fetch(`/posts/${postId}`, {
            method: "PUT",
            body: JSON.stringify({
                content: newContent,
            })
        })
        .then(result => {
            // Print result
            console.log(result);
            // Revert to original post content but change the post content
            post.innerHTML = post_original;
            post.querySelector("#post-content").innerHTML = newContent;
            post.querySelector(".edit-button").addEventListener("click", () => edit_post(post));
        });
    });
}