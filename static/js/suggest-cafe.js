// =========================================
// CONFIG
// =========================================
const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
const API_KEY = "";

// =========================================
// STATE
// =========================================
let userLocation = null;
let searchRequestId = 0;
let addressSearchRequestId = 0;
let autocompleteController = null;
let placeDetailsController = null;
let addressAutocompleteController = null;
let cafeLatitude = null;
let cafeLongitude = null;
let selectedPhotos = [];

// =========================================
// DOM REFERENCES
// =========================================

//================ CAFE-SUGGESTION ================
const searchInput = document.getElementById("cafe-search-input");
const suggestions = document.querySelector(".cafe-suggestions");
const manualCafeButton = document.querySelector(".manual-cafe-button");

//================ BASIC-INFORMATION ================
const cafeName = document.getElementById("cafe-name");
const cafeCity = document.getElementById("cafe-city");
const cafeAddress = document.getElementById("cafe-address");
const cafeAddressSuggestions = document.querySelector(".cafe-address-suggestions");
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
const openingHoursStatus = openingHours.querySelector(".section-status");
const openingHoursArrow = openingHoursSectionButton.querySelector(".section-arrow");
const openingDays = document.querySelectorAll(".opening-day");
const openingHoursContinueButton = openingHours.querySelector(".continue-btn");

//================ FINAL-REVIEW ================
const finalReview = document.querySelector(".final-review");
const finalReviewContent = finalReview.querySelector(".section-content");
const finalReviewSectionButton = finalReview.querySelector(".section-toggle");
const finalReviewStatus = finalReview.querySelector(".section-status");
const finalReviewArrow = finalReview.querySelector(".section-arrow");
const photoPreviewContainer = document.querySelector(".photo-preview-container");
const finalReviewContinueButton = finalReview.querySelector(".continue-btn");
const photoInput = document.getElementById("cafe-photo-input");
const finalWarning = document.querySelector(".final-warning");
const finalWarningSubmitButton = document.querySelector(".submit-btn");

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

async function getPlaceDetails(placeId, signal) {
    const url = `https://api.geoapify.com/v2/place-details?id=${placeId}&apiKey=${API_KEY}`;

    const response = await fetch(url, {signal: signal});
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
            const removeIntervalButton = interval.querySelector(".opening-interval-remove");

            if (removeIntervalButton) {
                removeIntervalButton.click();
            }
        })

        const radioButtons = day.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
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

function formatPhoneNumber(phoneNumber) {
    if (!phoneNumber) {
        return "";
    }

    phoneNumber = phoneNumber.replace("+420", "");
    phoneNumber = phoneNumber.replace(/\D/g, "");
    phoneNumber = phoneNumber.slice(0, 9);

    if (phoneNumber.length > 6) {
        phoneNumber = phoneNumber.slice(0, 3) + " " +
            phoneNumber.slice(3, 6) + " " +
            phoneNumber.slice(6);
    } else if (phoneNumber.length > 3) {
        phoneNumber = phoneNumber.slice(0, 3) + " " +
            phoneNumber.slice(3);
    }

    return phoneNumber;
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

    if (cafePhone.value !== "" && !cafePhone.checkValidity()) {
        cafePhone.reportValidity();
        informationStatus.textContent = "❌ ";
        return false;
    }

    if (cafeEmail.value !== "" && !cafeEmail.checkValidity()) {
        cafeEmail.reportValidity();
        informationStatus.textContent = "❌ ";
        return false;
    }


    informationStatus.textContent = "✔️ ";
    return true;
}

