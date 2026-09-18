const uploadBox = document.getElementById("uploadBox");

const imageInput = document.getElementById("imageInput");

const chooseBtn = document.getElementById("chooseBtn");

const preview = document.getElementById("previewImage");

// Open file picker
chooseBtn.onclick = () => imageInput.click();

uploadBox.onclick = () => imageInput.click();

// Preview selected image
imageInput.onchange = function () {

    const file = this.files[0];

    if (file) {

        preview.src = URL.createObjectURL(file);

        preview.style.display = "block";

    }

};

// Let Flask receive the form.
// Do NOT use e.preventDefault().
document.getElementById("foundForm").addEventListener("submit", function () {

    // Optional: disable submit button while uploading

});