const uploadBox = document.getElementById("uploadBox");
const imageInput = document.getElementById("imageInput");
const chooseBtn = document.getElementById("chooseBtn");
const preview = document.getElementById("previewImage");
const noImage = document.getElementById("noImage");

// Open file picker
chooseBtn.onclick = (e) => {
    e.stopPropagation();

    if (!noImage.checked) {
        imageInput.click();
    }
};

// Open file picker when upload box is clicked
uploadBox.onclick = () => {

    if (!noImage.checked) {
        imageInput.click();
    }

};

// Show image preview
imageInput.onchange = function () {

    const file = this.files[0];

    if (file) {

        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";

    }

};

// Handle "No Photo" checkbox
noImage.addEventListener("change", function () {

    if (this.checked) {

        // Clear selected image
        imageInput.value = "";

        // Disable image input
        imageInput.disabled = true;

        // Hide preview
        preview.style.display = "none";

        // Disable upload UI
        uploadBox.style.opacity = "0.5";
        uploadBox.style.cursor = "not-allowed";
        chooseBtn.disabled = true;

    } else {

        // Enable upload again
        imageInput.disabled = false;

        uploadBox.style.opacity = "1";
        uploadBox.style.cursor = "pointer";
        chooseBtn.disabled = false;

    }

});

// Allow Flask to submit the form normally
document.getElementById("lostForm").addEventListener("submit", function () {

    // Nothing required here

});