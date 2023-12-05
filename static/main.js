 // Sample data - replace this with your actual data fetching logic
 const userData = {
    posts: [
        {
            id: 1,
            content: "Post Content 1",
            image: "post_image_1.jpg",
            date_posted: "2023-01-01 12:34:56",
            comments: [
                { content: "Comment 1", date_posted: "2023-01-02 08:45:30" },
                { content: "Comment 2", date_posted: "2023-01-03 14:22:18" }
            ]
        },
        {
            id: 2,
            content: "Post Content 2",
            image: "post_image_2.jpg",
            date_posted: "2023-01-05 18:12:45",
            comments: [
                { content: "Comment 3", date_posted: "2023-01-07 09:20:10" }
                // Additional comments for post 2
            ]
        }
        // Additional posts
    ]
};

// Function to render posts
function renderPosts() {
    const postsContainer = document.getElementById("posts-container");

    userData.posts.forEach(post => {
        const postElement = document.createElement("div");
        postElement.classList.add("post");

        postElement.innerHTML = `
            <p>${post.content}</p>
            ${post.image ? `<img src="${post.image}" alt="Post Image">` : ''}
            <small>${post.date_posted}</small>
            <ul>
                ${post.comments.map(comment => `<li>${comment.content} - ${comment.date_posted}</li>`).join('')}
            </ul>
            <form onsubmit="addComment(${post.id}); return false;">
                <label for="comment">Add Comment:</label>
                <input type="text" name="comment" required>
                <button type="submit">Post Comment</button>
            </form>
            <hr>
        `;

        postsContainer.appendChild(postElement);
    });
}

// Function to add a comment (dummy function for illustration)
function addComment(postId) {
    const commentInput = document.querySelector(`[name="comment"]`);
    const commentContent = commentInput.value;

    // Dummy logic to add the comment to the respective post
    console.log(`Adding comment "${commentContent}" to post ${postId}`);
    commentInput.value = '';  // Clear the input after adding the comment

    // You can implement the actual logic to send the comment to the server here
}

// Render posts on page load
renderPosts();

async function signup() {
    // console.log(document.getElementById('signupUsername').value)
    const username = document.getElementById('inputUsername').value;
    const password = document.getElementById('inputPassword').value;
    console.log(password)
    // return;
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Signup successful:', data);

        // Optionally, you can redirect the user or perform other actions
    } catch (error) {
        console.error('Error during signup:', error.message);
        // Handle errors or display a message to the user
    }
}

function login(){
    const username = document.getElementById('inputUsername').value;
    const password = document.getElementById('inputPassword').value;

    // Send a POST request to the server
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Login successful', data);
        // Optionally, you can redirect the user to a new page or perform other actions
    })
    .catch(error => {
        console.error('Error during signup:', error.message);
        // Handle errors or display a message to the user
    });
}