//================ FEATURES ================
function showFeaturesForm() {
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

    for (const day of openingDays) {
        const radioOpenButton = day.querySelector("input[value='open']");
        const timeInputs = day.querySelectorAll(".opening-interval input");
        const openingTimeInputs = day.querySelectorAll("input[name$='-open']");
        const closingTimeInputs = day.querySelectorAll("input[name$='-close']");

        if (radioOpenButton.checked) {
            timeInputs.forEach(timeInput => {
                timeInput.required = true;
            });

        } else {
            timeInputs.forEach(timeInput => {
                timeInput.required = false;
            });
        }

        if (!radioOpenButton.checked) {
            continue;
        }

        for (let i = 0; i < openingTimeInputs.length; i++) {
            openingTimeInputs[i].setCustomValidity("");

            const openingTime = openingTimeInputs[i].value;
            const closingTime = closingTimeInputs[i].value;


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

//================ FINAL-REVIEW ================
function showFinalReviewForm() {
    finalReview.classList.remove("is-hidden");
}

function toggleFinalReviewForm() {
    finalReviewContent.classList.toggle("is-hidden");
    finalReview.classList.toggle("is-collapsed");

    if (finalReviewContent.classList.contains("is-hidden")) {
        finalReviewArrow.textContent = "▶";
    } else {
        finalReviewArrow.textContent = "▼";
    }
}

function renderPhotoPreviews() {
    photoPreviewContainer.innerHTML = "";

    selectedPhotos.forEach((file, index) => {
        const photoContainer = document.createElement("div");
        photoContainer.classList.add("photo-preview");

        const image = document.createElement("img");
        image.src = URL.createObjectURL(file);

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.textContent = "x";

        removeButton.addEventListener("click", () => {
            selectedPhotos.splice(index, 1);
            renderPhotoPreviews();
        });

        photoContainer.appendChild(image);
        photoContainer.appendChild(removeButton);

        photoPreviewContainer.appendChild(photoContainer);
    });
}

function validateFinalReviewForm() {
    const requiredFields = finalReview.querySelectorAll("input[required]")

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            console.log(field);
            console.log(field.validity.valid);
            field.reportValidity();
            finalReviewStatus.textContent = "❌ ";
            return false;
        }
    }

    finalReviewStatus.textContent = "✔️ ";
    return true;
}

function validateSuggestionForm() {
    return !!(validateInformationForm() & validateFeaturesForm() & validateOpeningHoursForm() & validateFinalReviewForm());
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

    if (autocompleteController) {
        autocompleteController.abort();
    }

    autocompleteController = new AbortController();

    const requestId = ++searchRequestId;

    let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&type=amenity&filter=countrycode:cz&limit=20&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        url += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    try {
        const response = await fetch(url, {signal: autocompleteController.signal});
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
                    searchRequestId++;

                    suggestions.style.display = "none";
                    searchInput.value = `${result.name}, ${result.address_line2}`;

                    if (placeDetailsController) {
                        placeDetailsController.abort();
                    }

                    placeDetailsController = new AbortController();

                    try {
                        const placeDetails = await getPlaceDetails(result.place_id, placeDetailsController.signal);

                        if (!placeDetails.features || placeDetails.features.length === 0) {
                            console.error("No place details found.");
                        }

                        const cafeDetails = placeDetails.features[0].properties;
                        console.log(cafeDetails);

                        cafeName.value = cafeDetails.name || "";
                        cafeCity.value = cafeDetails.city || "";
                        cafeAddress.value = cafeDetails.address_line2?.split(',')[0].trim() || "";
                        cafePostCode.value = cafeDetails.postcode || "";
                        cafePhone.value = formatPhoneNumber(cafeDetails.contact?.phone) || "";
                        cafeEmail.value = cafeDetails.contact?.email || "";
                        cafeWebsite.value = cafeDetails.website || "";

                        const cafeAcceptsCards = !!(
                            cafeDetails.payment_options?.debit_cards ||
                            cafeDetails.payment_options?.credit_cards
                        );
                        cardPayment.checked = cafeAcceptsCards;

                        resetOpeningHours();
                        const cafeOpeningHours = cafeDetails.opening_hours;
                        if (cafeOpeningHours) {
                            const today = new Date();
                            today.setHours(0, 0, 0, 0);

                            const nextWeek = new Date(today);
                            nextWeek.setDate(today.getDate() + 7);

                            const queryStart = new Date(today);
                            queryStart.setDate(queryStart.getDate() - 1);

                            const queryEnd = new Date(today);
                            queryEnd.setDate(queryEnd.getDate() + 8);

                            const openingHours = new opening_hours(cafeOpeningHours);
                            const intervals = openingHours.getOpenIntervals(queryStart, queryEnd);

                            const openingSchedule = {
                                monday: [],
                                tuesday: [],
                                wednesday: [],
                                thursday: [],
                                friday: [],
                                saturday: [],
                                sunday: []
                            };

                            const mergedIntervals = [];

                            intervals.forEach(([start, end]) => {
                                const last = mergedIntervals[mergedIntervals.length - 1];
                                if (last && last[1].getTime() === start.getTime()) {
                                    last[1] = end;
                                } else {
                                    mergedIntervals.push([start, end]);
                                }
                            });

                            const relevantIntervals = [];
                            mergedIntervals.forEach(interval => {
                                const start = interval[0];

                                if (start >= today && start < nextWeek) {
                                    relevantIntervals.push(interval);
                                }

                            });

                            relevantIntervals.forEach(([start, end]) => {
                                const day = days[start.getDay()];

                                openingSchedule[day].push({
                                    open: formatTime(start),
                                    close: formatTime(end)
                                });
                            });


                            days.forEach(day => {
                                openingSchedule[day].forEach((schedule, index) => {
                                    const openingDayElement = document.querySelector(`[data-day="${day}"]`);

                                    const openRadioButton = openingDayElement.querySelector(`input[name="${day}"][value="open"]`);
                                    openRadioButton.click();

                                    const addIntervalButton = openingDayElement.querySelector(".opening-interval-add")

                                    if (index > 0) {
                                        addIntervalButton.click();
                                    }

                                    const openingTimeInputs = openingDayElement.querySelectorAll(`input[name="${day}-open"]`);
                                    const closingTimeInputs = openingDayElement.querySelectorAll(`input[name="${day}-close"]`);

                                    openingTimeInputs[index].value = schedule.open;
                                    closingTimeInputs[index].value = schedule.close;
                                });


                            });

                        }
                    } catch (error) {
                        if (error.name !== "AbortError") {
                            console.error("Failed to get place details:", error);
                        }
                    }
                    showInformationForm();
                });

                suggestions.appendChild(item);
            }
        });

        suggestions.style.display = cafeFound ? "block" : "none";

    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Autocomplete request failed:", error);
        }
    }
});

