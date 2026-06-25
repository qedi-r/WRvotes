var WRV_FAVOURITE_KEY = "wrv-favourited";
var WRV_NOTE_PREFIX = "wrv-note-";

function clearSavedCandidateData() {
    localStorage.removeItem(WRV_FAVOURITE_KEY);

    Object.keys(localStorage).forEach(function (key) {
        if (key.startsWith(WRV_NOTE_PREFIX)) {
            localStorage.removeItem(key);
        }
    });
}

function parseFavourites() {
    var favouritesRaw = localStorage.getItem(WRV_FAVOURITE_KEY);
    return favouritesRaw ? JSON.parse(favouritesRaw) : [];
}

function saveFavourite(candidate) {
    var favourites = parseFavourites();
    if (!favourites.includes(candidate)) {
        favourites.push(candidate);
        localStorage.setItem(WRV_FAVOURITE_KEY, JSON.stringify(favourites));
    }
}

function removeFavourite(candidate) {
    var favourites = parseFavourites();
    favourites = favourites.filter(x => x != candidate);
    localStorage.setItem(WRV_FAVOURITE_KEY, JSON.stringify(favourites));
}


function setFavouriteState(btn, isFavourited) {
    btn.toggleClass("favourited", isFavourited);
    btn.attr("aria-pressed", String(isFavourited));
    btn.find("i")
        .toggleClass("fa-solid", isFavourited)
        .toggleClass("fa-regular", !isFavourited);
}

function updateFavourites() {
    var favouritedCandidates = parseFavourites();
    $(".favourite-btn[data-candidate-id]").each(function () {
        var btn = $(this);
        setFavouriteState(
            btn,
            favouritedCandidates.includes(btn.attr("data-candidate-id")),
        );
    });
}
 
function saveNote(candidate, content) {
    localStorage.setItem(WRV_NOTE_PREFIX + candidate, content);
}

function loadNote(candidate) {
    return localStorage.getItem(WRV_NOTE_PREFIX + candidate) || '';
}

function updateNotes() {
    $(".auto-resize-textarea[data-candidate-id]").each(function () {
        var saved = loadNote($(this).attr("data-candidate-id"));
        if (saved) {
            $(this).html(saved);
        } else { 
            $(this).html("");
        }
    });
}

$(document).ready(function () {
    var debounce;
    $(".auto-resize-textarea[data-candidate-id]").on("input", function () {
        var el = $(this);
        clearTimeout(debounce);
        debounce = setTimeout(function () {
            saveNote(el.attr("data-candidate-id"), el.html());
        }, 300);
    });

    $("h3.no-website").on("click", (e) => {
        tooltip_id = $(e.target).attr('aria-describedby');
        tooltip_e = $("#" + tooltip_id)
        if (tooltip_e.hasClass("hidden")) {
            tooltip_e.removeClass("hidden");
            setTimeout(() => {
                tooltip_e.addClass("hidden");
            }, 3000);
        }
    });

    $(".favourite-btn").on("click", function () {
        var candidate = $(this).attr("data-candidate-id");
        
        var btn = $(this);
        if (btn.hasClass("favourited")) {
            setFavouriteState(btn, false);
            removeFavourite(candidate);
        } else {
            setFavouriteState(btn, true);
            saveFavourite(candidate);
        }

    });

    $(".notes-btn").on("click", function () {
        var candidate = $(this).attr("data-candidate-id");
        $(this).toggleClass("opened");
        var icon = $(this).find("i");
        var notes = $(`.auto-resize-textarea[data-candidate-id='${candidate}']`);
        if (notes) { 
            if ($(this).hasClass("opened")) {
                icon.removeClass("fa-regular").addClass("fa-solid");
                notes.closest(".notes-container").addClass("open");
            } else {
                icon.removeClass("fa-solid").addClass("fa-regular");
                notes.closest(".notes-container").removeClass("open");
            }
        }
    });

    updateNotes();
    updateFavourites();

    window.addEventListener("storage", (event) => {
        console.log("Storage event detected " + event.key);
        if (event.key === WRV_FAVOURITE_KEY) {
            updateFavourites();
        } else if (event.key.startsWith(WRV_NOTE_PREFIX)) {
            updateNotes();
        }
    });

    $(".clear-saved-candidate-data").each(function() { 
            this.addEventListener("click", function (event) {
                event.preventDefault();

                if (window.confirm("Clear all saved notes and favourites? This will remove them from this browser and cannot be undone.")) {
                    clearSavedCandidateData();
                    window.location.reload();
                }
            });

            this.parentElement.removeAttribute("hidden");
        });


    $("#worksheet-no-js-warning").hide();
});
