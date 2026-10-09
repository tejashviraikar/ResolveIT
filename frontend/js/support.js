const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");
const role = localStorage.getItem("user_role");

const issuesContainer = document.getElementById("issuesContainer");
const message = document.getElementById("message");

// Check whether the user is logged in as Support Staff
if (!token || role !== "SUPPORT") {
    window.location.href = "index.html";
}

// Headers for authenticated API requests
function getHeaders() {
    return {
        "Authorization": `Bearer ${token}`
    };
}

// Load dashboard statistics
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/dashboard`, {
            method: "GET",
            headers: getHeaders()
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to load dashboard statistics"
            );
        }

        document.getElementById("totalIssues").textContent =
            data.total_issues ?? 0;

        document.getElementById("openIssues").textContent =
            data.open_issues ?? 0;

        document.getElementById("inProgressIssues").textContent =
            data.in_progress_issues ?? 0;

        document.getElementById("resolvedIssues").textContent =
            data.resolved_issues ?? 0;

    } catch (error) {
        message.textContent = error.message;
    }
}

// Load issues with optional search and filters
async function loadIssues() {
    issuesContainer.textContent = "Loading issues...";
    message.textContent = "";

    const params = new URLSearchParams();

    const search =
        document.getElementById("searchInput").value.trim();

    const status =
        document.getElementById("statusFilter").value;

    const priority =
        document.getElementById("priorityFilter").value;

    const category =
        document.getElementById("categoryFilter").value;

    if (search) {
        params.append("search", search);
    }

    if (status) {
        params.append("status", status);
    }

    if (priority) {
        params.append("priority", priority);
    }

    if (category) {
        params.append("category", category);
    }

    try {
        const response = await fetch(
            `${API_URL}/issues/search?${params.toString()}`,
            {
                method: "GET",
                headers: getHeaders()
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Unable to load issues");
        }

        displayIssues(data.issues || []);

    } catch (error) {
        issuesContainer.textContent = "";
        message.textContent = error.message;
    }
}

// Display issue cards safely
function displayIssues(issues) {
    issuesContainer.textContent = "";

    if (issues.length === 0) {
        const emptyMessage = document.createElement("p");
        emptyMessage.textContent = "No issues found.";
        issuesContainer.appendChild(emptyMessage);
        return;
    }

    issues.forEach(function (issue) {
        const card = document.createElement("article");
        card.className = "issue-card";

        const title = document.createElement("h3");
        title.textContent = issue.title;

        const description = document.createElement("p");
        description.textContent =
            "Description: " + issue.description;

        const category = document.createElement("p");
        category.textContent = "Category: " + issue.category;

        const priority = document.createElement("p");
        priority.textContent = "Priority: " + issue.priority;

        const status = document.createElement("p");
        status.textContent = "Status: " + issue.status;

        const issueId = document.createElement("p");
        issueId.textContent = "Issue ID: " + issue.issue_id;

        const creator = document.createElement("p");
        creator.textContent =
            "Created By User ID: " + issue.created_by;

        const assigned = document.createElement("p");
        assigned.textContent =
            "Assigned To: " +
            (issue.assigned_to ?? "Not assigned");

        // Assign issue controls
        const assignInput = document.createElement("input");
        assignInput.type = "number";
        assignInput.min = "1";
        assignInput.placeholder = "Support User ID";
        assignInput.value = issue.assigned_to || "";

        const assignButton = document.createElement("button");
        assignButton.textContent = "Assign Issue";

        assignButton.addEventListener("click", async function () {
            const assignedTo = Number(assignInput.value);

            if (!Number.isInteger(assignedTo) || assignedTo <= 0) {
                message.textContent = "Enter a valid support user ID.";
                return;
            }

            try {
                const response = await fetch(
                    `${API_URL}/issues/${issue.issue_id}/assign`,
                    {
                        method: "PUT",
                        headers: {
                            ...getHeaders(),
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            assigned_to: assignedTo
                        })
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Assignment failed");
                }

                message.textContent = "Issue assigned successfully.";
                await loadIssues();
                await loadDashboard();

            } catch (error) {
                message.textContent = error.message;
            }
        });

        card.appendChild(assignInput);

        // Issue status controls
        const statusSelect = document.createElement("select");

        const statuses = [
            "OPEN",
            "ASSIGNED",
            "IN PROGRESS",
            "RESOLVED",
            "CLOSED"
        ];

        statuses.forEach(function (statusValue) {
            const option = document.createElement("option");
            option.value = statusValue;
            option.textContent = statusValue;
            statusSelect.appendChild(option);
        });

        statusSelect.value = issue.status;

        const statusButton = document.createElement("button");
        statusButton.textContent = "Update Status";

        statusButton.addEventListener("click", async function () {
            try {
                const response = await fetch(
                    `${API_URL}/issues/${issue.issue_id}/status`,
                    {
                        method: "PUT",
                        headers: {
                            ...getHeaders(),
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            status: statusSelect.value
                        })
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.detail || "Unable to update status"
                    );
                }

                message.textContent = "Issue status updated successfully.";

                await loadIssues();
                await loadDashboard();

            } catch (error) {
                message.textContent = error.message;
            }
        });

        card.appendChild(statusSelect);
        card.appendChild(statusButton);

        card.appendChild(assignButton);

        const detailsButton = document.createElement("button");
        detailsButton.textContent = "View Details";

        detailsButton.addEventListener("click", function () {
            window.location.href =
                "issue.html?id=" + encodeURIComponent(issue.issue_id);
        });

        card.appendChild(title);
        card.appendChild(description);
        card.appendChild(category);
        card.appendChild(priority);
        card.appendChild(status);
        card.appendChild(issueId);
        card.appendChild(creator);
        card.appendChild(assigned);
        card.appendChild(detailsButton);

        issuesContainer.appendChild(card);
    });
}

// Apply search and filters
document.getElementById("filterBtn").addEventListener(
    "click",
    function () {
        loadIssues();
    }
);

// Refresh issues and statistics
document.getElementById("refreshBtn").addEventListener(
    "click",
    function () {
        loadIssues();
        loadDashboard();
    }
);

// Logout
document.getElementById("logoutBtn").addEventListener(
    "click",
    function () {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_role");
        localStorage.removeItem("user_id");

        window.location.href = "index.html";
    }
);

// Load dashboard when the page opens
if (token && role === "SUPPORT") {
    loadDashboard();
    loadIssues();
}