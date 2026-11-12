(() => {
  "use strict";

  // Find the part of the page this code will update.
  const form = document.querySelector("#profile-form");
  if (!form) return;

  const fields = {
    fullName: form.elements.fullName,
    email: form.elements.email,
    contactNumber: form.elements.contactNumber
  };
  const saveButton = form.querySelector("button[type=submit]");

  // Find the part of the page this code will update.
  const status = document.querySelector("#profile-status");
  const demo = form.hasAttribute("data-demo");
  const profileUrl = form.dataset.profileUrl;
  const demoKey = "finsync-settings-demo-profile";
  const sampleProfile = {
    fullName: "John Doe",
    email: "johndoe@gmail.com",
    contactNumber: "012 345 6789"
  };

  // Handle this part of the page.
  function showStatus(message, isError = false) {
    status.textContent = message;
    status.dataset.error = String(isError);
  }

  // Handle this part of the page.
  function showFieldError(input, message) {
    document.getElementById(input.getAttribute("aria-describedby")).textContent = message;
    input.setAttribute("aria-invalid", String(Boolean(message)));
  }

  // Handle this part of the page.
  function displayProfile(profile) {
    for (const [key, input] of Object.entries(fields)) {
      input.value = profile[key] ?? "";
    }
  }

  // Read a saved demo profile or load the signed-in user's profile from FinSync.
  // The backend should identify the user from their session.
  async function loadProfile() {
    try {
      if (demo) {

        const savedProfile = localStorage.getItem(demoKey);
        displayProfile(savedProfile ? JSON.parse(savedProfile) : sampleProfile);

      } else {

        if (!profileUrl) throw new Error("Missing profile URL");

        const response = await fetch(profileUrl, { cache: "no-store" });

        if (!response.ok) throw new Error("Profile request failed");

        const result = await response.json();
        displayProfile({fullName: result.fullName, email: result.email, contactNumber: result.contactNumber});
      }
      saveButton.disabled = false;

    } catch {
      showStatus("We could not load your profile. Please refresh and try again.", true);
    }
  }

  // Handle this part of the page.
  function validateProfile(profile) {
    const errors = {};
    const { fullName, email, contactNumber } = profile;

    // Accept names with accents, spaces, apostrophes and hyphens.
    if (!fullName || !/\p{L}/u.test(fullName) || /[\d@<>]/.test(fullName)) {
      errors.fullName = "Enter a valid full name.";
    }
    if (!email || fields.email.validity.typeMismatch || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = "Enter a valid email address.";
    }

    // Blank is allowed. A supplied number may use spaces, dashes and
    // parentheses, with an optional country-code plus sign at the start.
    const digits = contactNumber.replace(/\D/g, "");

    if (contactNumber && (!/^\+?[\d ()-]+$/.test(contactNumber) ||
        digits.length < 10 || digits.length > 15)) {
      errors.contactNumber = "Enter a contact number with 10 to 15 digits.";
    }
    return errors;
  }

  // Run this code when the user interacts with the page.
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (saveButton.disabled) return;

    const profile = Object.fromEntries(
      Object.entries(fields).map(([key, input]) => [key, input.value.trim()])
    );
    const errors = validateProfile(profile);
    for (const [key, input] of Object.entries(fields)) {
      showFieldError(input, errors[key] ?? "");
    }

    const firstError = Object.keys(errors)[0];
    if (firstError) {
      showStatus("Please correct the highlighted fields.", true);
      fields[firstError].focus();
      return;
    }

    // Lock the form while saving so a second submission cannot overwrite
    // the first one and the success message matches the values submitted.
    saveButton.disabled = true;
    Object.values(fields).forEach(input => { input.readOnly = true; });
    showStatus("Saving changes…");

    try {
      if (demo) {
        localStorage.setItem(demoKey, JSON.stringify(profile));
      } else {

        // The authenticated backend must validate the fields again and
        // return a successful HTTP status only after saving the profile.
        const response = await fetch(profileUrl, {

          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(profile)
        });

        if (response.status === 409) {
          showFieldError(fields.email, "This email address is already in use.");
          showStatus("Please use a different email address.", true);
          fields.email.focus();
          return;
        }

        if (!response.ok) throw new Error("Profile update failed");
      }

      displayProfile(profile);
      showStatus("Profile information updated successfully.");

    } catch {
      showStatus("We could not save your changes. Please try again.", true);

    } finally {
      saveButton.disabled = false;
      Object.values(fields).forEach(input => { input.readOnly = false; });
    }

  });

  for (const input of Object.values(fields)) {
    // Run this code when the user interacts with the page.
    input.addEventListener("input", () => {
      showFieldError(input, "");
      showStatus("");
    });
  }
  loadProfile();
})();
