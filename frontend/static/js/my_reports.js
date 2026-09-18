// Get elements
const searchInput = document.getElementById("searchInput");
const filterType = document.getElementById("filterType");
const searchBtn = document.getElementById("searchBtn");

// Function to filter reports
function filterReports() {

    const searchText = searchInput.value.trim().toLowerCase();
    const selectedType = filterType.value;

    const rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {

        // Get item name
        const itemName = row.querySelector(".item-name").innerText.toLowerCase();

        // Get row type (Lost / Found)
        const rowType = row.dataset.type;

        // Check search text
        const matchesSearch = itemName.includes(searchText);

        // Check filter
        const matchesFilter =
            selectedType === "All" ||
            rowType === selectedType;

        // Show or Hide row
        if (matchesSearch && matchesFilter) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

}

// Search button click
searchBtn.addEventListener("click", filterReports);

// Filter dropdown change
filterType.addEventListener("change", filterReports);

// Search while typing
searchInput.addEventListener("keyup", filterReports);