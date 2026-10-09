const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    try {

        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            message.textContent = data.detail || "Login failed";
            return;
        }

        localStorage.setItem("access_token", data.access_token);

        const payload = JSON.parse(
            atob(data.access_token.split(".")[1])
        );

        localStorage.setItem("user_role", payload.role);
        localStorage.setItem("user_id", payload.user_id);

        message.textContent = "Login successful!";

        if (payload.role === "SUPPORT") {
            window.location.href = "support-dashboard.html";
        } else {
            window.location.href = "employee-dashboard.html";
        }

    } catch (error) {

        console.error(error);

        message.textContent =
            "Unable to connect to the server.";
    }
});