const input = document.getElementById("resume");
const nameBox = document.getElementById("filename");
const form = document.getElementById("atsForm");
const button = document.getElementById("checkBtn");

if (input) {
    input.addEventListener("change", () => {
        nameBox.textContent = input.files.length
            ? "Selected: " + input.files[0].name
            : "";
    });
}

if (form) {
    form.addEventListener("submit", () => {
        button.textContent = "Analyzing Resume...";
        button.disabled = true;
    });
}