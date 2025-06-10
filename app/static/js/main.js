/**
 * PrecatoFácil - Scripts Principais
 * Autor: Manus AI
 * Data: 05/06/2025
 */

document.addEventListener('DOMContentLoaded', function() {
    // Menu Mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const navList = document.querySelector('.nav-list');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            navList.classList.toggle('active');
            
            // Altera o ícone do menu
            const hamburger = this.querySelector('.hamburger');
            if (navList.classList.contains('active')) {
                hamburger.style.background = 'transparent';
                hamburger.style.transform = 'rotate(180deg)';
                hamburger.style.transition = 'all 0.3s ease';
                
                hamburger.style.background = 'transparent';
                hamburger.style.transform = 'rotate(180deg)';
                
                hamburger.style.before = {
                    transform: 'rotate(45deg) translate(5px, 5px)'
                };
                
                hamburger.style.after = {
                    transform: 'rotate(-45deg) translate(5px, -5px)'
                };
            } else {
                hamburger.style.background = '#1A365D';
                hamburger.style.transform = 'rotate(0)';
            }
        });
    }
    
    // Fechar menu ao clicar em um link
    const navLinks = document.querySelectorAll('.nav-list a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navList.classList.remove('active');
        });
    });
    
    // Header fixo com mudança de estilo ao scroll
    const header = document.querySelector('.header');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            header.style.background = '#fff';
        } else {
            header.style.boxShadow = 'none';
            header.style.background = '#fff';
        }
    });
    
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', function() {
            // Fecha todos os outros itens
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Abre/fecha o item atual
            item.classList.toggle('active');
            
            // Altera o ícone
            const icon = item.querySelector('.faq-toggle i');
            if (item.classList.contains('active')) {
                icon.classList.remove('fa-plus');
                icon.classList.add('fa-minus');
            } else {
                icon.classList.remove('fa-minus');
                icon.classList.add('fa-plus');
            }
        });
    });
    
    // Carrossel de depoimentos simples
    const testimonials = document.querySelectorAll('.testimonial');
    const dots = document.querySelectorAll('.dot');
    let currentTestimonial = 0;
    
    // Função para mostrar um depoimento específico
    function showTestimonial(index) {
        // Esconde todos os depoimentos
        testimonials.forEach(testimonial => {
            testimonial.style.display = 'none';
        });
        
        // Remove a classe active de todos os dots
        dots.forEach(dot => {
            dot.classList.remove('active');
        });
        
        // Mostra o depoimento atual
        if (testimonials[index]) {
            testimonials[index].style.display = 'block';
        }
        
        // Adiciona a classe active ao dot atual
        if (dots[index]) {
            dots[index].classList.add('active');
        }
    }
    
    // Inicializa o carrossel
    if (testimonials.length > 0) {
        showTestimonial(currentTestimonial);
        
        // Adiciona evento de clique aos dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', function() {
                showTestimonial(index);
                currentTestimonial = index;
            });
        });
        
        // Rotação automática a cada 5 segundos
        setInterval(function() {
            currentTestimonial = (currentTestimonial + 1) % testimonials.length;
            showTestimonial(currentTestimonial);
        }, 5000);
    }
    
    // Validação do formulário de contato
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validação básica
            let isValid = true;
            const requiredFields = contactForm.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            // Validação de email
            const emailField = contactForm.querySelector('#email');
            if (emailField && emailField.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailField.value)) {
                    isValid = false;
                    emailField.style.borderColor = 'red';
                }
            }
            
            // Se tudo estiver válido, simula o envio
            if (isValid) {
                // Aqui seria a lógica de envio do formulário
                alert('Formulário enviado com sucesso! Em breve entraremos em contato.');
                contactForm.reset();
            } else {
                alert('Por favor, preencha todos os campos obrigatórios corretamente.');
            }
        });
    }
    
    // Animações de scroll
    const animateElements = document.querySelectorAll('.benefit-card, .step, .type-card');
    
    function checkScroll() {
        const triggerBottom = window.innerHeight * 0.8;
        
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            
            if (elementTop < triggerBottom) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Inicializa os elementos com opacidade 0
    animateElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.5s ease';
    });
    
    // Verifica o scroll inicial e adiciona evento de scroll
    window.addEventListener('scroll', checkScroll);
    checkScroll();
});

