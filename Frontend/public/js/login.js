document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('auth-form');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const usernameError = document.getElementById('username-error');
  const passwordError = document.getElementById('password-error');
  const signupBtn = document.getElementById('signup-btn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    let isValid = true;
    usernameError.classList.add('hidden');
    passwordError.classList.add('hidden');

    if (!usernameInput.value) {
      usernameError.textContent = "Username required";
      usernameError.classList.remove('hidden');
      isValid = false;
    }
    if (passwordInput.value.length < 6) {
      passwordError.classList.remove('hidden');
      isValid = false;
    }

    if (isValid) {
      try {
        const body = new URLSearchParams();
        body.append('grant_type', 'password');
        body.append("username", usernameInput.value);
        body.append("password", passwordInput.value);

        const res = await fetch("http://127.0.0.1:8000/auth/token", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: body
        });
        const data = await res.json();

        if (res.ok) {
          alert("Login successful! Welcome, " + usernameInput.value);
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("username", usernameInput.value);
          localStorage.setItem("user_id", data.user_id); // ✅ this enables reco.js
          window.location.href = "index.html";
        } else {
          alert(data.detail || "Login failed.");
        }
      } catch (err) {
        console.error(err);
        alert("Server error. Please try again.");
      }
    }
  });

  signupBtn?.addEventListener('click', () => window.location.href = 'register.html');
});
