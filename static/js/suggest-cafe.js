// =========================================
// CONSTANTS
// =========================================
const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
const API_KEY = "";
let searchRequestId = 0;
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
const openingHours = document.querySelector(".opening-hours");
const openingHoursContent = openingHours.querySelector(".section-content");
const openingHoursSectionButton = openingHours.querySelector(".section-toggle");
const openingHoursArrow = openingHoursSectionButton.querySelector(".section-arrow");
const openingHoursStatus = openingHours.querySelector(".section-status");
const openingDays = document.querySelectorAll(".opening-day");
const openingHoursContinueButton = openingHours.querySelector(".continue-btn");

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

function resetOpeningHours() {

    openingDays.forEach(day => {
        const openingInterval = day.querySelectorAll(".opening-interval");
        openingInterval.forEach(interval => {
            const removeButton = interval.querySelector(".opening-interval-remove");

            if (removeButton) {
                removeButton.click();
            }
        })

        const radioInputs = day.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(radio => {
            radio.checked = false;
        });

    });

    days.forEach(dayName => {
        const openingTimeInput = document.querySelector(`input[name="${dayName}-open"]`);
        const closingTimeInput = document.querySelector(`input[name="${dayName}-close"]`);

        openingTimeInput.value = "";
        closingTimeInput.value = "";
    });


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
function showOpeningHoursForm() {
    if (!openingHours.classList.contains("is-hidden")) {
        return;
    }

    openingHours.classList.remove("is-hidden");
}

function toggleOpeningHoursForm() {
    openingHoursContent.classList.toggle("is-hidden");
    openingHours.classList.toggle("is-collapsed");

    if (openingHoursContent.classList.contains("is-hidden")) {
        openingHoursArrow.textContent = "▶";
    } else {
        openingHoursArrow.textContent = "▼";
    }
}

function validateOpeningHoursForm() {
    openingDays.forEach(day => {
        const radioOpenInput = day.querySelector("input[value='open']");
        const timeInputs = day.querySelectorAll(".opening-interval input");

        if (radioOpenInput.checked) {
            timeInputs.forEach(timeInput => {
                timeInput.required = true;
            });

        } else {
            timeInputs.forEach(timeInput => {
                timeInput.required = false;
            });
        }
    });

    for (const day of openingDays) {
        const radioOpenInput = day.querySelector("input[value='open']");
        const openingTimeInputs = day.querySelectorAll("input[name$='-open']");
        const closingTimeInputs = day.querySelectorAll("input[name$='-close']");

        if (!radioOpenInput.checked) {
            continue;
        }

        for (let i = 0; i < openingTimeInputs.length; i++) {
            openingTimeInputs[i].setCustomValidity("");

            const openingTime = openingTimeInputs[i].value;
            const closingTime = closingTimeInputs[i].value;

            if (openingTime && closingTime && openingTime >= closingTime) {
                openingTimeInputs[i].setCustomValidity(
                    "Opening time must be earlier than closing time."
                );
                openingTimeInputs[i].reportValidity();
                openingHoursStatus.textContent = "❌ ";
                return false;
            }

            if (i > 0) {
                const previousClosingTime = closingTimeInputs[i - 1].value;

                if (openingTime < previousClosingTime) {
                    openingTimeInputs[i].setCustomValidity(
                        "Opening intervals must not overlap."
                    );
                    openingTimeInputs[i].reportValidity();
                    openingHoursStatus.textContent = "❌ ";
                    return false;
                }
            }
        }
    }

    const requiredFields = openingHours.querySelectorAll("input[required]");

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            openingHoursStatus.textContent = "❌ ";
            return false;
        }
    }


    openingHoursStatus.textContent = "✔️ ";

    return true;
}

initializeLocation();

// =========================================
// EVENT-LISTENERS
// =========================================

//================ CAFE-SUGGESTION ================
searchInput.addEventListener("input", async () => {
    //================ CAFE-SUGGESTION ================
    const text = searchInput.value.trim();

    if (text.length < 3) {
        suggestions.style.display = "none";
        suggestions.innerHTML = "";
        return;
    }

    const requestId = ++searchRequestId;

    let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&type=amenity&filter=countrycode:cz&limit=20&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        url += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (requestId !== searchRequestId) {
            return;
        }

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

                    searchRequestId++;

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

                    resetOpeningHours();
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

                        intervals.forEach(([start, end]) => {  //„Projdi každý interval. Z něj si vezmi začátek a konec. Podívej se podle začátku, kterému dni patří. Najdi v našem rozvrhu tento den a přidej do něj začátek a konec ve formátu HH:MM.“
                            const day = days[start.getDay()]; //Jaký den v týdnu je toto datum? Vrati napr. 1

                            openingSchedule[day].push({
                                open: formatTime(start),
                                close: formatTime(end)
                            });
                        });

                        days.forEach(day => {
                            openingSchedule[day].forEach((schedule, index) => {
                                const openingDay = document.querySelector(`[data-day="${day}"]`);

                                const openRadio = openingDay.querySelector(`input[name="${day}"][value="open"]`);
                                openRadio.click();

                                const addButton = openingDay.querySelector(".opening-interval-add")

                                if (index > 0) {
                                    addButton.click();
                                }

                                const openingTimeInputs = openingDay.querySelectorAll(`input[name="${day}-open"]`);
                                const closingTimeInputs = openingDay.querySelectorAll(`input[name="${day}-close"]`);

                                openingTimeInputs[index].value = schedule.open;
                                closingTimeInputs[index].value = schedule.close;
                            });


                        });

                    }
                    showInformationForm();
                });

                suggestions.appendChild(item);
            }
        });

        suggestions.style.display = cafeFound ? "block" : "none";

    } catch (error) {
        console.error("Autocomplete request failed:", error);
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
openingHoursSectionButton.addEventListener("click", toggleOpeningHoursForm);

openingHoursContinueButton.addEventListener("click", () => {
    if (!validateOpeningHoursForm()) {
        return;
    }

    toggleOpeningHoursForm();
})

openingDays.forEach(day => {
    const statusRadios = day.querySelectorAll('input[type="radio"]');
    const openingInterval = day.querySelector(".opening-interval");
    const openingIntervals = day.querySelector(".opening-intervals");
    const addButton = day.querySelector(".opening-interval-add");

    statusRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            const allOpeningIntervals = day.querySelectorAll(".opening-interval");

            if (radio.value === "open") {
                allOpeningIntervals.forEach(interval => {
                    interval.classList.remove("is-hidden");
                });

            } else {
                allOpeningIntervals.forEach(interval => {
                    interval.classList.add("is-hidden");
                });
            }
        });
    });

    addButton.addEventListener("click", () => {
        const newInterval = openingInterval.cloneNode(true);
        const newOpeningTime = newInterval.querySelector("input[name$='-open']");
        const newClosingTime = newInterval.querySelector("input[name$='-close']");
        const removeButton = newInterval.querySelector(".opening-interval-add");

        removeButton.textContent = "-";
        removeButton.classList.remove("opening-interval-add");
        removeButton.classList.add("opening-interval-remove");

        newOpeningTime.value = "";
        newClosingTime.value = "";

        addButton.classList.add("is-hidden");

        removeButton.addEventListener("click", () => {
            newInterval.remove();
            addButton.classList.remove("is-hidden");
        });

        openingIntervals.append(newInterval);
    });
});





