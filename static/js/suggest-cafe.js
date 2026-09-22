// =========================================
// CONFIG
// =========================================
const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
const API_KEY = "";

const allowedPhotoTypes = ["image/jpeg", "image/png", "image/webp"];
const maxPhotoSize = 5 * 1024 * 1024;
const maxPhotoCount = 6;

// =========================================
// STATE
// =========================================
let userLocation = null;
let searchRequestId = 0;
let addressSearchRequestId = 0;
let autocompleteController = null;
let placeDetailsController = null;
let addressAutocompleteController = null;

// =========================================
// DOM REFERENCES
// =========================================
const cafeSuggestionForm = document.querySelector(".cafe-suggestion-form");
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
const cafeInstagram = document.getElementById("cafe-instagram");
let cafeLatitude = null;
let cafeLongitude = null;
let cafeGeoapifyId = null;

const information = getSection(".basic-information");

//================ FEATURES ================
const features = getSection(".features");
const cardPayment = document.getElementById("card-yes");

//================ OPENING-HOURS ================
const openingHours = getSection(".opening-hours");
const openingDays = document.querySelectorAll(".opening-day");
let openingSchedule = {
    monday: [],
    tuesday: [],
    wednesday: [],
    thursday: [],
    friday: [],
    saturday: [],
    sunday: []
};

//================ FINAL-REVIEW ================
const finalReview = getSection(".final-review");
const photoPreviewContainer = document.querySelector(".photo-preview-container");
const photoInput = document.getElementById("cafe-photo-input");
const photoError = document.getElementById("photo-error");
let selectedPhotos = [];
//================ SUBMIT ================
const finalWarning = document.querySelector(".final-warning");
const finalWarningSubmitButton = document.querySelector(".submit-btn");

// =========================================
// FUNCTIONS
// =========================================
function getSection(sectionSelector) {
    const section = document.querySelector(sectionSelector);
    const sectionContent = section.querySelector(".section-content");
    const sectionButton = section.querySelector(".section-toggle");
    const status = section.querySelector(".section-status");
    const arrow = section.querySelector(".section-arrow");
    const continueButton = section.querySelector(".continue-btn");

    return {
        section,
        sectionContent,
        sectionButton,
        status,
        arrow,
        continueButton
    }
}

function toggleSectionForm(section) {
    section.sectionContent.classList.toggle("is-hidden");
    section.section.classList.toggle("is-collapsed");

    if (section.sectionContent.classList.contains("is-hidden")) {
        section.arrow.textContent = "▶";
    } else {
        section.arrow.textContent = "▼";
    }
}

function showSectionForm(section) {
    section.section.classList.remove("is-hidden");
}

//================ LOCATION ================
async function initializeLocation() {
    try {
        userLocation = await getUserLocation();
    } catch (error) {
        console.log("Location unavailable:", error);
    }
}

//================ CAFE-SUGGESTION ================
async function getCafeData(text) {
    if (autocompleteController) {
        autocompleteController.abort();
    }

    autocompleteController = new AbortController();

    let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&type=amenity&filter=countrycode:cz&limit=20&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        url += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    const response = await fetch(url, {signal: autocompleteController.signal});
    return response.json();
}

async function getPlaceDetails(placeId, signal) {
    const url = `https://api.geoapify.com/v2/place-details?id=${placeId}&apiKey=${API_KEY}`;

    const response = await fetch(url, {signal: signal});
    return response.json();
}

async function loadCafeDetails(placeId) {
    if (placeDetailsController) {
        placeDetailsController.abort();
    }

    placeDetailsController = new AbortController();

    return getPlaceDetails(placeId, placeDetailsController.signal);
}

async function selectCafe(result) {
    searchRequestId++;
    suggestions.style.display = "none";
    searchInput.value = `${result.name}, ${result.address_line2}`;
    cafeGeoapifyId = result.place_id;

    try {
        const placeDetails = await loadCafeDetails(result.place_id);

        if (!placeDetails.features || placeDetails.features.length === 0) {
            console.error("No place details found.");
            return
        }

        const cafeDetails = placeDetails.features[0].properties;

        fillCafeDetails(cafeDetails);
        resetOpeningHours();

        const cafeOpeningHours = cafeDetails.opening_hours;

        if (cafeOpeningHours) {
            fillCafeOpeningHours(cafeOpeningHours);
        }

    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Failed to get place details:", error);
        }
    }

    showInformationForm();
}

