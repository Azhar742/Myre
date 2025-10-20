const sidebar = document.getElementById('sidebar');
const hamburger = document.getElementById('hamburger');

// Toggle sidebar on mobile
hamburger?.addEventListener('click', () => sidebar.classList.toggle('open'));

// Close sidebar when clicking outside on mobile
document.addEventListener('click', e => {
  if (window.matchMedia('(max-width:800px)').matches) {
    if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  }
});
