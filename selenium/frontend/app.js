$(document).ready(function() {
    const loggedInUser = localStorage.getItem("loggedInUser");

    if (window.location.pathname.includes("users.html")) {
        $.get("http://localhost:5000/user/list", function (data) {
            $("#userList").empty();

            data.forEach(function (user) {
                $("#userList").append(`
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.email}</td>
                        <td>${user.first_name} ${user.middle_name ? user.middle_name + ' ' : ''}${user.last_name}</td>
                        <td>${user.birthdate}</td>
                        <td>
                            <button name="updateButton" class="updateButton btn btn-primary" data-user-id="${user.id}">Update</button>
                            <button name="deleteButton" class="deleteButton btn btn-danger" data-user-id="${user.id}">Delete</button>
                        </td>
                    </tr>
                `);
            });

            $("#onlineUsersButton").click(function() {
                window.location.href = "onlineusers.html";
            });

            $(".updateButton").click(function() {
                const userId = $(this).data("user-id");
                window.location.href = `update.html?user_id=${userId}`;
            });

            $(".deleteButton").click(function() {
                const userId = $(this).data("user-id");
                deleteUserData(userId);
            });
        });

        function deleteUserData(userId) {
            $.ajax({
                type: "DELETE",
                url: `http://localhost:5000/user/delete/${userId}`,
                contentType: "application/json",
                statusCode: {
                    200: function(response) {
                        alert(response.message);
                        window.location.href = "users.html";
                    },
                    400: function(response) {
                        alert(response.error);
                    },
                    500: function() {
                        alert("An error occurred while processing your request.");
                    }
                }
            });
        }

        $("#logoutButton").click(function() {
            $.ajax({
                type: "POST",
                url: "http://localhost:5000/logout",
                data: JSON.stringify({ username: loggedInUser }),
                contentType: "application/json",
                statusCode: {
                    200: function(response) {
                        localStorage.removeItem("loggedInUser");
                        alert(response.message);
                        window.location.href = "login.html";
                    },
                    401: function(response) {
                        alert(response.error);
                    },
                    500: function() {
                        alert("An error occurred while processing your request.");
                    }
                }
            });
        });
    }

    if (window.location.pathname.includes("onlineusers.html")) {
        $.get("http://localhost:5000/onlineusers", function (data) {
            $("#onlineUsers").empty();

            data.forEach(function (user) {
                $("#onlineUsers").append(`
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.ipaddress}</td>
                        <td>${user.login_time}</td>
                    </tr>
                `);
            });
        });

        $("#usersButton").click(function() {
            window.location.href = "users.html";
        });
    }

    if (window.location.pathname.includes("login.html")) {
        $("#goToRegister").click(function() {
            window.location.href = "register.html";
        });

        $("#loginForm").submit(function (event) {
            event.preventDefault();

            const username = $("#username").val();
            const password = $("#password").val();

            $.ajax({
                type: "POST",
                url: "http://localhost:5000/login",
                data: JSON.stringify({username: username, password: password}),
                contentType: "application/json",
                statusCode: {
                    200: function (response) {
                        // Store the username in localStorage after successful login
                        localStorage.setItem("loggedInUser", username);
                        window.location.href = "users.html";
                    },
                    401: function() {
                        alert("Login failed. Please check your credentials.");
                    },
                    500: function() {
                        alert("An error occurred while processing your request.");
                    }
                }
            });
        });
    }

    if (window.location.pathname.includes("register.html")) {
        $("#goToLogin").click(function() {
            window.location.href = "login.html";
        });

        // Registration form submission handling
        $("#registrationForm").submit(function (event) {
            event.preventDefault();

            // Gather registration form data
            const username = $("#username").val();
            const first_name = $("#firstname").val();
            const last_name = $("#lastname").val();
            const email = $("#email").val();
            const password = $("#password").val();

            const formDataJSON = JSON.stringify( {
                username: username,
                first_name: first_name,
                last_name: last_name,
                email: email,
                password: password
            });

            // Make AJAX request to Flask API for registration
            $.ajax({
                type: "POST",
                url: "http://localhost:5000/user/create", // Replace with actual URL
                data: formDataJSON,
                contentType: "application/json",
                statusCode: {
                    200: function () {
                        alert("Registration successful. You can now log in.");
                        window.location.href = "login.html";
                    },
                    400: function(response) {
                        alert(response.error);
                    },
                    500: function() {
                        alert("An error occurred while processing your request.");
                    }
                }
            });
        });
    }

    if (window.location.pathname.includes("update.html")) {
        const userId = getParameterByName("user_id");

        $("#updateForm").submit(function (event) {
            event.preventDefault();

            // Gather updated user data from form fields
            const updatedData = {
                username: $("#newUsername").val(),
                firstname: $("#newFirstName").val(),
                lastname: $("#newLastName").val(),
                email: $("#newEmail").val()
            };

            console.log(JSON.stringify(updatedData))

            $.ajax({
                type: "PUT",
                url: `http://localhost:5000/user/update/${userId}`,
                data: JSON.stringify(updatedData),
                contentType: "application/json",
                statusCode: {
                    200: function (response) {
                        alert(response.message);
                        window.location.href = "users.html";
                    },
                    400: function(response) {
                        alert(response.error);
                    },
                    500: function() {
                        alert("An error occurred while processing your request.");
                    }
                }
            });
        });
    }
});

function getParameterByName(name, url) {
    if (!url) {
        url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
    const results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return "";
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
