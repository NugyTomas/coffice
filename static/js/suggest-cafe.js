// =========================================
// CONSTANTS
// =========================================
const API_KEY = "";
let userLocation = null;

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

const information = document.querySelector(".basic-information");
const informationContent = information.querySelector(".section-content");
const informationSectionButton = information.querySelector(".section-toggle");
const informationStatus = informationSectionButton.querySelector(".section-status");
const informationArrow = informationSectionButton.querySelector(".section-arrow");
const informationContinueButton = information.querySelector(".continue-btn");

//================ FEATURES ================
const features = document.querySelector(".features");
const featuresContent = features.querySelector(".section-content");
const featuresSectionButton = features.querySelector(".section-toggle");
const featuresStatus = featuresSectionButton.querySelector(".section-status");
const featuresArrow = featuresSectionButton.querySelector(".section-arrow");
const cardPayment = document.getElementById("card-yes");
const featuresContinueButton = features.querySelector(".continue-btn");

//================ OPENING-HOURS ================
const openingDays = document.querySelectorAll(".opening-day");

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

function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${hours}:${minutes}`;
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

//================ OPENING-HOURS ================

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

                const cafeAcceptsCards = !!(
                    cafeDetails.payment_options?.debit_cards ||
                    cafeDetails.payment_options?.credit_cards
                );
                cardPayment.checked = cafeAcceptsCards;


                const cafeOpeningHours = cafeDetails.opening_hours

                if (cafeOpeningHours) {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const nextWeek = new Date(today);
                    nextWeek.setDate(today.getDate() + 7);

                    const openingHours = new opening_hours(cafeOpeningHours);
                    const intervals = openingHours.getOpenIntervals(today, nextWeek);

                    const openingSchedule = {
                        monday: [],
                        tuesday: [],
                        wednesday: [],
                        thursday: [],
                        friday: [],
                        saturday: [],
                        sunday: []
                    };
                    const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];

                    intervals.forEach(([start, end]) => {  //„Projdi každý interval. Z něj si vezmi začátek a konec. Podívej se podle začátku, kterému dni patří. Najdi v našem rozvrhu tento den a přidej do něj začátek a konec ve formátu HH:MM.“
                        const day = days[start.getDay()]; //Jaký den v týdnu je toto datum? Vrati napr. 1

                        openingSchedule[day].push({
                            open: formatTime(start),
                            close: formatTime(end)
                        });
                    });

                    days.forEach(day => {
                        const openingDay = document.querySelector(`[data-day="${day}"]`);
                        const openingTimeInputs = openingDay.querySelectorAll(`input[name="${day}-open"]`);
                        const closingTimeInputs = openingDay.querySelectorAll(`input[name="${day}-close"]`);

                        openingTimeInputs.forEach(openingTimeInput => {
                            openingTimeInput.value = openingSchedule[day][0].open;
                        })

                        closingTimeInputs.forEach(closingTimeInput => {
                            closingTimeInput.value = openingSchedule[day][0].close;
                        })

                    });

                }

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

//================ OPENING-HOURS ================
openingDays.forEach(day => {
    const dayRadios = day.querySelectorAll('input[type="radio"]');
    const openingInterval = day.querySelector(".opening-interval");
    const openingIntervals = day.querySelector(".opening-intervals");
    const addButton = day.querySelector(".opening-interval-add");

    dayRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "open") {
                openingInterval.classList.remove("is-hidden");
            } else {
                openingInterval.classList.add("is-hidden");
            }
        });
    });

    addButton.addEventListener("click", () => {
        const newInterval = openingInterval.cloneNode(true);
        const newAddButton = newInterval.querySelector(".opening-interval-add");

        newAddButton.textContent = "-";
        addButton.classList.add("is-hidden");

        newAddButton.addEventListener("click", () => {
            newInterval.remove();
            addButton.classList.remove("is-hidden");
        });

        openingIntervals.append(newInterval);
    });
});



