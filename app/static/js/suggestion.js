export function collectCafeSuggestionData(cafeGeoapifyId, cafeLatitude, cafeLongitude, cafeSuggestionForm, scheduleData) {
    const htmlFormData = new FormData(cafeSuggestionForm);


    return {
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
            price_level: htmlFormData.get("cafePrice"),
            coffee_quality: htmlFormData.get("coffeeQuality")
        },

        cafe_features: {
            wifi_quality: htmlFormData.get("cafeWifi"),
            power_outlets: htmlFormData.get("cafeOutlets"),
            noise_level: htmlFormData.get("cafeNoise"),
            seating_type: htmlFormData.get("cafeSeating"),
            air_conditioning: htmlFormData.get("cafeAirConditioning"),
            typical_occupancy: htmlFormData.get("cafeOccupancy"),
            card_payment: htmlFormData.get("cafeCard"),
            food_options: htmlFormData.get("cafeFood"),
            vegetarian_options: htmlFormData.get("cafeVegetarian")
        },

        cafe_opening_hours: scheduleData,

        cafe_review: {
            rating: htmlFormData.get("userRating"), text: htmlFormData.get("userReview"),
        }

    };
}

export function createCafeSuggestionFormData(cafeSuggestion, selectedPhotos) {
    const completeFormData = new FormData();

    completeFormData.append("suggestion", JSON.stringify(cafeSuggestion));

    for (const photo of selectedPhotos) {
        completeFormData.append("photos", photo);
    }

    return completeFormData;
}