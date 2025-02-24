document.querySelectorAll(".metric-section-header").forEach(header => {
    header.addEventListener("click", function() {
        let content = this.nextElementSibling;

        if (content.style.maxHeight && content.style.maxHeight !== "0px") {
            content.style.maxHeight = "0px";
            content.style.padding = "0 10px";
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            content.style.padding = "10px";
        }
    });
});