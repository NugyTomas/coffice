import {apiRequest, sendCafeSuggestion} from "./api.js";
import {maxPhotoCount} from "./config.js";
import {formatInstagramUsername, formatPhoneNumber, formatPostalCode} from "./format.js";
import {getUserLocation} from "./geolocation.js";
import {fillCafeOpeningHours, resetOpeningHours, updateOpeningScheduleData} from "./opening-hours.js";
import {renderPhotoPreviews, showPhotoError, validatePhoto} from "./photos.js";
import {getSection, showInformationForm, showSectionForm, toggleSectionForm} from "./section.js";
import {createCafeSuggestionFormData, collectCafeSuggestionData} from "./suggestion.js";
import {
    validateFeaturesForm,
    validateFinalReviewForm,
    validateInformationForm,
    validateOpeningHoursForm
} from "./validation.js";

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
const information = getSection(".basic-information");

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

let selectedAddress = {
    address: "", city: "", postCode: "", latitude: null, longitude: null
};

//================ FEATURES ================
const features = getSection(".features");

const cardPayment = document.getElementById("card-yes");

//================ OPENING-HOURS ================
const openingHours = getSection(".opening-hours");

const openingDays = document.querySelectorAll(".opening-day");
let openingSchedule = {
    monday: [], tuesday: [], wednesday: [], thursday: [], friday: [], saturday: [], sunday: []
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
const submissionMessage = document.querySelector(".submission-message");

// =========================================
// FUNCTIONS
// =========================================

//================ LOCATION ================
async function initializeLocation() {
    try {
        userLocation = await getUserLocation();
    } catch (error) {
        console.log("Location unavailable:", error);
    }
}

//================ CAFE-SUGGESTION ================
function getCafeData(text) {
    if (autocompleteController) {
        autocompleteController.abort();
    }

    autocompleteController = new AbortController();

    let url = `/api/geoapify/autocomplete?text=${encodeURIComponent(text)}&type=amenity&filter=countrycode:cz&limit=20&format=json`;

    if (userLocation) {
        url += `&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    return apiRequest(url, autocompleteController.signal)
}

function getPlaceDetails(placeId, signal) {
    const url = `/api/geoapify/place-details?id=${encodeURIComponent(placeId)}`;

    return apiRequest(url, signal);
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
        saveAddressDetails(cafeDetails);
        openingSchedule = resetOpeningHours(openingDays);

        const cafeOpeningHours = cafeDetails.opening_hours;

        if (cafeOpeningHours) {
            fillCafeOpeningHours(cafeOpeningHours, openingSchedule);
        }

    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Failed to get place details:", error);
        }
    }

    showInformationForm(information);
}

function fillCafeDetails(cafeDetails) {
    cafeName.value = cafeDetails.name || "";
    cafeCity.value = cafeDetails.city || "";
    cafeAddress.value = buildStreetAddress(cafeDetails);
    cafePostCode.value = formatPostalCode(cafeDetails.postcode) || "";
    cafePhone.value = formatPhoneNumber(cafeDetails.contact?.phone) || "";
    cafeEmail.value = cafeDetails.contact?.email || "";
    cafeWebsite.value = cafeDetails.website || "";
    cafeLatitude = cafeDetails.lat;
    cafeLongitude = cafeDetails.lon;

    const cafeAcceptsCards = !!(cafeDetails.payment_options?.debit_cards || cafeDetails.payment_options?.credit_cards);
    cardPayment.checked = cafeAcceptsCards;
}

//================ ADDRESS ================
function getCafeAddress(text) {
    if (addressAutocompleteController) {
        addressAutocompleteController.abort();
    }

    addressAutocompleteController = new AbortController();

    let url = `/api/geoapify/autocomplete?text=${encodeURIComponent(text)}&filter=countrycode:cz&limit=5&format=json`;

    if (userLocation) {
        url += `&bias=proximity:${userLocation.lon},${userLocation.lat}`;
    }

    return apiRequest(url, addressAutocompleteController.signal);
}

function fillAddressDetails(addressDetails) {
    cafeAddressSuggestions.style.display = "none";
    cafeAddress.value = buildStreetAddress(addressDetails);
    cafeCity.value = addressDetails.city || "";
    cafePostCode.value = formatPostalCode(addressDetails.postcode) || "";

    cafeLatitude = addressDetails.lat;
    cafeLongitude = addressDetails.lon;
}

function buildStreetAddress(addressDetails) {
    if (addressDetails.street) {
        return addressDetails.housenumber ? `${addressDetails.street} ${addressDetails.housenumber}` : addressDetails.street;
    }

    if (addressDetails.housenumber) {
        return `${addressDetails.city || addressDetails.suburb || ""} ${addressDetails.housenumber}`.trim();
    }

    return addressDetails.address_line2?.split(",")[0].trim() || "";
}

function saveAddressDetails(addressDetails) {
    selectedAddress.address = buildStreetAddress(addressDetails);
    selectedAddress.city = addressDetails.city || "";
    selectedAddress.postCode = formatPostalCode(addressDetails.postcode) || "";
    selectedAddress.latitude = addressDetails.lat;
    selectedAddress.longitude = addressDetails.lon;
}

//================ SUBMIT ================
function validateSuggestionForm() {
    const informationValid = validateInformationForm(information, cafePhone, cafeEmail, cafeWebsite, cafeInstagram);
    const featuresValid = validateFeaturesForm(features);
    const openingHoursValid = validateOpeningHoursForm(openingDays, openingHours);
    const finalReviewValid = validateFinalReviewForm(finalReview);

    return informationValid && featuresValid && openingHoursValid && finalReviewValid;
}

async function prepareCafeSuggestion() {
    const scheduleData = updateOpeningScheduleData();
    const cafeSuggestion = collectCafeSuggestionData(cafeGeoapifyId, cafeLatitude, cafeLongitude, cafeSuggestionForm, scheduleData);

    const completeFormData = createCafeSuggestionFormData(cafeSuggestion, selectedPhotos);

    submissionMessage.textContent = "";

    try {
        await sendCafeSuggestion(completeFormData);
        submissionMessage.textContent = "Café suggestion submitted successfully.";
    } catch (error) {
        submissionMessage.textContent = error.message;
    }
}


initializeLocation();

// =========================================
// EVENT-LISTENERS
// =========================================
document.addEventListener("click", (event) => {
    const clickedInsideCafeSearch = searchInput.contains(event.target) || suggestions.contains(event.target);

    const clickedInsideAddressSearch = cafeAddress.contains(event.target) || cafeAddressSuggestions.contains(event.target);

    if (!clickedInsideCafeSearch) {
        searchRequestId++;

        if (autocompleteController) {
            autocompleteController.abort();
        }

        suggestions.style.display = "none";
    }

    if (!clickedInsideAddressSearch) {
        addressSearchRequestId++;

        if (addressAutocompleteController) {
            addressAutocompleteController.abort();
        }

        cafeAddressSuggestions.style.display = "none";
    }


});

//================ CAFE-SUGGESTION ================
searchInput.addEventListener("input", async () => {
    //================ CAFE-SUGGESTION ================
    const text = searchInput.value.trim();
    cafeGeoapifyId = null;

    if (text.length < 3) {
        suggestions.style.display = "none";
        suggestions.textContent = "";
        searchRequestId++
        return;
    }

    const requestId = ++searchRequestId;

    try {
        const data = await getCafeData(text);

        if (requestId !== searchRequestId) {
            return;
        }
        suggestions.textContent = "";

        let cafeFound = false;

        data.results.forEach(result => {
            if (result.category === 'catering.cafe') {
                cafeFound = true;
                const item = document.createElement("div");
                item.classList.add("suggestion-item");

                const name = document.createElement("strong");
                name.textContent = result.name;

                const address = document.createElement("small");
                address.textContent = result.address_line2;

                item.append(name, document.createTextNode(", "), address);

                if (result.coffice_status) {
                    item.classList.add("suggestion-item-disabled");

                    const badge = document.createElement("span");
                    badge.classList.add("suggestion-badge");
                    badge.textContent = result.coffice_status === "approved" ? "Already on Coffice" : "Waiting for approval";

                    item.appendChild(badge);
                } else {
                    item.addEventListener("click", () => selectCafe(result));
                }

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

searchInput.addEventListener("focus", () => {
    if (searchInput.value.trim().length >= 3 && suggestions.children.length > 0) {
        suggestions.style.display = "block";
    }
});

manualCafeButton.addEventListener("click", () => showInformationForm(information));

//================ BASIC-INFORMATION ================
information.sectionButton.addEventListener("click", () => {
    toggleSectionForm(information);
});

information.continueButton.addEventListener("click", () => {
    if (!validateInformationForm(information, cafePhone, cafeEmail, cafeWebsite, cafeInstagram)) {
        return;
    }

    toggleSectionForm(information);
    showSectionForm(features);
});

cafeAddress.addEventListener("input", async () => {
    const text = cafeAddress.value.trim();

    if (text.length < 3) {
        cafeAddressSuggestions.style.display = "none";
        cafeAddressSuggestions.textContent = "";
        addressSearchRequestId++
        return;
    }

    const requestId = ++addressSearchRequestId;

    try {
        const data = await getCafeAddress(text);

        if (requestId !== addressSearchRequestId) {
            return;
        }
        cafeAddressSuggestions.textContent = "";

        let cafeAddressFound = false;

        data.results.forEach(result => {
            if (!result.postcode) {
                return
            }

            cafeAddressFound = true;
            const item = document.createElement("div");
            item.classList.add("suggestion-item");

            const address = document.createElement("strong");
            address.textContent = result.formatted;

            item.appendChild(address);
            item.addEventListener("click", () => {
                addressSearchRequestId++;
                fillAddressDetails(result);
                saveAddressDetails(result);
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

cafeAddress.addEventListener("focus", () => {
    if (cafeAddress.value.trim().length >= 3 && cafeAddressSuggestions.children.length > 0) {
        cafeAddressSuggestions.style.display = "block";
    }
});

cafeAddress.addEventListener("focusout", () => {
    cafeAddress.value = selectedAddress.address;
    cafeCity.value = selectedAddress.city;
    cafePostCode.value = selectedAddress.postCode;
});

[cafeName, cafeAddress].forEach(field => {
    field.addEventListener("blur", () => {
        field.value = field.value.trim().replace(/\s{2,}/g, " ");
    });
});

cafePostCode.addEventListener("input", () => {
    cafePostCode.value = formatPostalCode(cafePostCode.value);
});

cafePhone.addEventListener("input", () => {
    cafePhone.value = formatPhoneNumber(cafePhone.value);
});

[cafeEmail, cafeWebsite].forEach(field => {
    field.addEventListener("input", () => {
        field.value = field.value.replace(/\s/g, "");
    });
});

cafeInstagram.addEventListener("input", () => {
    let username = cafeInstagram.value.toLowerCase().replace(/[^a-z0-9._]/g, "");
    username = username.replace(/\.{2,}/g, ".").slice(0, 30);
    cafeInstagram.value = username ? "@" + username : "";
});

cafeInstagram.addEventListener("blur", () => {
    cafeInstagram.value = formatInstagramUsername(cafeInstagram.value);
});

//================ FEATURES ================
features.sectionButton.addEventListener("click", () => {
    toggleSectionForm(features);
});

features.continueButton.addEventListener("click", () => {
    if (!validateFeaturesForm(features)) {
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
    if (!validateOpeningHoursForm(openingDays, openingHours)) {
        return;
    }

    toggleSectionForm(openingHours);
    showSectionForm(finalReview);

})

openingDays.forEach(dayElement => {
    const statusRadios = dayElement.querySelectorAll('input[type="radio"]');
    const openRadio = dayElement.querySelector('input[type="radio"][value="open"]');
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

    dayElement.addEventListener("input", (event) => {
        if (!event.target.matches('input[type="time"]')) {
            return;
        }

        if (!openRadio.checked) {
            openRadio.click();
        }
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
    if (!validateFinalReviewForm(finalReview)) {
        return
    }
    toggleSectionForm(finalReview);
    finalWarning.classList.remove("is-hidden");
});

photoInput.addEventListener("change", () => {
    photoError.textContent = "";

    const newFiles = photoInput.files;

    if (selectedPhotos.length + newFiles.length > maxPhotoCount) {
        showPhotoError(`You can select a maximum of ${maxPhotoCount} photos.`, photoError);
        return;
    }

    for (const file of newFiles) {
        const error = validatePhoto(file);

        if (error) {
            showPhotoError(`${file.name}: ${error}`, photoError);
            continue;
        }

        selectedPhotos.push(file);
    }

    renderPhotoPreviews(selectedPhotos, photoPreviewContainer);
});

//================ SUBMIT ================
finalWarningSubmitButton.addEventListener("click", () => {
    if (!validateSuggestionForm()) {
        return;
    }

    prepareCafeSuggestion();
})




