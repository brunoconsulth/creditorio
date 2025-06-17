document.addEventListener('DOMContentLoaded', function() {
    // Menu Mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const navList = document.querySelector('.nav-list');
    
    if (menuToggle && navList) {
        menuToggle.addEventListener('click', function() {
            navList.classList.toggle('active');
            const hamburger = this.querySelector('.hamburger');
            
            if (hamburger) {
                if (navList.classList.contains('active')) {
                    hamburger.style.background = 'transparent';
                    hamburger.style.transform = 'rotate(180deg)';
                    hamburger.style.transition = 'all 0.3s ease';
                    hamburger.classList.add('active');
                } else {
                    hamburger.style.background = '#1A365D';
                    hamburger.style.transform = 'rotate(0)';
                    hamburger.classList.remove('active');
                }
            }
        });
    }

    // Fechar menu ao clicar em um link
    const navLinks = document.querySelectorAll('.nav-list a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navList) navList.classList.remove('active');
        });
    });

    // Header fixo com mudança de estilo ao scroll
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
                header.style.background = '#fff';
            } else {
                header.style.boxShadow = 'none';
                header.style.background = '#fff';
            }
        });
    }

    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.addEventListener('click', function() {
                // Fecha todos os outros itens
                faqItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove('active');
                        const otherIcon = otherItem.querySelector('.faq-toggle i');
                        if (otherIcon) {
                            otherIcon.classList.remove('fa-minus');
                            otherIcon.classList.add('fa-plus');
                        }
                    }
                });
                
                // Abre/fecha o item atual
                item.classList.toggle('active');
                
                // Altera o ícone
                const icon = item.querySelector('.faq-toggle i');
                if (icon) {
                    if (item.classList.contains('active')) {
                        icon.classList.remove('fa-plus');
                        icon.classList.add('fa-minus');
                    } else {
                        icon.classList.remove('fa-minus');
                        icon.classList.add('fa-plus');
                    }
                }
            });
        }
    });
    
    // Carrossel de depoimentos simples
    const testimonials = document.querySelectorAll('.testimonial');
    const dots = document.querySelectorAll('.dot');
    let currentTestimonial = 0;
    let testimonialInterval;
    
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
    if (testimonials.length > 0 && dots.length > 0) {
        showTestimonial(currentTestimonial);
        
        // Adiciona evento de clique aos dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', function() {
                currentTestimonial = index;
                showTestimonial(currentTestimonial);
                resetTestimonialInterval();
            });
        });
        
        // Rotação automática
        function startTestimonialInterval() {
            testimonialInterval = setInterval(function() {
                currentTestimonial = (currentTestimonial + 1) % testimonials.length;
                showTestimonial(currentTestimonial);
            }, 5000);
        }
        
        function resetTestimonialInterval() {
            clearInterval(testimonialInterval);
            startTestimonialInterval();
        }
        
        startTestimonialInterval();
    }

    // Formulário de precatórios
    const estadoSelect = document.getElementById("estado");
    const municipioSelect = document.getElementById("municipio");
    const tipoSelect = document.getElementById("precatory-type");
    const estadoGroup = document.getElementById("estado-group");
    const municipioGroup = document.getElementById("municipio-group");

    // === API IBGE: Carregar estados ===
    if (estadoSelect) {
        fetch("https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome")
            .then(res => {
                if (!res.ok) throw new Error('Falha ao carregar estados');
                return res.json();
            })
            .then(estados => {
                estadoSelect.innerHTML = '<option value="">Selecione o estado</option>';
                estados.forEach(estado => {
                    const opt = document.createElement("option");
                    opt.value = estado.sigla;
                    opt.textContent = `${estado.nome} (${estado.sigla})`;
                    estadoSelect.appendChild(opt);
                });
            })
            .catch(error => {
                console.error('Erro ao carregar estados:', error);
                estadoSelect.innerHTML = '<option value="">Erro ao carregar estados</option>';
            });
    }

    // === Mostrar/ocultar campos baseado no tipo ===
    if (tipoSelect && estadoGroup && municipioGroup) {
        tipoSelect.addEventListener("change", function() {
            const tipo = this.value;
            estadoGroup.style.display = (tipo === "estadual" || tipo === "municipal") ? "block" : "none";
            municipioGroup.style.display = (tipo === "municipal") ? "block" : "none";
            
            // Limpa o município quando o tipo muda
            if (municipioSelect && tipo !== "municipal") {
                municipioSelect.innerHTML = '<option value="">Selecione o município</option>';
            }
        });
    }

    // === API IBGE: Carregar municípios ===
    if (estadoSelect && municipioSelect) {
        estadoSelect.addEventListener("change", function() {
            const uf = this.value;
            if (!uf) return;
            
            municipioSelect.innerHTML = '<option value="">Carregando municípios...</option>';
            fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`)
                .then(res => {
                    if (!res.ok) throw new Error('Falha ao carregar municípios');
                    return res.json();
                })
                .then(municipios => {
                    municipioSelect.innerHTML = '<option value="">Selecione o município</option>';
                    municipios.forEach(m => {
                        const opt = document.createElement("option");
                        opt.value = m.nome;
                        opt.textContent = m.nome;
                        municipioSelect.appendChild(opt);
                    });
                })
                .catch(error => {
                    console.error('Erro ao carregar municípios:', error);
                    municipioSelect.innerHTML = '<option value="">Erro ao carregar municípios</option>';
                });
        });
    }

    // === Função genérica para aplicar máscaras ===
    function maskInput(input, formatter) {
        if (!input) return;
        
        input.addEventListener("input", function() {
            this.value = formatter(this.value);
        });
        
        // Aplica a máscara no valor inicial se existir
        if (input.value) {
            input.value = formatter(input.value);
        }
    }

    // === Máscaras ===
    const formatPhone = v => v.replace(/\D/g, '').slice(0,11)
        .replace(/^(\d{2})(\d)/g, "($1) $2")
        .replace(/(\d{5})(\d)/, "$1-$2");

    const formatMoney = v => {
        v = v.replace(/\D/g, '');
        v = (v / 100).toFixed(2).replace('.', ',');
        return 'R$ ' + v.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.");
    };

    const formatDoc = v => {
        v = v.replace(/\D/g, '');
        if (v.length <= 11) {
            return v.slice(0,11)
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
        } else {
            return v.slice(0,14)
                .replace(/^(\d{2})(\d)/, "$1.$2")
                .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
                .replace(/\.(\d{3})(\d)/, ".$1/$2")
                .replace(/(\d{4})(\d)/, "$1-$2");
        }
    };

    const formatDate = v => v.replace(/\D/g, '').slice(0,8)
        .replace(/(\d{2})(\d)/, "$1/$2")
        .replace(/(\d{2})(\d)/, "$1/$2");

    // === Aplicar máscaras nos campos ===
    maskInput(document.querySelector(".mask-phone"), formatPhone);
    maskInput(document.querySelector(".mask-money"), formatMoney);
    maskInput(document.querySelector(".mask-doc"), formatDoc);
    maskInput(document.querySelector(".mask-date"), formatDate);

    // === Validação simples de e-mail ===
    const emailInput = document.querySelector(".validate-email");
    if (emailInput) {
        emailInput.addEventListener("blur", function() {
            const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
            if (!isValid && this.value !== '') {
                alert("E-mail inválido! Verifique o formato.");
                this.focus();
            }
        });
    }

    // === Formulário de contato ===
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validação do checkbox de termos
            const termsCheckbox = document.getElementById('terms');
            if (termsCheckbox && !termsCheckbox.checked) {
                alert('Por favor, aceite os termos e condições');
                termsCheckbox.focus();
                return;
            }
            
            const formData = {
                'precatory-type': document.getElementById('precatory-type')?.value,
                'acao': document.getElementById('acao')?.value,
                'cpf_cnpj': document.getElementById('cpf_cnpj')?.value.replace(/\D/g,''),
                'name': document.getElementById('name')?.value,
                'email': document.getElementById('email')?.value,
                'phone': document.getElementById('phone')?.value.replace(/\D/g,''),
                'estado': document.getElementById('estado')?.value,
                'municipio': document.getElementById('municipio')?.value,
                'value': document.getElementById('value')?.value.replace(/\D/g,''),
                'message': document.getElementById('message')?.value,
                'terms': document.getElementById('terms')?.checked
            };

            try {
                // Substitua pela URL correta do seu endpoint
                const response = await fetch('/formulario-contato', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    alert('Enviado com sucesso, em breve entraremos em contato');
                    this.reset();
                } else {
                    const errorData = await response.json();
                    alert(errorData.message || 'Erro ao enviar, tente novamente.');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Erro ao enviar, tente novamente.');
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