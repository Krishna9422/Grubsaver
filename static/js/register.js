document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".register-btn").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent form submission

        let fullName = document.querySelector("input[placeholder='Enter your full name']").value;
        let email = document.querySelector("input[placeholder='Enter your email']").value;
        let username = document.querySelector("input[placeholder='Choose a username']").value;
        let password = document.querySelector("input[placeholder='Create a password']").value;

        if (fullName.length < 3) {
            alert("Full name must be at least 3 characters long.");
            return;
        }
        if (!email.match(/^.+@.+\..+$/)) {
            alert("Invalid email format.");
            return;
        }
        if (username.length < 4) {
            alert("Username must be at least 4 characters long.");
            return;
        }
        if (password.length < 6) {
            alert("Password must be at least 6 characters long.");
            return;
        }

        // Send data to Flask backend
        fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Registration successful!");
                window.location.href = "login.html"; // Redirect after successful registration
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
