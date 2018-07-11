// Forward declare jQuery"s `$` symbol
"use strict";
jQuery, $;
let animating = false;

function closeSidebar(event) {
  let sidebarWidth = document.getElementById('sidebar').offsetWidth;
  if (!animating && sidebarWidth > 0) {
    animating = true;
    $("#sidebar").stop().animate({width: 'toggle'}, 200, 0,
      function() {
        $(this).removeClass("open");
        animating = false;
      }
    );
  }
}

function openSidebar(event) {
  if ($("#mobile-header").is(":visible")) {
    $("#sidebar").stop().animate({width: 'toggle'}, 200, 0,
      function() {
        $(this).addClass("open");
      }
    );
    event.stopPropagation();
  }
}

// ORCID button in base.html
function openORCID() {
  let baseUrl = window.location.origin;
  let loginPath = baseUrl + "/login/orcid/";
  console.log(loginPath);
  window.location.assign(loginPath);
  return false;
}

function confirmDelete() {
  let yes = confirm(
    "This action is final and cannot be undone. Would you like to proceed?"
  );
  if (yes) {
    return window.location.assign('?delete=True')
  }
}


// On Load ----------------------------------------------------------------- //
$("document").ready(function() {
  
  // Initialise select2
  $(".select2").select2();
  $(".select2-token-select").select2({
      tags: true,
      tokenSeparators: [","]
  });

  let mobileHeader = document.getElementById("mobile-header");
  let middle_content = document.getElementById("middle-content");
  let sticky = middle_content.offsetTop;
  stickHeader();
  
  function stickHeader() {
    if (window.pageYOffset > 3 * sticky) {
      mobileHeader.classList.add("sticky");
    } else {
      mobileHeader.classList.remove("sticky");
    }
  }
  
  // Sticky the header on scroll
  window.onscroll = function () {
    stickHeader();
  };
  
  // Sidebar open/close events
  $("#mobile-header").click(function(event) {
    openSidebar(event);
  });
  $("#middle-content,#footer").click(function(event) {
    closeSidebar(event)
  });
  $(window).on("resize focusout scroll", function(event) {
    closeSidebar(event);
  });
  
  $(".nav-dropdown").hover(function() {
    $(".nav-dropdown .nav-dropdown-content").show();
  });
  $(".nav-dropdown").mouseleave(function() {
    $(".nav-dropdown .nav-dropdown-content").hide();
  });
  
  
  // Convert marked elements to markdown
  let converter = new showdown.Converter();
  let rowColumns = $(".markdown");
  console.log(rowColumns);
  for (let i=0; i < rowColumns.length; i++) {
    rowColumns[i].innerHTML = converter.makeHtml(rowColumns[i].innerHTML);
  }
  
});
