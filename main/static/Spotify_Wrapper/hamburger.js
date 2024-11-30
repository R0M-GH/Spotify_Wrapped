/**
 * Event listener that runs when the DOM content is fully loaded.
 * It sets up a click event listener for the hamburger button to toggle the display of the menu.
 *
 * @event DOMContentLoaded
 * @type {EventListener}
 */
document.addEventListener("DOMContentLoaded", () => {

  /**
   * The hamburger menu button element that triggers the menu toggle action when clicked.
   * @type {HTMLElement}
   */
  const hamburger = document.getElementById("hamburger");

  /**
   * The menu element that will be toggled between visible and hidden states.
   * @type {HTMLElement}
   */
  const menu = document.getElementById("menu");

  /**
   * Click event listener for the hamburger button. It toggles the visibility of the menu by changing the display style.
   * When the menu is displayed as "block", it switches it to "none", and vice versa.
   *
   * @event click
   * @type {EventListener}
   */
  hamburger.addEventListener("click", () => {
    // Toggle menu visibility between 'block' and 'none'
    menu.style.display = menu.style.display === "block" ? "none" : "block";
  });
});
