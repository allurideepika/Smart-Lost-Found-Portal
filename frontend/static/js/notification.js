console.log("notification.js loaded");
const searchInput = document.getElementById("searchNotification");
const filter = document.getElementById("filterNotification");
const cards = document.querySelectorAll(".notification-item");

// Events
searchInput.addEventListener("keyup", applyFilters);
filter.addEventListener("change", applyFilters);

function applyFilters() {

    const searchText = searchInput.value.trim().toLowerCase();
    const filterValue = filter.value;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    cards.forEach(card => {

        let visible = true;

        const message = card.querySelector(".notification-text")
                            .dataset.message
                            .toLowerCase();

        const cardDate = new Date(card.dataset.date + "T00:00:00");
cardDate.setHours(0, 0, 0, 0);

        // Search
        if (!message.includes(searchText)) {
            visible = false;
        }

        // Filter
        if (visible) {

            switch (filterValue) {

                case "today":

                    visible = cardDate.getTime() === today.getTime();
                    break;

                case "week":

                    const diff =
                        (today - cardDate) / (1000 * 60 * 60 * 24);

                    visible = diff >= 0 && diff <= 7;
                    break;

                case "returned":

                    visible = message.includes("returned");
                    break;

                case "matched":

                    visible = message.includes("matched");
                    break;

                case "approved":

                    visible = message.includes("approved");
                    break;

                case "all":

                default:

                    visible = true;
                    break;
            }

        }

        card.style.display = visible ? "" : "none";

    });

}