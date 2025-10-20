function handleLogout() {
  // Clear user data and redirect to login
  if (confirm('Are you sure you want to logout?')) {
    localStorage.removeItem('user');
    window.location.href = '/';
  }
}

// Add smooth scroll behavior
document.addEventListener('DOMContentLoaded', () => {
  // Check if user is logged in
  const user = JSON.parse(localStorage.getItem('user'));
  if (!user) {
    // Redirect to login if not authenticated
    window.location.href = '/';
    return;
  }

  // Update user info in header
  const userNameElement = document.querySelector('.user-name');
  const userAvatarElement = document.querySelector('.user-avatar');
  
  if (userNameElement) {
    userNameElement.textContent = user.name;
  }
  
  if (userAvatarElement) {
    // Get initials from name
    const nameParts = user.name.split(' ');
    const initials = nameParts.length >= 2 
      ? nameParts[0][0] + nameParts[1][0] 
      : nameParts[0][0];
    userAvatarElement.textContent = initials.toUpperCase();
  }

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