manualCafeButton.addEventListener("click", showInformationForm);

//================ BASIC-INFORMATION ================
informationSectionButton.addEventListener("click", toggleInformationForm);

cafeAddress.addEventListener("input", async () => {
    const text = cafeAddress.value.trim();

    if (text.length < 3) {
        cafeAddressSuggestions.style.display = "none";
        cafeAddressSuggestions.innerHTML = "";
        return;
    }

    if (addressAutocompleteController) {
        addressAutocompleteController.abort();
    }

    addressAutocompleteController = new AbortController();

    const requestId = ++addressSearchRequestId;

    let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&filter=countrycode:cz&limit=5&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        url += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    try {
        const response = await fetch(url, {signal: addressAutocompleteController.signal});
        const data = await response.json();

        if (requestId !== addressSearchRequestId) {
            return;
        }
        cafeAddressSuggestions.innerHTML = "";

        let cafeAddressFound = false;

        data.results.forEach(result => {

            cafeAddressFound = true;
            const item = document.createElement("div");
            item.classList.add("suggestion-item");
            item.innerHTML = `<strong>${result.formatted}</strong>`;

            item.addEventListener("click", async () => {
                addressSearchRequestId++;

                cafeAddressSuggestions.style.display = "none";
                cafeAddress.value = result.address_line1 || "";
                cafeCity.value = result.city || "";
                cafePostCode.value = result.postcode || "";

                cafeLatitude = result.lat;
                cafeLongitude = result.lon;
                console.log(cafeLatitude, cafeLongitude);
            });
            cafeAddressSuggestions.appendChild(item);
        });

        cafeAddressSuggestions.style.display = cafeAddressFound ? "block" : "none";

    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Autocomplete request failed:", error);
        }
    }
});

