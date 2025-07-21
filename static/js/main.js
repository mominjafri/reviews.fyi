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