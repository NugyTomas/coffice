// =========================================
// CONSTANTS
// =========================================

//================ CAFE-SUGGESTION ================
const searchInput = document.getElementById("cafe-search-input");
const suggestions = document.querySelector(".cafe-suggestions");
const manualCafeButton = document.querySelector(".manual-cafe-button");

//================ BASIC-INFORMATION ================
const cafeName = document.getElementById("cafe-name");
const cafeCity = document.getElementById("cafe-city");
const cafeAddress = document.getElementById("cafe-address");
const cafePostCode = document.getElementById("cafe-postal-code");
const cafePhone = document.getElementById("cafe-phone");
const cafeEmail = document.getElementById("cafe-email");
const cafeWebsite = document.getElementById("cafe-website");

const information = document.querySelector(".cafe-basic-information");
const informationContent = information.querySelector(".section-content");
const informationSectionButton = information.querySelector(".section-toggle");
const informationStatus = informationSectionButton.querySelector(".section-status");
const informationArrow = informationSectionButton.querySelector(".section-arrow");
const informationContinueButton = information.querySelector(".continue-btn");

//================ FEATURES ================
const features = document.querySelector(".work-friendly-features");
const featuresContent = features.querySelector(".section-content");
const featuresSectionButton = features.querySelector(".section-toggle");
const featuresStatus = featuresSectionButton.querySelector(".section-status");
const featuresArrow = featuresSectionButton.querySelector(".section-arrow");
const featuresContinueButton = features.querySelector(".continue-btn");


const API_KEY = "";

let userLocation = null;

// =========================================
// FUNCTIONS
// =========================================

async function initializeLocation() {
    try {
        userLocation = await getUserLocation();
    } catch (error) {
        console.log("Location unavailable:", error);
    }
}

async function getPlaceDetails(placeId) {
    const url = `https://api.geoapify.com/v2/place-details?id=${placeId}&apiKey=${API_KEY}`;

    const response = await fetch(url);
    return await response.json();
}

//================ BASIC-INFORMATION ================
function showInformationForm() {
    information.classList.remove("is-hidden");
    information.classList.remove("is-collapsed");
    informationContent.classList.remove("is-hidden");
    informationArrow.textContent = "▼";
}

function toggleInformationForm() {
    informationContent.classList.toggle("is-hidden");
    information.classList.toggle("is-collapsed");

    if (informationContent.classList.contains("is-hidden")) {
        informationArrow.textContent = "▶";
    } else {
        informationArrow.textContent = "▼";
    }
}

function validateInformationForm() {
    const requiredFields = information.querySelectorAll(
        "input[required], select[required]"
    );

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            informationStatus.textContent = "❌ ";
            return false;
        }
    }

    informationStatus.textContent = "✔️ ";

    return true;
}

//================ FEATURES ================
function showFeaturesForm() {
    if (!features.classList.contains("is-hidden")) {
        return;
    }

    features.classList.remove("is-hidden");
}

function toggleFeaturesForm() {
    featuresContent.classList.toggle("is-hidden");
    features.classList.toggle("is-collapsed");

    if (featuresContent.classList.contains("is-hidden")) {
        featuresArrow.textContent = "▶";
    } else {
        featuresArrow.textContent = "▼";
    }
}

function validateFeaturesForm() {
    const requiredFields = features.querySelectorAll(
        "input[required]"
    );

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            featuresStatus.textContent = "❌ ";
            return false;
        }
    }

    featuresStatus.textContent = "✔️ ";

    return true;
}

initializeLocation();

// =========================================
// EVENT-LISTENERS
// =========================================

//================ CAFE-SUGGESTION ================
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

            item.addEventListener("click", async () => {
                suggestions.style.display = "none";
                searchInput.value = `${result.name}, ${result.address_line2}`;

                const placeDetails = await getPlaceDetails(result.place_id);
                const cafeDetails = placeDetails.features[0].properties;
                console.log(cafeDetails);

                cafeName.value = cafeDetails.name || "";
                cafeCity.value = cafeDetails.city || "";
                cafeAddress.value = cafeDetails.address_line2?.split(',')[0].trim() || "";
                cafePostCode.value = cafeDetails.postcode || "";

                cafePhone.value = cafeDetails.contact?.phone || "";
                cafeEmail.value = cafeDetails.contact?.email || "";
                cafeWebsite.value = cafeDetails.website || "";

                showInformationForm();
            });

            suggestions.appendChild(item);
        }
    });

    if (cafeFound) {
        suggestions.style.display = "block";
    } else {
        suggestions.style.display = "none";
    }
});

manualCafeButton.addEventListener("click", showInformationForm);

//================ BASIC-INFORMATION ================
informationSectionButton.addEventListener("click", toggleInformationForm);

informationContinueButton.addEventListener("click", () => {
    if (!validateInformationForm()) {
        return;
    }

    showFeaturesForm();
    toggleInformationForm();

});

//================ FEATURES ================
featuresSectionButton.addEventListener("click", toggleFeaturesForm);

featuresContinueButton.addEventListener("click", () => {
    if (!validateFeaturesForm()) {
        return;
    }

    toggleFeaturesForm();
});



