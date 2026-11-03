# FinSync - Password Reset Frontend Tests

Tester: Michalyn Moodley
Date: 30 October 2026
Browser: Microsoft Edge
Environment: Local password-reset.html frontend prototype

These results were recorded from manual browser testing.
Backend email delivery and password updates were not tested.

| ID | Test | Expected result | Actual result | Status |
|---|---|---|---|---|
| T01 | Submit an empty email | Required-field error without reloading | "Email address is required." appeared; page did not reload | Pass |
| T02 | Submit michalyn@ | Email-format error | "Enter a valid email address." appeared | Pass |
| T03 | Submit michalyn@example.com | Frontend preview confirmation | "Email format accepted. This preview does not send emails." appeared | Pass |
| T04 | Submit both password fields empty | Required-field errors | "Password is required." and "Please confirm your password." appeared | Pass |
| T05 | Enter Fin12 in both fields | Minimum-length error | "Use at least 7 characters." appeared | Pass |
| T06 | Enter finsync7 in both fields | Uppercase-letter error | "Include at least one uppercase letter." appeared | Pass |
| T07 | Enter FINSYNC7 in both fields | Lowercase-letter error | "Include at least one lowercase letter." appeared | Pass |
| T08 | Enter Finsync in both fields | Number requirement error | "Include at least one number." appeared | Pass |
| T09 | Enter FinSync7 and FinSync8 | Password mismatch error | "The passwords do not match." appeared | Pass |
| T10 | Enter FinSync7 in both fields | Validation confirmation and cleared fields | "Validation passed. This preview has not changed your password." appeared; both fields cleared | Pass |
| T11 | Correct an invalid email while typing | Existing error disappears when valid | Error disappeared without another submission | Pass |
| T12 | Switch between both preview screens | Correct form appears for each link | Both navigation links displayed the correct forms | Pass |

## Outstanding checks

- Back to Login navigation within the Flask application.
- Shared validation on login and registration forms.
- Mobile layout and keyboard navigation.
- Backend reset-email submission and response messages.
- Valid, expired, invalid and already-used reset links.
- Actual password update and login using the new password.
- Network/server error handling and retry behaviour.

## Defects

No defects were reported during the 12 tests above.
Integration-dependent behaviour remains unverified.