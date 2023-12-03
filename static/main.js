var courseList;
var type;

function signout() {
    // Clear any stored authentication data (e.g., tokens, session data, cookies)
    // For instance, if using tokens:
    localStorage.removeItem('authToken'); // Remove token from local storage

    // Redirect the user to the sign-in page or homepage
    window.location.href = "/"; // Redirect to the sign-in page
}
function userLogin() {
    let studName = document.getElementById("stuName").value;
    const studPass = document.getElementById("stuPass").value;

    const data = { "name": studName, "password": studPass };

    const xmlhttp = new XMLHttpRequest();
    const method = 'POST'; // Considering this should be a POST request for login
    const url = 'http://127.0.0.1:5000/userLogin'; // Assuming this is the login endpoint

    xmlhttp.open(method, url, true);
    xmlhttp.setRequestHeader("Content-Type", "application/json"); // Setting the request header

    xmlhttp.onload = function () {
        if (xmlhttp.status === 200) {
            checkUserType(studName, function(type) {
                if (type == '3') {
                    window.location.href = '/admin';
                } else if (type == '2') {
                    window.location.href = '/teacher';
                } else {
                    let loginDiv = document.getElementById("rcorners1");
                    let loginBtn = document.getElementById("loginBtn");
                    let signUpBtn = document.getElementById("signupBtn");
                    let studentFunction = document.getElementById("postSignIn");
                    loginDiv.classList.add("hide");
                    loginBtn.classList.add("hide");
                    signUpBtn.classList.add("hide");

                    logOutBtn.classList.remove("hide");
                    logOutBtn.classList.add("button");
                    logOutBtn.classList.add("button1");

                    studentFunction.classList.remove("hide");
                }
            });
        } else {
            alert("Login failed. Please check your credentials.");
        }
    };

    xmlhttp.onerror = function () {
        alert("There was an error during the login process.");
    };
    xmlhttp.send(JSON.stringify(data));
}


function checkUserType(studName, callback) {
    const xmlhttp = new XMLHttpRequest();
    const method = 'POST';
    const url = 'http://127.0.0.1:5000/getType';

    const data = {
        userName: studName
    };

    xmlhttp.open(method, url, true);
    xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

    xmlhttp.onload = function () {
        if (xmlhttp.status === 200) {
            const userType = JSON.parse(xmlhttp.responseText);
            // Call the callback function with the user type
            callback(userType);
        } else {
            // Handle non-200 HTTP status
            console.error('Error:', xmlhttp.status);
        }
    };

    xmlhttp.send(JSON.stringify(data));
}


function openAllCourses() {
    // Show the modal
    if (window.location.href.indexOf("/admin") === -1) {
        // If not, show the modal
        document.getElementById("allCoursesModal").style.display = "block";
    }
    
    // Get the result div where you want to display the table
    const resultDiv = document.getElementById("resultAllCourses");

    // API request
    const xmlhttp = new XMLHttpRequest();
    const method = 'GET';
    const url = 'http://127.0.0.1:5000/schoolCourses';

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4) {
            if (xmlhttp.status == 200) {
                // Parse the JSON response
                const classList = JSON.parse(xmlhttp.responseText);
    
                // Create an HTML table
                let tableHTML = '<table border="1">';
                tableHTML += '<tr><th>Class ID</th><th>Class Name</th><th>Instructor</th><th>Meeting Time</th><th>Enrolled Students</th><th>Max Students</th></tr>';
    
                for (let i = 0; i < classList.length; i++) {
                    let classData = classList[i];
    
                    // Creating table rows
                    tableHTML += `<tr><td>${classData.ClassID}</td><td>${classData.ClassName}</td><td>${classData.Instructor}</td><td>${classData.MeetingTime}</td><td>${classData.EnrolledStudents}</td><td>${classData.MaxStudents}</td></tr>`;
                }
                tableHTML += '</table>';
                resultDiv.innerHTML = tableHTML;
            } else {
                // Handle errors here, e.g., display an error message
                resultDiv.innerHTML = 'Error: ' + xmlhttp.status;
            }
        }
    };
    

    xmlhttp.open(method, url, true);
    xmlhttp.send();
}

function openRegistrationCourses() {
    // Show the modal
    document.getElementById("registerCoursesModal").style.display = "block";

    // Get the result div where you want to display the table
    const resultDiv = document.getElementById("resultRegisterCourses");

    // API request
    const xmlhttp = new XMLHttpRequest();
    const method = 'GET';
    const url = 'http://127.0.0.1:5000/schoolCourses';

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4) {
            if (xmlhttp.status == 200) {
                // Parse the JSON response
                const classList = JSON.parse(xmlhttp.responseText);

                // Create an HTML table
                let tableHTML = '<table border="1">';
                tableHTML += '<tr><th>Class ID</th><th>Class Name</th><th>Instructor</th><th>Meeting Time</th><th>Enrolled Students</th><th>Max Students</th><th>Register</th></tr>';

                for (let i = 0; i < classList.length; i++) {
                    let classData = classList[i];

                    // Creating table rows with a "Register" button
                    tableHTML += `<tr><td>${classData.ClassID}</td><td>${classData.ClassName}</td><td>${classData.Instructor}</td><td>${classData.MeetingTime}</td><td>${classData.EnrolledStudents}</td><td>${classData.MaxStudents}</td><td><button onclick="registerForClass(${classData.ClassID})">Register</button></td></tr>`;
                }
                tableHTML += '</table>';
                resultDiv.innerHTML = tableHTML;
            } else {
                // Handle errors here, e.g., display an error message
                resultDiv.innerHTML = 'Error: ' + xmlhttp.status;
            }
        }
    };

    xmlhttp.open(method, url, true);
    xmlhttp.send();
}

