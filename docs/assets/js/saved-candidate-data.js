var WRV_FAVOURITE_KEY = "wrv-favourited";
var WRV_NOTE_PREFIX = "wrv-note-";
var WRV_CLEAR_SAVED_CANDIDATE_DATA_ID = "clear-saved-candidate-data";

function clearSavedCandidateData() {
    localStorage.removeItem(WRV_FAVOURITE_KEY);

    Object.keys(localStorage).forEach(function (key) {
        if (key.startsWith(WRV_NOTE_PREFIX)) {
            localStorage.removeItem(key);
        }
    });
}

var clearSavedCandidateDataLink = document.getElementById(WRV_CLEAR_SAVED_CANDIDATE_DATA_ID);

if (clearSavedCandidateDataLink) {
    clearSavedCandidateDataLink.addEventListener("click", function (event) {
        event.preventDefault();

        if (window.confirm("Clear all saved notes and favourites? This will remove them from this browser and cannot be undone.")) {
            clearSavedCandidateData();
            window.location.reload();
        }
    });

    clearSavedCandidateDataLink.parentElement.removeAttribute("hidden");
}
