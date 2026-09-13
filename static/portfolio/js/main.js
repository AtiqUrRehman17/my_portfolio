// Shared motion. Respect the visitor's reduced-motion preference.
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (window.AOS) {
    AOS.init({
        duration: prefersReducedMotion ? 0 : 650,
        once: true,
        offset: 60,
        easing: 'ease-out-cubic',
        disable: prefersReducedMotion
    });
}

// Navbar background and spacing after the page starts scrolling.
const navbar = document.getElementById('mainNav');
const updateNavbar = () => {
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 24);
};
updateNavbar();
window.addEventListener('scroll', updateNavbar, { passive: true });

// Close the mobile navigation after choosing a destination.
const navbarMenu = document.getElementById('navbarNav');
document.querySelectorAll('#navbarNav a').forEach(link => {
    link.addEventListener('click', () => {
        if (navbarMenu && navbarMenu.classList.contains('show') && window.bootstrap) {
            bootstrap.Collapse.getOrCreateInstance(navbarMenu).hide();
        }
    });
});

// Project filtering on the work page.
const filterButtons = document.querySelectorAll('.filter-buttons .btn');
const projectItems = document.querySelectorAll('.project-item');
const filterEmptyState = document.querySelector('.filter-empty');

filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(item => item.classList.remove('active'));
        button.classList.add('active');
        const selectedCategory = button.dataset.filter;
        let visibleProjects = 0;

        projectItems.forEach(item => {
            const shouldShow = selectedCategory === 'all' || item.dataset.category === selectedCategory;
            item.hidden = !shouldShow;
            if (shouldShow) visibleProjects += 1;
        });

        if (filterEmptyState) filterEmptyState.hidden = visibleProjects !== 0;
    });
});

// Active navigation item, ignoring fragment identifiers.
const currentPath = window.location.pathname;
document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    const linkPath = new URL(link.href, window.location.origin).pathname;
    if (linkPath === currentPath && !link.hash) link.classList.add('active');
});

// Keep the footer year current without requiring a template update.
const year = document.getElementById('current-year');
if (year) year.textContent = new Date().getFullYear();
