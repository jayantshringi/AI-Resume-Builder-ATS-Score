document.querySelectorAll(".color-dot").forEach(dot => {
    dot.addEventListener("click", () => {
        document.querySelectorAll(".color-dot").forEach(x => {
            x.style.outline = "none";
        });

        dot.style.outline = "3px solid #fff";
    });
});

document.querySelectorAll(".template-option").forEach(option => {
    option.addEventListener("click", () => {
        document.querySelectorAll(".template-option").forEach(x => {
            x.classList.remove("selected");
        });

        option.classList.add("selected");
    });
});