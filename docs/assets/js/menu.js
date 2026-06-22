$(document).ready(function () {

  function add_ul_toggle_button(target, classname, title, inittext) {
    retval =
      '<button data-toc="' +
      target +
      '" ' +
      'id="' + target + '-btn" ' + 'class="' + classname +
      '" title="' + title +
      '" >' +
      inittext +
      "</button>";
    $("#" + target)
      .parent()
      .prepend(retval);
  }

  function add_toc_toggle_button() {
    var target = $(this).attr("id");
    add_ul_toggle_button(target, "toggle-toc", "Toggle table of contents", "–");
  }

  function add_menu_toggle_button() {
    var target = $(this).attr("id");
    var target_button = target + "-btn";
    add_ul_toggle_button(
      target,
      "toggle-menu",
      "toggle main menu",
      '<i class="fas fa-bars"></i>',
    );

    $("#" + target_button).attr({
      "aria-controls": target,
      "aria-expanded": "false",
      "aria-label": "Toggle main menu",
      type: "button",
    });
  }

  function toggle_main_menu(button_id) {
    var target_ul = "#main-menu-ul";
    var target_button = "#main-menu-ul-btn";

    if ($(target_ul).hasClass("hidden")) {
      $(target_ul).removeClass("hidden");
      $(target_ul).slideDown();
      $(target_button).attr({
        "aria-expanded": "true",
      });
    } else {
      $(target_ul).addClass("hidden");
      $(target_ul).slideUp();
      $(target_button).attr({
        "aria-expanded": "false",
      });
    }
  }

  function toggle_toc(target_button) {
    var target_ul = "#toc-list";

    if ($(target_ul).hasClass("hidden")) {
      $(target_ul).removeClass("hidden");
      $(target_button).text("–");
      $(target_ul).slideDown();
    } else {
      $(target_ul).addClass("hidden");
      $(target_button).text("+");
      $(target_ul).slideUp();
    }
  }

  $("#toc-list").each(add_toc_toggle_button);
  $("#main-menu-ul").each(add_menu_toggle_button);

  $(".toggle-toc").on("click", function (e) {
    toggle_toc("#" + e.target.id);
  });

  $(".toggle-menu").on("click", function (e) {
    toggle_main_menu("#" + e.target.id);
  });

});
