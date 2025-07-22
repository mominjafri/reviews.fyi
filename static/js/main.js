document.addEventListener('DOMContentLoaded', function() {
    // Button hover effects
    const buttons = document.querySelectorAll('.action-btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-2px)';
            btn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0)';
            btn.style.boxShadow = 'none';
        });
    });

    // Footer link animations
    const footerLinks = document.querySelectorAll('footer a');
    footerLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            const icon = link.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1.1)';
            }
        });
        link.addEventListener('mouseleave', () => {
            const icon = link.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1)';
            }
        });
    });
});

// Smooth page transition system
function smoothTransition(url) {
    // Add fade-out class to main content
    document.querySelector('main').classList.add('fade-out');
    
    // After animation completes, navigate
    setTimeout(() => {
        window.location.href = url;
    }, 300); // Match this duration to your CSS transition
}

// Attach to all internal links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.href !== window.location.href) {
                e.preventDefault();
                smoothTransition(this.href);
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle functionality
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;
    
    // Check for saved user preference
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode === 'dark') {
        htmlElement.classList.add('dark-mode');
    } else if (savedMode === 'light') {
        htmlElement.classList.remove('dark-mode');
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // Default to system preference
        htmlElement.classList.add('dark-mode');
    }
    
    // Toggle dark mode
    darkModeToggle.addEventListener('click', function() {
        htmlElement.classList.toggle('dark-mode');
        
        // Save user preference
        const isDark = htmlElement.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark ? 'dark' : 'light');
    });
    
    // Watch for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (localStorage.getItem('darkMode') === null) {
            htmlElement.classList.toggle('dark-mode', e.matches);
        }
    });
});