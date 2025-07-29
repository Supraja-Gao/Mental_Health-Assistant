document.addEventListener('DOMContentLoaded', () => {
  console.log("Main.js loaded - running in light mode only.");

  // Example future setup:
  // Handle mobile navbar toggle if you have a hamburger menu
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('hidden');
    });
  }
});
