// ================================
// SMART LOST & FOUND PORTAL
// LOGIN PAGE
// ================================

const loginForm = document.getElementById("loginForm");
const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");

// ================================
// SHOW / HIDE PASSWORD
// ================================

togglePassword.addEventListener("click", () => {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        togglePassword.innerHTML = '<i class="bi bi-eye-slash"></i>';

    } else {

        passwordInput.type = "password";
        togglePassword.innerHTML = '<i class="bi bi-eye"></i>';

    }

});

// ================================
// FORM VALIDATION
// ================================

loginForm.addEventListener("submit", function (e) {

    const role = document.getElementById("role").value;
    const email = document.getElementById("email").value.trim();
    const password = passwordInput.value.trim();

    if (role === "" || email === "" || password === "") {

        e.preventDefault();
        alert("Please fill all fields.");

    }

    // If all fields are filled,
    // the form is submitted automatically to Flask.
});