cafePhone.addEventListener("input", () => {
    let phoneNumber = cafePhone.value;

    phoneNumber = phoneNumber.replace(/\D/g, "");

    phoneNumber = phoneNumber.slice(0, 9);

    if (phoneNumber.length > 6) {
        phoneNumber = phoneNumber.slice(0, 3) + " " +
            phoneNumber.slice(3, 6) + " " +
            phoneNumber.slice(6);
    } else if (phoneNumber.length > 3) {
        phoneNumber = phoneNumber.slice(0, 3) + " " +
            phoneNumber.slice(3);
    }

    cafePhone.value = phoneNumber;

});

informationContinueButton.addEventListener("click", () => {
    if (!validateInformationForm()) {
        return;
    }

    toggleInformationForm();
    showFeaturesForm();

});

//================ FEATURES ================
featuresSectionButton.addEventListener("click", toggleFeaturesForm);

featuresContinueButton.addEventListener("click", () => {
    if (!validateFeaturesForm()) {
        return;
    }

    toggleFeaturesForm();
    showOpeningHoursForm();
});

//================ OPENING-HOURS ================
openingHoursSectionButton.addEventListener("click", toggleOpeningHoursForm);

openingDays.forEach(dayElement => {
    const statusRadios = dayElement.querySelectorAll('input[type="radio"]');
    const openingIntervalTemplate = dayElement.querySelector(".opening-interval");
    const openingIntervalsContainer = dayElement.querySelector(".opening-intervals");
    const addIntervalButton = dayElement.querySelector(".opening-interval-add");

    statusRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            const allOpeningIntervals = dayElement.querySelectorAll(".opening-interval");

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

    addIntervalButton.addEventListener("click", () => {
        const newInterval = openingIntervalTemplate.cloneNode(true);
        const newOpeningTime = newInterval.querySelector("input[name$='-open']");
        const newClosingTime = newInterval.querySelector("input[name$='-close']");
        const removeIntervalButton = newInterval.querySelector(".opening-interval-add");

        removeIntervalButton.textContent = "-";
        removeIntervalButton.classList.remove("opening-interval-add");
        removeIntervalButton.classList.add("opening-interval-remove");

        newOpeningTime.value = "";
        newClosingTime.value = "";

        addIntervalButton.classList.add("is-hidden");

        removeIntervalButton.addEventListener("click", () => {
            newInterval.remove();
            addIntervalButton.classList.remove("is-hidden");
        });

        openingIntervalsContainer.append(newInterval);
    });
});

openingHoursContinueButton.addEventListener("click", () => {
    if (!validateOpeningHoursForm()) {
        return;
    }

    toggleOpeningHoursForm();
    showFinalReviewForm();

})

//================ FINAL-REVIEW ================
finalReviewSectionButton.addEventListener("click", toggleFinalReviewForm)

finalReviewContinueButton.addEventListener("click", () => {
    if (!validateFinalReviewForm()) {
        return
    }
    toggleFinalReviewForm();
    finalWarning.classList.remove("is-hidden");
});

photoInput.addEventListener("change", () => {

    if (selectedPhotos.length + photoInput.files.length > 6) {
        return;
    }

    for (const file of photoInput.files) {
        selectedPhotos.push(file);
    }

    renderPhotoPreviews();
});

finalWarningSubmitButton.addEventListener("click", () => {
    if(!validateSuggestionForm()){
        return;
    }
    //jinak posli do suggestions db
})




