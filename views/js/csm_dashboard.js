function handleLogout() {
  // Redirect to login page or home
  if (confirm('Are you sure you want to logout?')) {
    window.location.href = '/';
  }
}

// Add smooth scroll behavior
document.addEventListener('DOMContentLoaded', () => {
  // Add animation on page load
  const cards = document.querySelectorAll('.dashboard-card');
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      card.style.transition = 'all 0.5s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, index * 100);
  });
});
