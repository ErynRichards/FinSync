
// LOGIN PAGE

// Find the Login form
const loginForm = document.getElementById("loginForm");

// Only run on Login page
if (loginForm) {

    loginForm.addEventListener("submit", function(event) {

        // Stop submission until backend is connected
        event.preventDefault();

        alert("Login frontend is ready for backend integration.");

    });

}


// SIGN UP PAGE

// Find the Sign Up form
const signupForm = document.getElementById("signupForm");

// Only run on Sign Up page
if (signupForm) {

    signupForm.addEventListener("submit", function(event) {

        // Stop submission until backend is connected
        event.preventDefault();

        // Get passwords
        const password =
            document.getElementById("signupPassword").value;

        const confirmPassword =
            document.getElementById("confirmPassword").value;

        // Get error message
        const errorMessage =
            document.getElementById("passwordError");

        // Check if passwords match
        if (password !== confirmPassword) {

            errorMessage.textContent =
                "Passwords do not match.";

        } else {

            errorMessage.textContent = "";

            alert("Sign Up frontend is ready for backend integration.");

        }

    });

}
