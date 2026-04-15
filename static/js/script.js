// Leaflet Map
var map = L.map('map').setView([19.0760, 72.8777], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);

// GPS User Location
navigator.geolocation.getCurrentPosition(function(position) {
    let lat = position.coords.latitude;
    let lon = position.coords.longitude;

    map.setView([lat, lon], 14);

    L.marker([lat, lon]).addTo(map)
        .bindPopup("You are here")
        .openPopup();
});

// Sample Parking Marker
L.marker([19.0760, 72.8777]).addTo(map)
    .bindPopup("Parking Available Here");

// Mobile Navbar
const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");

menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");
});

// Scroll Reveal
const reveals = document.querySelectorAll(".reveal");

window.addEventListener("scroll", () => {
    reveals.forEach(section => {
        const top = section.getBoundingClientRect().top;
        if (top < window.innerHeight - 100) {
            section.classList.add("active");
        }
    });
});

// Typing Hero Effect
const heroText = document.querySelector(".hero-content h1");
const text = "Find Smart Parking Near You Instantly";
let index = 0;

heroText.innerHTML = "";

function typeText() {
    if(index < text.length){
        heroText.innerHTML += text.charAt(index);
        index++;
        setTimeout(typeText, 60);
    }
}

typeText();