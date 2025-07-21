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