export async function apiRequest(url, signal) {
    const response = await fetch(url, {signal});

    if (!response.ok) {
        throw new Error("API request failed.");
    }

    return response.json();
}

export async function sendCafeSuggestion(completeFormData) {
    let response;
    try {
        response = await fetch("/api/cafe-suggestions", {
            method: "POST", body: completeFormData
        });
    } catch {
        throw new Error("Could not reach the server. Please check your connection and try again.");
    }

    let result = null;
    const contentType = response.headers.get("content-type");

    if (contentType && contentType.includes("application/json")) {
        try {
            result = await response.json();
        } catch {
            result = null;
        }
    }

    if (!response.ok) {
        const errorMessage = result?.errors ? Object.values(result.errors)
            .flat()
            .join("\n") : "Something went wrong while submitting the café suggestion.";

        throw new Error(errorMessage);
    }

    return result;
}