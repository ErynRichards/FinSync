// Frontend source: Phase 5.1 Frontend.zip / auth.js
// Integrated with Mishayle's Flask authentication routes.
// Login submits normally to Flask; no demo alert or preventDefault.

const signupForm = document.getElementById("signupForm");
if (signupForm) {
    // Run this code when the user interacts with the page.
    signupForm.addEventListener("submit", function(event) {
        const password = document.getElementById("signupPassword").value;
        const confirmation = document.getElementById("confirmPassword").value;
        const errorMessage = document.getElementById("passwordError");
        if (password !== confirmation) {
            event.preventDefault();
            errorMessage.textContent = "Passwords do not match.";
        } else {
            errorMessage.textContent = "";
            // Submit normally to Flask /signup.
        }
    });
}
