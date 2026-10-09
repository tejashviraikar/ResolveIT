const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "index.html";
}

const params = new URLSearchParams(window.location.search);
const issueId = params.get("id");


if (!issueId) {
    alert("Invalid issue ID");
    window.location.href = "employee-dashboard.html";
}


const issueTitle = document.getElementById("issueTitle");
const issueIdElement = document.getElementById("issueId");
const issueDescription = document.getElementById("issueDescription");
const issueCategory = document.getElementById("issueCategory");
const issuePriority = document.getElementById("issuePriority");
const issueStatus = document.getElementById("issueStatus");
const issueCreatedAt = document.getElementById("issueCreatedAt");

const commentsContainer =
    document.getElementById("commentsContainer");

const commentForm =
    document.getElementById("commentForm");

const commentMessage =
    document.getElementById("commentMessage");

const closeIssueBtn =
    document.getElementById("closeIssueBtn");

const closeMessage =
    document.getElementById("closeMessage");


async function loadIssue() {

    try {

        const response = await fetch(
            `${API_URL}/issues/${issueId}`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            alert(data.detail || "Unable to load issue");

            window.location.href =
                "employee-dashboard.html";

            return;
        }

        issueTitle.textContent = data.title;
        issueIdElement.textContent = data.issue_id;
        issueDescription.textContent = data.description;
        issueCategory.textContent = data.category;
        issuePriority.textContent = data.priority;
        issueStatus.textContent = data.status;
        issueCreatedAt.textContent = data.created_at;

        if (data.status === "CLOSED") {
            closeIssueBtn.style.display = "none";
        }

    } catch (error) {

        console.error(error);

        issueTitle.textContent =
            "Unable to connect to the server.";
    }
}


async function loadComments() {

    try {

        const response = await fetch(
            `${API_URL}/issues/${issueId}/comments`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            commentsContainer.innerHTML =
                `<p>${data.detail || "Unable to load comments."}`;

            return;
        }

        displayComments(data.comments);

    } catch (error) {

        console.error(error);

        commentsContainer.innerHTML =
            "<p>Unable to connect to the server.</p>";
    }
}


function displayComments(comments) {

    if (!comments || comments.length === 0) {

        commentsContainer.innerHTML =
            "<p>No comments yet.</p>";

        return;
    }

    commentsContainer.innerHTML = "";

    comments.forEach(comment => {

        const card = document.createElement("div");

        card.className = "comment-card";

        card.innerHTML = `
            <strong>${comment.name}</strong>

            <p>${comment.comment}</p>

            <small>${comment.created_at}</small>
        `;

        commentsContainer.appendChild(card);
    });
}


commentForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const comment =
        document.getElementById("comment").value.trim();

    if (!comment) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/issues/${issueId}/comments`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    comment: comment
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            commentMessage.textContent =
                data.detail || "Unable to add comment";

            return;
        }

        commentMessage.textContent =
            "Comment added successfully.";

        document.getElementById("comment").value = "";

        loadComments();

    } catch (error) {

        console.error(error);

        commentMessage.textContent =
            "Unable to connect to the server.";
    }
});


closeIssueBtn.addEventListener("click", async function () {

    if (!confirm("Are you sure you want to close this issue?")) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/issues/${issueId}/close`,
            {
                method: "PUT",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            closeMessage.textContent =
                data.detail || "Unable to close issue";

            return;
        }

        closeMessage.textContent =
            "Issue closed successfully.";

        loadIssue();

    } catch (error) {

        console.error(error);

        closeMessage.textContent =
            "Unable to connect to the server.";
    }
});


document.getElementById("backBtn").addEventListener(
    "click",
    function () {
        window.location.href = "employee-dashboard.html";
    }
);


document.getElementById("logoutBtn").addEventListener(
    "click",
    function () {

        localStorage.removeItem("access_token");
        localStorage.removeItem("user_role");
        localStorage.removeItem("user_id");

        window.location.href = "index.html";
    }
);


loadIssue();
loadComments();

// Support-only issue status management
const supportControls = document.getElementById("supportControls");
const supportStatus = document.getElementById("supportStatus");
const updateStatusBtn = document.getElementById("updateStatusBtn");
const statusMessage = document.getElementById("statusMessage");

if (role === "SUPPORT" && supportControls) {
    supportControls.style.display = "block";
}

if (updateStatusBtn) {
    updateStatusBtn.addEventListener("click", async function () {
        if (role !== "SUPPORT") {
            statusMessage.textContent =
                "Only Support Staff can update issue status.";
            return;
        }

        try {
            const response = await fetch(
                `${API_URL}/issues/${issueId}/status`,
                {
                    method: "PUT",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        status: supportStatus.value
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Unable to update issue status."
                );
            }

            statusMessage.textContent =
                "Issue status updated successfully.";

            // Refresh the displayed issue details
            await loadIssue();
        } catch (error) {
            statusMessage.textContent = error.message;
        }
    });
}
