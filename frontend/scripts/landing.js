document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Animation on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.feature-card, .step, .faq-item');
        
        elements.forEach((element, index) => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (elementPosition < screenPosition) {
                // Add delay based on element index for cascading effect
                setTimeout(() => {
                    element.style.opacity = 1;
                    element.style.transform = 'translateY(0)';
                }, index * 100); // 100ms delay between each element
            }
        });
    };
    
    // Set initial styles for animation
    document.querySelectorAll('.feature-card, .step, .faq-item').forEach(element => {
        element.style.opacity = 0;
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    // Animate section headings
    document.querySelectorAll('section > h2').forEach(heading => {
        heading.style.opacity = 0;
        heading.style.transform = 'translateY(20px)';
        heading.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    });
    
    const animateHeadings = () => {
        document.querySelectorAll('section > h2').forEach(heading => {
            const elementPosition = heading.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;
            
            if (elementPosition < screenPosition) {
                heading.style.opacity = 1;
                heading.style.transform = 'translateY(0)';
            }
        });
    };
    
    // Add animated background effect
    const moveBackground = () => {
        const shapes = document.querySelectorAll('.bg-animated-shape');
        window.addEventListener('mousemove', (e) => {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            shapes.forEach(shape => {
                const speed = parseFloat(shape.getAttribute('data-speed') || 0.05);
                const offsetX = (x * speed * 100);
                const offsetY = (y * speed * 100);
                
                shape.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${1 + (y * 0.05)})`;
            });
        });
    };
    
    // Set speed attributes for shapes
    document.querySelector('.bg-shape-1')?.setAttribute('data-speed', '0.05');
    document.querySelector('.bg-shape-2')?.setAttribute('data-speed', '0.03');
    document.querySelector('.bg-shape-3')?.setAttribute('data-speed', '0.07');
    document.querySelector('.bg-shape-4')?.setAttribute('data-speed', '0.04');
    document.querySelector('.bg-shape-5')?.setAttribute('data-speed', '0.06');
    
    // Add floating math symbols dynamically
    const addFloatingMathSymbols = () => {
        const mathSymbols = ['∫', 'π', '∑', '√', '×', '÷', 'θ', '∞', '+', '−', '=', 'α', 'β', 'Δ', 'λ'];
        const body = document.querySelector('body');
        
        // Add 5 more symbols dynamically
        for (let i = 0; i < 5; i++) {
            const symbol = document.createElement('div');
            symbol.className = 'math-symbol';
            symbol.textContent = mathSymbols[Math.floor(Math.random() * mathSymbols.length)];
            symbol.style.left = `${Math.random() * 80 + 10}%`;
            symbol.style.top = `${Math.random() * 30 + 40}%`;
            symbol.style.animationDuration = `${Math.random() * 20 + 30}s`;
            symbol.style.animationDelay = `${Math.random() * 15}s`;
            symbol.style.opacity = '0';
            symbol.style.fontSize = `${Math.random() * 1.5 + 1}rem`;
            body.appendChild(symbol);
        }
    };
    
    // Run animations
    window.addEventListener('scroll', () => {
        animateOnScroll();
        animateHeadings();
    });
    
    animateOnScroll();
    animateHeadings();
    moveBackground();
    addFloatingMathSymbols();
});
