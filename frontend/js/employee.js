const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");
const role = localStorage.getItem("user_role");

if (!token) {
    window.location.href = "index.html";
}

if (role !== "EMPLOYEE") {
    window.location.href = "index.html";
}

const issuesContainer = document.getElementById("issuesContainer");
const refreshBtn = document.getElementById("refreshBtn");
const logoutBtn = document.getElementById("logoutBtn");
const createIssueBtn = document.getElementById("createIssueBtn");


async function loadIssues() {

    issuesContainer.innerHTML = "<p>Loading issues...</p>";

    try {

        const response = await fetch(`${API_URL}/issues`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {

            issuesContainer.innerHTML =
                "<p>Unable to load issues.</p>";

            return;
        }

        const data = await response.json();

        displayIssues(data.issues);

    } catch (error) {

        console.error(error);

        issuesContainer.innerHTML =
            "<p>Unable to connect to the server.</p>";
    }
}


function displayIssues(issues) {

    if (!issues || issues.length === 0) {

        issuesContainer.innerHTML =
            "<p>No issues found.</p>";

        return;
    }

    issuesContainer.innerHTML = "";

    issues.forEach(issue => {

        const issueCard = document.createElement("div");

        issueCard.className = "issue-card";

        issueCard.innerHTML = `
            <h3>${issue.title}</h3>

            <p>
                <strong>Description:</strong>
                ${issue.description}
            </p>

            <p>
                <strong>Category:</strong>
                ${issue.category}
            </p>

            <p>
                <strong>Priority:</strong>
                ${issue.priority}
            </p>

            <p>
                <strong>Status:</strong>
                ${issue.status}
            </p>

            <p>
                <strong>Issue ID:</strong>
                ${issue.issue_id}
            </p>

            <button class="view-issue-btn">
                View Details
            </button>
        `;

        issueCard.querySelector(".view-issue-btn")
            .addEventListener("click", function () {

                window.location.href =
                    `issue.html?id=${issue.issue_id}`;

            });

        issuesContainer.appendChild(issueCard);
    });
}


refreshBtn.addEventListener("click", loadIssues);


logoutBtn.addEventListener("click", function () {

    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
    localStorage.removeItem("user_id");

    window.location.href = "index.html";
});


const issueFormContainer =
    document.getElementById("issueFormContainer");

const issueForm =
    document.getElementById("issueForm");

const cancelIssueBtn =
    document.getElementById("cancelIssueBtn");

const issueMessage =
    document.getElementById("issueMessage");


createIssueBtn.addEventListener("click", function () {

    issueFormContainer.classList.remove("hidden");

    issueMessage.textContent = "";

});


cancelIssueBtn.addEventListener("click", function () {

    issueForm.reset();

    issueFormContainer.classList.add("hidden");

    issueMessage.textContent = "";

});


issueForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const title =
        document.getElementById("title").value;

    const description =
        document.getElementById("description").value;

    const category =
        document.getElementById("category").value;

    const priority =
        document.getElementById("priority").value;


    try {

        const response = await fetch(`${API_URL}/issues`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify({
                title: title,
                description: description,
                category: category,
                priority: priority
            })

        });


        const data = await response.json();


        if (!response.ok) {

            issueMessage.textContent =
                data.detail || "Failed to create issue";

            return;
        }


        issueMessage.textContent =
            `Issue created successfully. Issue ID: ${data.issue_id}`;


        issueForm.reset();


        setTimeout(function () {

            issueFormContainer.classList.add("hidden");

            issueMessage.textContent = "";

            loadIssues();

        }, 1000);


    } catch (error) {

        console.error(error);

        issueMessage.textContent =
            "Unable to connect to the server.";

    }

});

loadIssues();