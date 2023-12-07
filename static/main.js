 // Sample data - replace this with your actual data fetching logic
//  const userData = {
//     posts: [
//         {
//             id: 1,
//             content: "Post Content 1",
//             image: "post_image_1.jpg",
//             date_posted: "2023-01-01 12:34:56",
//             comments: [
//                 { content: "Comment 1", date_posted: "2023-01-02 08:45:30" },
//                 { content: "Comment 2", date_posted: "2023-01-03 14:22:18" }
//             ]
//         },
//         {
//             id: 2,
//             content: "Post Content 2",
//             image: "post_image_2.jpg",
//             date_posted: "2023-01-05 18:12:45",
//             comments: [
//                 { content: "Comment 3", date_posted: "2023-01-07 09:20:10" }
//                 // Additional comments for post 2
//             ]
//         }
//         // Additional posts
//     ]
// };

// Function to render posts
async function renderPosts() {
    // console.log("loading")
    const postsContainer = document.getElementById("posts-container");

    try {
        const response = await fetch('/dashboardFeed');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const postsData = await response.json();

        postsData.forEach(post => {
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
    } catch (error) {
        console.error('Error fetching and rendering posts:', error.message);
    }
}
window.onload = renderPosts();
// function renderPosts() {
//     const postsContainer = document.getElementById("posts-container");

//     userData.posts.forEach(post => {
//         const postElement = document.createElement("div");
//         postElement.classList.add("post");

//         postElement.innerHTML = `
//             <p>${post.content}</p>
//             ${post.image ? `<img src="${post.image}" alt="Post Image">` : ''}
//             <small>${post.date_posted}</small>
//             <ul>
//                 ${post.comments.map(comment => `<li>${comment.content} - ${comment.date_posted}</li>`).join('')}
//             </ul>
//             <form onsubmit="addComment(${post.id}); return false;">
//                 <label for="comment">Add Comment:</label>
//                 <input type="text" name="comment" required>
//                 <button type="submit">Post Comment</button>
//             </form>
//             <hr>
//         `;

//         postsContainer.appendChild(postElement);
//     });
// }

async function uploadPost() {
    event.preventDefault(); // Prevent the default form submission

    try {
        // Get the file input and its properties
        const fileInput = document.querySelector('input[name="picture"]');
        const file = fileInput.files[0];
        
        // Generate a new filename using the user's id and time of day
        const userId = await getUserId(); // Wait for getUserId to complete
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
        console.log(data); // Adjust as needed
    } catch (error) {
        console.error('Error:', error); // Adjust as needed
    }
}

// Helper function to get file extension
function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
}

// Replace this function with your actual function to get the user's id
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

renderPosts();

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