document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('nav');
    const isHomePage = window.location.pathname === '/' || window.location.pathname === '/es/' || window.location.pathname === '/en/';
    
    if (!navbar) return;
    
    // Common navbar styles for all pages
    navbar.classList.add('w-full', 'transition-all', 'duration-300');
   
    // Only apply fixed position and scroll effects on home page
    if (isHomePage) {
        // Set initial transparent background for home page
        navbar.classList.add('fixed', 'top-0', 'left-0', 'bg-transparent');
        
        // Apply initial style for transitions
        navbar.style.cssText = `
            background-size: 0 100%;
            background-position: center;
            transition: background-size 250ms ease;
            background-image: linear-gradient(to right, #3730a3, #312e81, #1e1b4b, #1e1b4b);
            background-repeat: no-repeat;
        `;
        
        // Handle scroll events for home page
        let lastScroll = 0;
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            // When scrolling down, add background color and shadow
            if (currentScroll > 10) {
                navbar.classList.remove('bg-transparent');
                navbar.style.backgroundSize = '100% 100%'; // Expand from center to edges
                navbar.classList.add('bg-gradient-to-r', 'from-indigo-800', 'via-indigo-950','to-indigo-950', 'shadow-md');
            } else {
                // When at the top, make it transparent again
                navbar.classList.remove('bg-gradient-to-r', 'from-indigo-800', 'via-indigo-950','to-indigo-950', 'shadow-md');
                navbar.style.backgroundSize = '0 100%'; // Shrink from edges to center
                navbar.classList.add('bg-transparent');
            }
            
            lastScroll = currentScroll;
        });
    } else {
        // For other pages, static navbar with solid color
        navbar.classList.add('bg-gradient-to-r', 'from-indigo-800', 'via-indigo-950','to-indigo-950', 'shadow-md');
        navbar.classList.remove('top-0', 'left-0');
        navbar.style.position = 'relative';
        document.body.style.paddingTop = '0';
    }
    
    // Mobile menu functionality
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuOverlay = document.getElementById('mobile-menu-overlay');
    
    if (mobileMenuButton && mobileMenu && menuOverlay) {
        const menuIcon = mobileMenuButton.querySelector('.menu-icon');
        const closeIcon = mobileMenuButton.querySelector('.close-icon');
        let isMenuOpen = false;
        
        // Function to open the menu
        function openMenu() {
            if (isMenuOpen) return;
            
            // Show overlay
            menuOverlay.classList.remove('hidden');
            menuOverlay.classList.add('opacity-0');
            
            // Force reflow for animation
            void menuOverlay.offsetWidth;
            
            // Animate overlay
            menuOverlay.classList.remove('opacity-0');
            menuOverlay.classList.add('opacity-100');
            
            // Show menu
            mobileMenu.classList.remove('scale-y-0', 'opacity-0', 'h-0', '-translate-y-full');
            mobileMenu.classList.add('scale-y-100', 'opacity-100', 'h-auto', 'translate-y-0');
            
            // Change icon
            menuIcon.classList.add('hidden');
            closeIcon.classList.remove('hidden');
            
            isMenuOpen = true;
            mobileMenuButton.setAttribute('aria-expanded', 'true');
            
            // Lock body scroll
            document.body.style.overflow = 'hidden';
        }
        
        // Function to close the menu
        function closeMenu() {
            if (!isMenuOpen) return;
            
            // Hide menu
            mobileMenu.classList.remove('scale-y-100', 'opacity-100', 'h-auto', 'translate-y-0');
            mobileMenu.classList.add('scale-y-0', 'opacity-0', 'h-0', '-translate-y-full');
            
            // Hide overlay
            menuOverlay.classList.remove('opacity-100');
            menuOverlay.classList.add('opacity-0');
            
            // Change icon
            menuIcon.classList.remove('hidden');
            closeIcon.classList.add('hidden');
            
            isMenuOpen = false;
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Hide overlay after animation
            setTimeout(() => {
                if (!isMenuOpen) {
                    menuOverlay.classList.add('hidden');
                }
            }, 300);
        }
        
        // Toggle menu function
        function toggleMenu() {
            if (isMenuOpen) {
                closeMenu();
            } else {
                openMenu();
            }
        }
        
        // Event listeners
        mobileMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleMenu();
        });
        
        menuOverlay.addEventListener('click', closeMenu);
        
        // Close menu when clicking on a link
        document.querySelectorAll('#mobile-menu a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });
        
        // Close menu with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isMenuOpen) {
                closeMenu();
            }
        });
        
        // Prevent menu from closing when clicking inside it
        mobileMenu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
});
