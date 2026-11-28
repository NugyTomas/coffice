export function validateInformationForm(information, cafePhone, cafeEmail, cafeWebsite, cafeInstagram) {
    const requiredFields = information.section.querySelectorAll("input[required], select[required]");

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

    if (cafeInstagram.value !== "" && !cafeInstagram.checkValidity()) {
        cafeInstagram.reportValidity();
        information.status.textContent = "❌ ";
        return false;
    }

    information.status.textContent = "✔️ ";
    return true;
}

export function validateFeaturesForm(features) {
    const requiredFields = features.section.querySelectorAll("input[required]");

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

export function validateOpeningHoursForm(openingDays, openingHours) {

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

            if (i > 0) {
                const previousClosingTime = closingTimeInputs[i - 1].value;

                if (openingTime === "") {
                    openingTimeInputs[i].setCustomValidity("Please enter valid interval");
                    openingTimeInputs[i].reportValidity();
                    openingHours.status.textContent = "❌ ";
                    return false;
                }

                if (openingTime < previousClosingTime) {
                    openingTimeInputs[i].setCustomValidity("Opening intervals must not overlap.");
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

export function validateFinalReviewForm(finalReview) {
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