function fillCafeDetails(cafeDetails) {
    cafeName.value = cafeDetails.name || "";
    cafeCity.value = cafeDetails.city || "";
    cafeAddress.value = cafeDetails.address_line2?.split(',')[0].trim() || "";
    cafePostCode.value = cafeDetails.postcode || "";
    cafePhone.value = formatPhoneNumber(cafeDetails.contact?.phone) || "";
    cafeEmail.value = cafeDetails.contact?.email || "";
    cafeWebsite.value = cafeDetails.website || "";
    cafeLatitude = cafeDetails.lat;
    cafeLongitude = cafeDetails.lon;

    const cafeAcceptsCards = !!(
        cafeDetails.payment_options?.debit_cards ||
        cafeDetails.payment_options?.credit_cards
    );
    cardPayment.checked = cafeAcceptsCards;
}

//================ ADDRESS ================
async function getCafeAddress(text) {
    if (addressAutocompleteController) {
        addressAutocompleteController.abort();
    }

    addressAutocompleteController = new AbortController();

    let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&filter=countrycode:cz&limit=5&format=json&apiKey=${API_KEY}`;

    if (userLocation) {
        const radiusInMeters = 493000;
        url += `&filter=circle:${userLocation.lon},${userLocation.lat},${radiusInMeters}&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    const response = await fetch(url, {signal: addressAutocompleteController.signal});
    return response.json();
}

function fillAddressDetails(addressDetails) {
    cafeAddressSuggestions.style.display = "none";
    cafeAddress.value = addressDetails.address_line1 || "";
    cafeCity.value = addressDetails.city || "";
    cafePostCode.value = addressDetails.postcode || "";

    cafeLatitude = addressDetails.lat;
    cafeLongitude = addressDetails.lon;
}

//================ OPENING-HOURS ================
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

function fillCafeOpeningHours(cafeOpeningHours) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);

    const queryStart = new Date(today);
    queryStart.setDate(queryStart.getDate() - 1);

    const queryEnd = new Date(today);
    queryEnd.setDate(queryEnd.getDate() + 8);

    const openingHoursParser = new opening_hours(cafeOpeningHours);
    const intervals = openingHoursParser.getOpenIntervals(queryStart, queryEnd);


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


            if (index > 0) {
                const addIntervalButton = openingDayElement.querySelector(".opening-interval-add")
                addIntervalButton.click();
            }

            const openingTimeInputs = openingDayElement.querySelectorAll(`input[name="${day}-open"]`);
            const closingTimeInputs = openingDayElement.querySelectorAll(`input[name="${day}-close"]`);

            openingTimeInputs[index].value = schedule.open;
            closingTimeInputs[index].value = schedule.close;
        });

    });
}

function updateOpeningScheduleData() {
    openingSchedule = {};

    days.forEach(day => {
        const openingDayElement = document.querySelector(
            `[data-day="${day}"]`
        );

        const selectedStatus = openingDayElement.querySelector(
            `input[name="${day}"]:checked`
        );

        const intervals = [];

        if (selectedStatus.value === "open") {
            const openingTimeInputs = openingDayElement.querySelectorAll(
                `input[name="${day}-open"]`
            );

            const closingTimeInputs = openingDayElement.querySelectorAll(
                `input[name="${day}-close"]`
            );

            for (let i = 0; i < openingTimeInputs.length; i++) {
                intervals.push({
                    open: openingTimeInputs[i].value,
                    close: closingTimeInputs[i].value
                });
            }
        }

        openingSchedule[day] = {
            status: selectedStatus.value,
            intervals: intervals
        };
    });
}

