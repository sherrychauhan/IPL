let groupedData = []; // Holds data grouped by team
let currentPage = 0;
let boughtPlayers = [];
let boughtPage = 0;

// Handle file input with enhanced error handling
document.getElementById('file-input').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            try {
                const jsonData = JSON.parse(e.target.result); // Parse JSON file

                // Ensure the JSON is an array
                if (!Array.isArray(jsonData)) {
                    throw new Error("The JSON file should contain an array of objects.");
                }

                // Replace NaN/null with "N/A" and group data by 'Team'
                const cleanedData = jsonData.map(item => {
                    const cleanedItem = {};
                    for (const key in item) {
                        cleanedItem[key] = (item[key] === null || String(item[key]) === "NaN") ? "N/A" : item[key];
                    }
                    return cleanedItem;
                });

                groupedData = groupBy(cleanedData, 'Team');
                currentPage = 0;
                renderTable();
                updatePaginationButtons();
                document.getElementById('save-btn').disabled = false; // Enable Save button
            } catch (error) {
                // Display meaningful error messages for invalid JSON
                alert(`Error loading JSON file: ${error.message}`);
            }
        };
        reader.onerror = function () {
            alert("Failed to read the file. Please try again.");
        };
        reader.readAsText(file); // Read file as text
    }
});

// Group data by a specific field
function groupBy(data, key) {
    return Object.values(data.reduce((result, current) => {
        const groupKey = current[key] || "Unknown";
        if (!result[groupKey]) {
            result[groupKey] = [];
        }
        result[groupKey].push(current);
        return result;
    }, {}));
}

// Render the main data table
function renderTable() {
    const tbody = document.querySelector("#data-table tbody");
    tbody.innerHTML = "";

    const currentGroup = groupedData[currentPage] || [];
    currentGroup.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item["Sr. No"]}</td>
            <td>${item["Player"]}</td>
            <td>${item["Team"]}</td>
            <td contenteditable="true" oninput="updateField(${currentPage}, ${item["Sr. No"]}, 'Role', this.textContent)">${item["Role"]}</td>
            <td>${item["International"]}</td>
            <td contenteditable="true" oninput="updateField(${currentPage}, ${item["Sr. No"]}, 'Bought by', this.textContent)">${item["Bought by"]}</td>
            <td contenteditable="true" oninput="updateField(${currentPage}, ${item["Sr. No"]}, 'Points', this.textContent)">${item["Points"]}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update a specific field in groupedData
function updateField(page, srNo, field, value) {
    const group = groupedData[page];
    const item = group.find(record => record["Sr. No"] === srNo);
    if (item) {
        item[field] = value;
    }
}

// Update pagination buttons
function updatePaginationButtons() {
    document.getElementById("prev-btn").disabled = currentPage === 0;
    document.getElementById("next-btn").disabled = currentPage === groupedData.length - 1;
}

// Pagination button handlers for main data table
document.getElementById("prev-btn").addEventListener("click", () => {
    if (currentPage > 0) {
        currentPage--;
        renderTable();
        updatePaginationButtons();
    }
});

document.getElementById("next-btn").addEventListener("click", () => {
    if (currentPage < groupedData.length - 1) {
        currentPage++;
        renderTable();
        updatePaginationButtons();
    }
});
