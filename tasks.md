# QA Testing Paths

1. Start as logged out user/
    - Visiting http://localhost:5000/dashboard should redirect back to homepage.
2. Try to sign up for a new account.
    - Invalid password mismatch test.
    - Invalid email address not matching regex should not work. **CHECK**
    - 