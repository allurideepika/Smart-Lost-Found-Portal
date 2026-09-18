const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");

function filterCards() {

    const search = searchInput.value.toLowerCase();
    const category = categoryFilter.value.toLowerCase();

    const cards = document.querySelectorAll(".item-card");

    cards.forEach(card => {

        const text = card.innerText.toLowerCase();
        const cardCategory = card.dataset.category.toLowerCase();

        const searchMatch = text.includes(search);
        const categoryMatch =
            category === "" || cardCategory === category;

        if (searchMatch && categoryMatch) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }

    });

}

searchInput.addEventListener("keyup", filterCards);
categoryFilter.addEventListener("change", filterCards);