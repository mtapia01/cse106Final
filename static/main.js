// Next steps: Work on feed. Add a sign out button and create post maybe at the top of the page as a nav bar?

window.onload = renderPost();
async function renderPost(){
    try {
        // Submit the form
        const response = await fetch('/dashboardFeed', {
            method: 'GET',
        });
        const responseData = await response.json();

        let postsData = [];

        if (Array.isArray(responseData)) {
            // If responseData is an array, use it directly
            postsData = responseData;
        } else if (typeof responseData === 'object' && responseData.posts) {
            // If responseData is an object with a 'posts' property, assume it's the array
            postsData = responseData.posts;
        } else {
            console.error('Invalid response format:', responseData);
            return;
        }
        console.log("Posts: ", postsData)
        let postArea = document.getElementById('posts-container');
        postsData.forEach(post => {
            const postElement = document.createElement("div");
            const imagePath = post.image
            // postElement.classList.add("post");
            postElement.insertAdjacentHTML('beforeend', `
                <div>
                    <span>${post.user}</span>
                    <p>${post.content}</p>

                    ${post.image ? `<img src="${imagePath}" alt="Post Image">` : ''}
                    <small>${post.date_posted}</small>
                    <ul>
                        comments go here
                    </ul>
                    <form onsubmit="addComment(${post.id}); return false;">
                        <label for="comment">Add Comment:</label>
                        <input type="text" name="comment" required>
                        <button type="submit">Post Comment</button>
                    </form>
                    <hr>
                </div>
            `);
            postArea.appendChild(postElement);
        });


        
    } catch (error) {
        console.error('Error:', error); // Adjust as needed
    }
}

function redirectUpload(){
    window.location.href = '/create-post';
}

function redirectFeed(){
    window.location.href = '/feed';
}

async function uploadPost() {
    event.preventDefault();

    try {
        // Get the file input and its properties
        const fileInput = document.querySelector('input[name="picture"]');
        const file = fileInput.files[0];
        
        // Generate a new filename using the user's id and time of day
        const userId = await getUserId(); 
        const timestamp = Date.now();
        const newFilename = `${userId}_${timestamp}${getFileExtension(file.name)}`;

        // Update the form data with the new filename
        const form = document.getElementById('postForm');
        const formData = new FormData(form);
        formData.set('picture', file, newFilename);

        // Submit the form
        const response = await fetch('/create_post', {
            method: 'POST',
            body: formData
        });

        const data = await response.json(); // Adjust as needed
        
    } catch (error) {
        console.error('Error:', error); // Adjust as needed
    }
}

// Helper function to get file extension
function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
}


function getUserId() {
    fetch('/get_current_user')
        .then(response => response.json())
        .then(data => {
            // Check if the response contains the user_id
            if (data && data.user_id) {
                return data.user_id;
            } else {
                console.error('Error retrieving user ID');
                return null;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            return null;
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

// renderPosts();

async function signup() {
    // console.log(document.getElementById('signupUsername').value)
    const username = document.getElementById('inputUsername').value;
    const password = document.getElementById('inputPassword').value;

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
        window.location.href = '/dashboard';
    } catch (error) {
        console.error('Error during signup:', error.message);
    }
}

async function login(){
    const username = document.getElementById('inputUsername').value;
    const password = document.getElementById('inputPassword').value;

    console.log(username);
    console.log(password);

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
        window.location.href = '/dashboard';
    })
    .catch(error => {
        console.error('Error during signup:', error.message);
    });
}

async function userFeed(){
    fetch('/dashboardFeed', {
        method: 'GET',
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
        document.getElementById("posts-container").append(data);
    })
}