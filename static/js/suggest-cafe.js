// =========================================
// CONSTANTS
// =========================================

//================ CAFE-SUGGESTION ================
const searchInput = document.getElementById("cafe-search-input");
const suggestions = document.querySelector(".cafe-suggestions");
const manualCafeDiv = document.querySelector(".manual-cafe")
const manualCafeButton = document.querySelector(".manual-cafe-button");

const formSection = document.querySelector(".form-section");
//================ CAFE-BASIC-INFORMATION ================
const cafeName = document.getElementById("cafe-name");
const cafeCity = document.getElementById("cafe-city");
const cafeAddress = document.getElementById("cafe-address");
const cafePostCode = document.getElementById("cafe-postal-code");
const cafePhone = document.getElementById("cafe-phone");
const cafeEmail = document.getElementById("cafe-email");
const cafeWebsite = document.getElementById("cafe-website")

const cafeInformation = document.querySelector(".cafe-basic-information");
const cafeInformationSection = cafeInformation.querySelector(".section-content");
const cafeInformationSectionButton = cafeInformation.querySelector(".section-toggle")
const cafeInformationSectionArrow = cafeInformationSectionButton.querySelector("span");
const cafeInformationContinueButton = cafeInformation.querySelector(".continue-btn")

//================ CAFE-FEATURES ================
const cafeFeatures = document.querySelector(".work-friendly-features");
const cafeFeaturesSection = cafeFeatures.querySelector(".section-content");
const cafeFeaturesSectionButton = cafeFeatures.querySelector(".section-toggle");
const cafeFeaturesSectionArrow = cafeFeaturesSectionButton.querySelector("span");


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
    const urlForPlaceDetails = `https://api.geoapify.com/v2/place-details?id=${placeId}&apiKey=${API_KEY}`;

    const responseForPlaceDetails = await fetch(urlForPlaceDetails);
    const dataForPlaceDetails = await responseForPlaceDetails.json();

    return dataForPlaceDetails;
}

//================ CAFE-BASIC-INFORMATION ================
function showCafeInformationForm() {
    cafeInformation.classList.remove("is-hidden");
    manualCafeDiv.style.display = "none";
}

function toggleBasicInformationForm() {
    cafeInformationSection.classList.toggle("is-hidden");
    formSection.classList.toggle("is-collapsed")

    if (cafeInformationSection.classList.contains("is-hidden")) {
        cafeInformationSectionArrow.textContent = "▶";
    } else {
        cafeInformationSectionArrow.textContent = "▼";
    }
}

function toggleCafeFeaturesForm() {
    cafeFeaturesSection.classList.toggle("is-hidden");
    cafeFeatures.classList.toggle("is-collapsed");

    if (cafeFeaturesSection.classList.contains("is-hidden")) {
        cafeFeaturesSectionArrow.textContent = "▶";
    } else {
        cafeFeaturesSectionArrow.textContent = "▼";
    }
}

function validateBasicInformation() {
    const requiredFields = cafeInformation.querySelectorAll(
        "input[required], select[required]"
    );

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            return false;
        }
    }

    if (!cafeInformationSectionButton.textContent.includes("✔️")) {
        cafeInformationSectionButton.prepend("✔️ ")
    }

    return true;
}

//================ CAFE-FEATURES ================
function showFeatureInformationForm() {
    cafeFeatures.classList.remove("is-hidden");
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

    let urlForAutoComplete = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&type=amenity&filter=countrycode:cz&limit=20&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        urlForAutoComplete += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    const responseForAutoComplete = await fetch(urlForAutoComplete);
    const dataForAutoComplete = await responseForAutoComplete.json();

    suggestions.innerHTML = "";

    let cafeFound = false;

    dataForAutoComplete.results.forEach(result => {

        if (result.category === 'catering.cafe') {
            cafeFound = true;
            const item = document.createElement("div");
            item.classList.add("suggestion-item");
            item.innerHTML = `<strong>${result.name}</strong>,<small>${result.address_line2}</small>`;

            item.addEventListener("click", async () => {
                suggestions.style.display = "none";
                searchInput.value = `${result.name}, ${result.address_line2}`;

                const dataForPlaceDetail = await getPlaceDetails(result.place_id)
                const cafeDetails = dataForPlaceDetail.features[0].properties
                console.log(cafeDetails)

                cafeName.value = cafeDetails.name || "";
                cafeCity.value = cafeDetails.city || "";
                cafeAddress.value = cafeDetails.address_line2?.split(',')[0].trim() || "";
                cafePostCode.value = cafeDetails.postcode || "";

                cafePhone.value = cafeDetails.contact?.phone || "";
                cafeEmail.value = cafeDetails.contact?.email || "";
                cafeWebsite.value = cafeDetails.website || "";

                showCafeInformationForm();
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
manualCafeButton.addEventListener("click", showCafeInformationForm);

//================ CAFE-BASIC-INFORMATION ================
cafeInformationSectionButton.addEventListener("click", toggleBasicInformationForm);
cafeInformationContinueButton.addEventListener("click", () => {
    if (!validateBasicInformation()) {
        return;
    }

    showFeatureInformationForm();
    toggleBasicInformationForm();

});

//================ CAFE-FEATURES ================
cafeFeaturesSectionButton.addEventListener("click", toggleCafeFeaturesForm);