function registerForClass(classID, button) {
    const username = document.getElementById("stuName").value;

    const xmlhttp = new XMLHttpRequest();
    const method = 'POST';
    const url = 'http://127.0.0.1:5000/registerClass';

    const data = {
        user_id: username,
        class_id: classID
    };

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            const response = JSON.parse(xmlhttp.responseText);
            if (response.status === 'registered') {
                button.innerHTML = 'DeRegister';
            } else if (response.status === 'deregistered') {
                button.innerHTML = 'Register';
            }
            
            // Disable the button if the user is registered
            button.disabled = response.status === 'registered';
            // Add a CSS class to visually indicate that the button is disabled
            button.classList.toggle('disabled', response.status === 'registered');
        }
    };

    xmlhttp.open(method, url, true);
    xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xmlhttp.send(JSON.stringify(data));
}


function openMyCourses() {
    document.getElementById("myModal").style.display = "block"; // Show the modal
    const resultDiv = document.getElementById("resultAll");
    const xmlhttp = new XMLHttpRequest();
    const method = 'GET';
    const url = 'http://127.0.0.1:5000/stuCourses';

    let studName = document.getElementById("stuName").value;
    const data = { "name": studName };

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            // Parse the JSON response
            courseList = JSON.parse(xmlhttp.responseText);

            // Create an HTML table
            let tableHTML = '<table border="1">';
            tableHTML += '<tr><th>Name</th><th>Grade</th><th>Action</th></tr>';

            for (let i = 0; i < courseList.length; i++) {
                let courseName = courseList[i].course_name;
                let grade = courseList[i].grade;
                let classId = courseList[i].class_id;

                // Creating table rows with a deregister button
                tableHTML += `<tr><td>${courseName}</td><td>${grade}</td><td><button onclick="deregisterCourse(${i}, ${classId})">Deregister</button></td></tr>`;
            }
            tableHTML += '</table>';
            resultDiv.innerHTML = tableHTML;
        }
    };

    xmlhttp.open(method, `${url}?name=${studName}`, true);  // Pass the name as a query parameter
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(JSON.stringify(data));
}

function deregisterCourse(index) {
    const xmlhttp = new XMLHttpRequest();
    const method = 'POST';
    const url = 'http://127.0.0.1:5000/deregisterCourse';

    const classId = courseList[index].class_id; 
    let studName = document.getElementById("stuName").value;
    const data = JSON.stringify({ "name": studName, "class_id": classId });

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            // Refresh the table after deregistering
            openMyCourses();
        }
    };

    xmlhttp.open(method, url, true);
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(data);
}


function closeMyCourses() {
    // Hide the modals
    document.getElementById("myModal").style.display = "none"; 
    document.getElementById("allCoursesModal").style.display = "none";
    document.getElementById("registerCoursesModal").style.display = "none";
}

async function postStudent() {
    const username = document.getElementById("stuName").value;
    const pass = document.getElementById("stuPass").value;
    const type = 1;

    const data = { username: username, password: pass, type: type };

    try {
        const response = await fetch('http://127.0.0.1:5000/user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const responseData = await response.json();

        // Show an alert with the error message, or "Success" if there's no error
        alert(responseData.error || 'Success');

        console.log(responseData);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example teacher-related functions in main.js

function getTeacherClasses() {
    const xmlhttp = new XMLHttpRequest();
    const method = 'GET';
    const url = 'http://127.0.0.1:5000/teacher/classes';

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            const teacherClasses = JSON.parse(xmlhttp.responseText);

            // Display the teacher's classes on the page
            displayTeacherClasses(teacherClasses);
        }
    };

    xmlhttp.open(method, url, true);
    xmlhttp.send();
}

function displayTeacherClasses(classes) {
    const teacherClassesDiv = document.getElementById('teacherClasses');
    let classesHTML = '<ul>';

    for (const classData of classes) {
        classesHTML += `<li>${classData.ClassName}</li>`;
    }

    classesHTML += '</ul>';
    teacherClassesDiv.innerHTML = classesHTML;
}

// Add more functions to manage grades as needed

// Fetch and display teacher's classes when the page loads
document.addEventListener('DOMContentLoaded', function () {
    getTeacherClasses();
});


function teacherLogin(){}
function postTeacher(){}