//================ BASIC-INFORMATION ================
function showInformationForm() {
    information.section.classList.remove("is-hidden");
    information.section.classList.remove("is-collapsed");
    information.sectionContent.classList.remove("is-hidden");
    information.arrow.textContent = "▼";
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

function formatInstagramUsername(username) {
    if (!username) {
        return "";
    }

    username = username.trim();
    username = username.toLowerCase();

    username = username.replace(/[^a-z0-9._]/g, "");
    username = username.replace(/\.{2,}/g, ".");
    username = username.replace(/^\.|\.$/g, "");

    return username ? "@" + username : "";
}

function validateInformationForm() {
    const requiredFields = information.section.querySelectorAll(
        "input[required], select[required]"
    );

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            information.status.textContent = "❌ ";
            return false;
        }
    }

    if (cafePhone.value !== "" && !cafePhone.checkValidity()) {
        cafePhone.reportValidity();
        information.status.textContent = "❌ ";
        return false;
    }

    if (cafeEmail.value !== "" && !cafeEmail.checkValidity()) {
        cafeEmail.reportValidity();
        information.status.textContent = "❌ ";
        return false;
    }

     if (cafeWebsite.value !== "" && !cafeWebsite.checkValidity()) {
        cafeWebsite.reportValidity();
        information.status.textContent = "❌ ";
        return false;
    }

    information.status.textContent = "✔️ ";
    return true;
}

//================ FEATURES ================
function validateFeaturesForm() {
    const requiredFields = features.section.querySelectorAll(
        "input[required]"
    );

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            features.status.textContent = "❌ ";
            return false;
        }
    }

    features.status.textContent = "✔️ ";
    return true;
}

//================ OPENING-HOURS ================.
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
                    openingHours.status.textContent = "❌ ";
                    return false;
                }
            }
        }
    }

    const requiredFields = openingHours.section.querySelectorAll("input[required]");

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            openingHours.status.textContent = "❌ ";
            return false;
        }
    }

    openingHours.status.textContent = "✔️ ";

    return true;
}

//================ FINAL-REVIEW ================
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

function showPhotoError(message) {
    photoError.textContent = message;
}

function validatePhoto(file) {
    if (!allowedPhotoTypes.includes(file.type)) {
        return "This file type is not allowed.";
    }

    if (file.size > maxPhotoSize) {
        return "This file is too large. Maximum size is 5 MB.";
    }

    return null;
}

function validateFinalReviewForm() {
    const requiredFields = finalReview.section.querySelectorAll("input[required]")

    for (const field of requiredFields) {
        if (!field.checkValidity()) {
            field.reportValidity();
            finalReview.status.textContent = "❌ ";
            return false;
        }
    }

    finalReview.status.textContent = "✔️ ";
    return true;
}

//================ SUBMIT ================
function validateSuggestionForm() {
    const informationValid = validateInformationForm();
    const featuresValid = validateFeaturesForm();
    const openingHoursValid = validateOpeningHoursForm();
    const finalReviewValid = validateFinalReviewForm();

    return informationValid &&
        featuresValid &&
        openingHoursValid &&
        finalReviewValid;
}

function collectCafeSuggestionData() {
    const htmlFormData = new FormData(cafeSuggestionForm);

    updateOpeningScheduleData();

    const cafeSuggestion = {
        cafe: {
            external_place_id: cafeGeoapifyId,
            name: htmlFormData.get("cafeName"),
            address: htmlFormData.get("cafeAddress"),
            city: htmlFormData.get("cafeCity"),
            postal_code: htmlFormData.get("cafePostCode"),
            latitude: cafeLatitude,
            longitude: cafeLongitude,
            phone: htmlFormData.get("cafePhone"),
            email: htmlFormData.get("cafeEmail"),
            website: htmlFormData.get("cafeWebsite"),
            instagram: htmlFormData.get("cafeInstagram"),
            cafe_price: htmlFormData.get("cafePrice"),
            coffee_quality: htmlFormData.get("coffeeQuality")
        },

        feature: {
            wifi_quality: htmlFormData.get("cafeWifi"),
            socket_availability: htmlFormData.get("cafeOutlets"),
            noise_level: htmlFormData.get("cafeNoise"),
            seating_type: htmlFormData.get("cafeSeating"),
            air_conditioning: htmlFormData.get("cafeAirConditioning"),
            typical_occupancy: htmlFormData.get("cafeOccupancy"),
            card_payment: htmlFormData.get("cafeCard"),
            food_available: htmlFormData.get("cafeFood"),
            vegetarian_options: htmlFormData.get("cafeVegetarian")
        },

        opening_hours: openingSchedule,

        cafe_review: {
            rating: htmlFormData.get("userRating"),
            text: htmlFormData.get("userReview"),
        }

    }

    return cafeSuggestion;
}

function createCafeSuggestionFormData(cafeSuggestion) {
    const completeFormData = new FormData();

    completeFormData.append(
        "suggestion",
        JSON.stringify(cafeSuggestion)
    );

    for (const photo of selectedPhotos) {
        completeFormData.append("photos", photo);
    }

    return completeFormData;
}

