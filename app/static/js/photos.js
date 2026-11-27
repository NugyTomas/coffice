import {allowedPhotoTypes, maxPhotoSize} from "./config.js";

export function renderPhotoPreviews(selectedPhotos, photoPreviewContainer) {
    photoPreviewContainer.textContent = "";

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
            renderPhotoPreviews(selectedPhotos, photoPreviewContainer);
        });

        photoContainer.appendChild(image);
        photoContainer.appendChild(removeButton);

        photoPreviewContainer.appendChild(photoContainer);
    });
}

export function showPhotoError(message, photoError) {
    photoError.textContent = message;
}

export function validatePhoto(file) {
    if (!allowedPhotoTypes.includes(file.type)) {
        return "This file type is not allowed.";
    }

    if (file.size > maxPhotoSize) {
        return "This file is too large. Maximum size is 5 MB.";
    }

    return null;
}