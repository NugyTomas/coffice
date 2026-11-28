import {days} from "./config.js";
import {formatTime} from "./format.js";

export function resetOpeningHours(openingDays) {
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

    return Object.fromEntries(days.map(day => [day, []]));
}

export function fillCafeOpeningHours(cafeOpeningHours, openingSchedule) {
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
            open: formatTime(start), close: formatTime(end)
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

export function updateOpeningScheduleData() {
    const scheduleData = {};

    days.forEach(day => {
        const openingDayElement = document.querySelector(`[data-day="${day}"]`);

        const selectedStatus = openingDayElement.querySelector(`input[name="${day}"]:checked`);

        const intervals = [];

        if (selectedStatus?.value === "open") {
            const openingTimeInputs = openingDayElement.querySelectorAll(`input[name="${day}-open"]`);

            const closingTimeInputs = openingDayElement.querySelectorAll(`input[name="${day}-close"]`);

            for (let i = 0; i < openingTimeInputs.length; i++) {
                intervals.push({
                    open: openingTimeInputs[i].value, close: closingTimeInputs[i].value
                });
            }
        }

        scheduleData[day] = {
            status: selectedStatus?.value, intervals: intervals
        };
    });

    return scheduleData
}