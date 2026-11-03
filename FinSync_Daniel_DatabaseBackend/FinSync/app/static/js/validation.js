/*
 * Basic client-side validation so the pages are testable.
 * Michalyn owns frontend validation and can replace this file.
 * The SAME rules are enforced again on the server (app/security.py),
 * because browser checks can always be bypassed.
 */
(function () {
  "use strict";

  var EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

  function passwordErrors(pw, confirm) {
    var errs = [];
    if (!pw) return ["Password is required."];
    if (pw.length < 8) errs.push("Password must be at least 8 characters.");
    if (pw.length > 128) errs.push("Password must be at most 128 characters.");
    if (!/[A-Z]/.test(pw)) errs.push("Password must contain an uppercase letter.");
    if (!/[a-z]/.test(pw)) errs.push("Password must contain a lowercase letter.");
    if (!/\d/.test(pw)) errs.push("Password must contain a number.");
    if (!/[^A-Za-z0-9]/.test(pw)) errs.push("Password must contain a special character.");
    if (confirm !== undefined && pw !== confirm) errs.push("Passwords do not match.");
    return errs;
  }

  function val(form, name) {
    var el = form.elements[name];
    return el ? el.value : "";
  }

  var checks = {
    forgot: function (f) {
      var e = val(f, "email").trim();
      if (!e) return ["Email address is required."];
      return EMAIL_RE.test(e) ? [] : ["Please enter a valid email address."];
    },
    reset: function (f) {
      return passwordErrors(val(f, "password"), val(f, "confirm_password"));
    },
    login: function (f) {
      var errs = [];
      if (!val(f, "email").trim()) errs.push("Email address is required.");
      if (!val(f, "password")) errs.push("Password is required.");
      return errs;
    },
    signup: function (f) {
      var errs = [];
      if (!val(f, "full_name").trim()) errs.push("Full name is required.");
      if (!EMAIL_RE.test(val(f, "email").trim())) errs.push("Please enter a valid email address.");
      return errs.concat(passwordErrors(val(f, "password"), val(f, "confirm_password")));
    }
  };

  document.querySelectorAll("form[data-validate]").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      var check = checks[form.getAttribute("data-validate")];
      var errs = check ? check(form) : [];
      var box = form.parentElement.querySelector(".js-errors");
      if (errs.length) {
        ev.preventDefault();   // stay on the page, no reload
        if (box) {
          box.innerHTML = "";
          var ul = document.createElement("ul");
          errs.forEach(function (m) {
            var li = document.createElement("li");
            li.textContent = m;     // textContent = safe from HTML injection
            ul.appendChild(li);
          });
          box.appendChild(ul);
          box.hidden = false;
        }
      } else if (box) {
        box.hidden = true;
      }
    });
  });
})();
