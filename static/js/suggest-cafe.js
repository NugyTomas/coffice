const searchInput = document.getElementById("cafe-search-input");
const suggestions = document.querySelector(".cafe-suggestions");

const API_KEY = "";

let userLocation = null;

async function initializeLocation() {
    try {
        userLocation = await getUserLocation();
    } catch (error) {
        console.log("Location unavailable:", error);
    }
}

initializeLocation();

searchInput.addEventListener("input", async () => {
    const text = searchInput.value.trim();

    if (text.length < 3) {
        suggestions.style.display = "none";
        return;
    }

    let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&type=amenity&filter=countrycode:cz&limit=20&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        url += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    const response = await fetch(url);
    const data = await response.json();

    suggestions.innerHTML = "";

    let cafeFound = false;

    data.results.forEach(result => {

        if (result.category === 'catering.cafe') {
            cafeFound = true;

            const item = document.createElement("div");
            item.classList.add("suggestion-item");
            item.innerHTML = `<strong>${result.name}</strong>,<small>${result.address_line2}</small>`;
            item.addEventListener("click", () => {
                console.log("Selected cafe:", result.name)
                console.log(result.place_id);
                suggestions.style.display = "none";
                searchInput.value = `${result.name}, ${result.address_line2}`;
            });

            suggestions.appendChild(item);
        }
    });

    if (cafeFound) {
        suggestions.style.display = "block";
    } else {
        suggestions.style.display = "none"
    }
})