async function prepareCafeSuggestion() {
    const cafeSuggestion = collectCafeSuggestionData();
    const completeFormData = createCafeSuggestionFormData(cafeSuggestion);

    try {
        const result = await sendCafeSuggestion(completeFormData);
        console.log("Suggestion sent successfully:", result);
    } catch (error) {
        console.error("Failed to send cafe suggestion:", error);
    }
}

async function sendCafeSuggestion(completeFormData) {
    const response = await fetch("/api/cafe-suggestions", {
        method: "POST",
        body: completeFormData
    });

    if (!response.ok) {
        throw new Error("Failed to send cafe suggestion.");
    }

    return response.json();
}

initializeLocation();

// =========================================
// EVENT-LISTENERS
// =========================================

//================ CAFE-SUGGESTION ================
searchInput.addEventListener("input", async () => {
    //================ CAFE-SUGGESTION ================
    const text = searchInput.value.trim();
    cafeGeoapifyId = null;

    if (text.length < 3) {
        suggestions.style.display = "none";
        suggestions.innerHTML = "";
        return;
    }

    const requestId = ++searchRequestId;

    try {
        const data = await getCafeData(text);

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

                item.addEventListener("click", () => selectCafe(result));

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
information.sectionButton.addEventListener("click", () => {
    toggleSectionForm(information);
});

information.continueButton.addEventListener("click", () => {
    if (!validateInformationForm()) {
        return;
    }

    toggleSectionForm(information);
    showSectionForm(features);
});

cafeAddress.addEventListener("input", async () => {
    const text = cafeAddress.value.trim();
    cafeLongitude = null;
    cafeLatitude = null;

    if (text.length < 3) {
        cafeAddressSuggestions.style.display = "none";
        cafeAddressSuggestions.innerHTML = "";
        return;
    }

    const requestId = ++addressSearchRequestId;

    try {
        const data = await getCafeAddress(text);

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

            item.addEventListener("click", () => {
                addressSearchRequestId++;
                fillAddressDetails(result);
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

cafePostCode.addEventListener("input", () => {
    let postCode = cafePostCode.value;

    postCode = postCode.replace(/\D/g, "");

    postCode = postCode.slice(0, 5);

    if (postCode.length > 3) {
        postCode = postCode.slice(0, 3) + " " + postCode.slice(3);
    }

    cafePostCode.value = postCode;
})

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

cafeInstagram.addEventListener("input", () => {
    cafeInstagram.value = formatInstagramUsername(cafeInstagram.value);
})

//================ FEATURES ================
features.sectionButton.addEventListener("click", () => {
    toggleSectionForm(features);
});

features.continueButton.addEventListener("click", () => {
    if (!validateFeaturesForm()) {
        return;
    }

    toggleSectionForm(features);
    showSectionForm(openingHours);
});

//================ OPENING-HOURS ================
openingHours.sectionButton.addEventListener("click", () => {
    toggleSectionForm(openingHours);
});

openingHours.continueButton.addEventListener("click", () => {
    if (!validateOpeningHoursForm()) {
        return;
    }

    toggleSectionForm(openingHours);
    showSectionForm(finalReview);

})

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

//================ FINAL-REVIEW ================
finalReview.sectionButton.addEventListener("click", () => {
    toggleSectionForm(finalReview);
})

finalReview.continueButton.addEventListener("click", () => {
    if (!validateFinalReviewForm()) {
        return
    }
    toggleSectionForm(finalReview);
    finalWarning.classList.remove("is-hidden");
});

photoInput.addEventListener("change", () => {
    photoError.textContent = "";

    const newFiles = photoInput.files;

    if (selectedPhotos.length + newFiles.length > maxPhotoCount) {
        showPhotoError(`You can select a maximum of ${maxPhotoCount} photos.`);
        return;
    }

    for (const file of newFiles) {
        const error = validatePhoto(file);

        if (error) {
            showPhotoError(`${file.name}: ${error}`);
            continue;
        }

        selectedPhotos.push(file);
    }

    renderPhotoPreviews();
});

//================ SUBMIT ================
finalWarningSubmitButton.addEventListener("click", () => {
    if (!validateSuggestionForm()) {
        return;
    }

    prepareCafeSuggestion();
})




