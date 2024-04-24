document.addEventListener("DOMContentLoaded", function() {
  var targetElement = document.querySelector("main>header");

  var menuButton = document.querySelector(".mobile.menu-button");
  menuButton.addEventListener("click", function() {
    targetElement.classList.add("active");
  });

  var menuButton = document.querySelector(".mobile.close-button");
  menuButton.addEventListener("click", function() {
    targetElement.classList.remove("active");
  });
})
