export function getSection(sectionSelector) {
    const section = document.querySelector(sectionSelector);
    const sectionContent = section.querySelector(".section-content");
    const sectionButton = section.querySelector(".section-toggle");
    const status = section.querySelector(".section-status");
    const arrow = section.querySelector(".section-arrow");
    const continueButton = section.querySelector(".continue-btn");

    return {
        section, sectionContent, sectionButton, status, arrow, continueButton
    }
}

export function toggleSectionForm(section) {
    section.sectionContent.classList.toggle("is-hidden");
    section.section.classList.toggle("is-collapsed");

    if (section.sectionContent.classList.contains("is-hidden")) {
        section.arrow.textContent = "▶";
    } else {
        section.arrow.textContent = "▼";
    }
}

export function showSectionForm(section) {
    section.section.classList.remove("is-hidden");
}

export function showInformationForm(information) {
    information.section.classList.remove("is-hidden");
    information.section.classList.remove("is-collapsed");
    information.sectionContent.classList.remove("is-hidden");
    information.arrow.textContent = "▼";
}