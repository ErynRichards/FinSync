document.addEventListener("DOMContentLoaded", function() {
    // mobile navigation menu
    const menuToggle= document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", function() {
            const isOpen = navLinks.classList.toggle("active");
            menuToggle.setAttribute(
            "aria-expanded",
            String(isOpen)
            );
            
        });
        
        // close menu after clicking a navigation Link
        navLinks.querySelectorAll("a").forEach(function (link){
            link.addEventListener("click", function(){
                navLinks.classList.remove("active");
                menuToggle.setAttribute("aria-expanded", "false");
            });
        });
    }
    // automatically update footer year
    const year = document.getElementById("year");
    if (year) {
        year.textContent = new Date().getFullYear();
    }
});