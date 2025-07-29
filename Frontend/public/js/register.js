
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('signup-form');
  const emailInput = document.getElementById('email');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const emailError = document.getElementById('email-error');
  const passwordError = document.getElementById('password-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    let isValid = true;
    emailError.classList.add('hidden');
    passwordError.classList.add('hidden');

    if (passwordInput.value.length < 6) {
      passwordError.classList.remove('hidden');
      isValid = false;
    }

    if (isValid) {
      try {
        const response = await fetch("http://127.0.0.1:8000/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            username: usernameInput.value,
            email: emailInput.value,
            password: passwordInput.value
          })
        });

        const data = await response.json();

        if (response.ok) {
          alert("Sign-up successful! Redirecting to login..");
          window.location.href = "login.html";  // or 'index.html' if you want direct access
        } else {
          alert(data.detail || "Signup failed.");
        }
      } catch (err) {
        console.error(err);
        alert("Server error.");
      }
    }
  });
});
