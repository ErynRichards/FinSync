// validation.js
// Checks the forms in the browser before they are sent, so the user sees
// mistakes straight away. Michalyn can replace this file with her own.
// The server checks everything again in app.py, because browser checks can be skipped.

// Handle this part of the page.
function isValidEmail(email) {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
}

// Handle this part of the page.
function checkPasswordRules(password, confirmPassword) {

  var errors = [];
  if (password.length < 8) errors.push("Password must be at least 8 characters.");
  if (!/[A-Z]/.test(password)) errors.push("Password must contain an uppercase letter.");
  if (!/[a-z]/.test(password)) errors.push("Password must contain a lowercase letter.");
  if (!/[0-9]/.test(password)) errors.push("Password must contain a number.");
  if (!/[^A-Za-z0-9]/.test(password)) errors.push("Password must contain a special character.");
  if (password !== confirmPassword) errors.push("Passwords do not match.");
  return errors;
}



// Returns a list of mistakes for the given form
function checkForm(form) {

  var type = form.dataset.validate;
  var errors = [];

  if (type === "forgot" || type === "login" || type === "signup") {
    if (!isValidEmail(form.email.value.trim())) {
      errors.push("Please enter a valid email address.");
    }
  }

  if (type === "login" && form.password.value === "") {
    errors.push("Password is required.");
  }
  if (type === "signup" && form.full_name.value.trim() === "") {
    errors.push("Full name is required.");
  }
  if (type === "signup" || type === "reset") {
    errors = errors.concat(checkPasswordRules(form.password.value, form.confirm_password.value));
  }
  return errors;
}



// Show the mistakes in the red box above the form
function showErrors(form, errors) {
  var box = form.parentElement.querySelector(".js-errors");
  box.innerHTML = "";
  for (var i = 0; i < errors.length; i++) {
    var line = document.createElement("div");
    line.textContent = errors[i];
    box.appendChild(line);
  }
  box.hidden = errors.length === 0;
}

// Check every form that has a data-validate attribute when it is submitted
var forms = document.querySelectorAll("form[data-validate]");
for (var i = 0; i < forms.length; i++) {
  forms[i].addEventListener("submit", function (event) {
    var errors = checkForm(this);
    showErrors(this, errors);
    if (errors.length > 0) {
      event.preventDefault(); // stop the form from being sent
    }
  });
}
