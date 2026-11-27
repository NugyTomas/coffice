export function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${hours}:${minutes}`;
}


export function formatPostalCode(value) {
    const digits = (value || "").replace(/\D/g, "").slice(0, 5);
    return digits.length > 3 ? digits.slice(0, 3) + " " + digits.slice(3) : digits;
}


export function formatPhoneNumber(phoneNumber) {
    if (!phoneNumber) {
        return "";
    }

    phoneNumber = phoneNumber.replace("+420", "");
    phoneNumber = phoneNumber.replace(/\D/g, "");
    phoneNumber = phoneNumber.slice(0, 9);

    if (phoneNumber.length > 6) {
        phoneNumber = phoneNumber.slice(0, 3) + " " + phoneNumber.slice(3, 6) + " " + phoneNumber.slice(6);
    } else if (phoneNumber.length > 3) {
        phoneNumber = phoneNumber.slice(0, 3) + " " + phoneNumber.slice(3);
    }

    return phoneNumber;
}

export function formatInstagramUsername(username) {
    if (!username) {
        return "";
    }

    username = username.toLowerCase();
    username = username.replace(/[^a-z0-9._]/g, "");
    username = username.replace(/\.{2,}/g, ".");
    username = username.slice(0, 30);
    username = username.replace(/^\.+|\.+$/g, "");

    return username ? "@" + username : "";
}