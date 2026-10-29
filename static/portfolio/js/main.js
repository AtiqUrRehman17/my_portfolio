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
const filterPill = document.querySelector('.filter-pill');
const filterCount = document.querySelector('.filter-count');
const totalProjectCount = projectItems.length;

// Slide the highlight pill behind whichever filter button is active.
const movePillTo = (button) => {
    if (!filterPill || !button) return;
    filterPill.style.width = `${button.offsetWidth}px`;
    filterPill.style.height = `${button.offsetHeight}px`;
    filterPill.style.transform = `translate(${button.offsetLeft}px, ${button.offsetTop}px)`;
    filterPill.style.opacity = '1';
};

const updateFilterCount = (visibleProjects) => {
    if (!filterCount) return;
    filterCount.textContent = visibleProjects === totalProjectCount
        ? `Showing all ${totalProjectCount} projects`
        : `Showing ${visibleProjects} of ${totalProjectCount} projects`;
};

filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(item => item.classList.remove('active'));
        button.classList.add('active');
        movePillTo(button);
        const selectedCategory = button.dataset.filter;
        let visibleProjects = 0;

        projectItems.forEach(item => {
            const shouldShow = selectedCategory === 'all' || item.dataset.category === selectedCategory;
            item.hidden = !shouldShow;
            if (shouldShow) {
                visibleProjects += 1;
                // Restart the reveal animation on every project that's now visible.
                item.classList.remove('pop-in');
                void item.offsetWidth;
                item.classList.add('pop-in');
            }
        });

        updateFilterCount(visibleProjects);
        if (filterEmptyState) filterEmptyState.hidden = visibleProjects !== 0;
    });
});

if (filterButtons.length) {
    const initialButton = document.querySelector('.filter-buttons .btn.active') || filterButtons[0];
    movePillTo(initialButton);
    updateFilterCount(totalProjectCount);
    window.addEventListener('resize', () => {
        const activeButton = document.querySelector('.filter-buttons .btn.active');
        movePillTo(activeButton);
    });
}

// Active navigation item, ignoring fragment identifiers.
const currentPath = window.location.pathname;
document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    const linkPath = new URL(link.href, window.location.origin).pathname;
    if (linkPath === currentPath && !link.hash) link.classList.add('active');
});

// Keep the footer year current without requiring a template update.
const year = document.getElementById('current-year');
if (year) year.textContent = new Date().getFullYear();

// Typed/rotating "currently exploring" line on the home page.
const roleRotatorEl = document.querySelector('.role-rotator-text');
if (roleRotatorEl) {
    const items = (roleRotatorEl.dataset.items || '')
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);

    if (items.length && !prefersReducedMotion) {
        let itemIndex = 0;
        let charIndex = 0;
        let deleting = false;

        const tick = () => {
            const current = items[itemIndex];
            if (!deleting) {
                charIndex += 1;
                roleRotatorEl.textContent = current.slice(0, charIndex);
                if (charIndex === current.length) {
                    deleting = true;
                    setTimeout(tick, 1600);
                    return;
                }
            } else {
                charIndex -= 1;
                roleRotatorEl.textContent = current.slice(0, charIndex);
                if (charIndex === 0) {
                    deleting = false;
                    itemIndex = (itemIndex + 1) % items.length;
                }
            }
            setTimeout(tick, deleting ? 35 : 55);
        };
        tick();
    } else if (items.length) {
        roleRotatorEl.textContent = items[0];
    }
}

// Animate skill proficiency bars once they scroll into view.
const skillBars = document.querySelectorAll('.skill-bar-fill');
if (skillBars.length) {
    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
        skillBars.forEach(bar => bar.classList.add('in-view'));
    } else {
        const barObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    barObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });
        skillBars.forEach(bar => barObserver.observe(bar));
    }
}

// Simulated backend log terminal on the home page.
const terminalBody = document.getElementById('terminal-log');
if (terminalBody) {
    const logLines = [
        { text: '$ curl -X POST /api/rag/query -d "question=..."', type: 'cmd' },
        { text: '[INFO] Request received · session=8f2a', type: 'info' },
        { text: '[INFO] LangChain retriever: 4 chunks matched (score > 0.82)', type: 'info' },
        { text: '[INFO] GPT-4o-mini generating grounded response...', type: 'info' },
        { text: '[INFO] ElevenLabs TTS stream started', type: 'info' },
        { text: '[WARN] Deepgram latency spike: 340ms (threshold 250ms)', type: 'warn' },
        { text: '[OK] Response delivered · 200 · 912ms', type: 'ok' },
    ];
    const maxVisibleLines = 8;

    const appendLine = (line) => {
        const div = document.createElement('div');
        div.className = `log-line log-${line.type}`;
        div.textContent = line.text;
        terminalBody.appendChild(div);
        while (terminalBody.children.length > maxVisibleLines) {
            terminalBody.removeChild(terminalBody.firstChild);
        }
    };

    if (prefersReducedMotion) {
        logLines.forEach(appendLine);
    } else {
        let lineIndex = 0;

        const typeLine = () => {
            const line = logLines[lineIndex % logLines.length];
            const div = document.createElement('div');
            div.className = `log-line log-${line.type}`;
            terminalBody.appendChild(div);

            let charIndex = 0;
            const typeChar = () => {
                charIndex += 1;
                div.textContent = line.text.slice(0, charIndex);
                if (charIndex < line.text.length) {
                    setTimeout(typeChar, 18);
                } else {
                    while (terminalBody.children.length > maxVisibleLines) {
                        terminalBody.removeChild(terminalBody.firstChild);
                    }
                    lineIndex += 1;
                    setTimeout(typeLine, 650);
                }
            };
            typeChar();
        };
        typeLine();
    }
}

// Intro video: play only while visible, muted by default with a manual
// unmute toggle (browsers block autoplay with sound outright), and let the
// whole frame act as a play/pause control.
const introVideo = document.getElementById('intro-video-player');
if (introVideo) {
    const frame = introVideo.closest('.video-frame');
    const soundToggle = frame.querySelector('.video-sound-toggle');

    const updateSoundLabel = () => {
        if (!soundToggle) return;
        soundToggle.setAttribute('aria-pressed', String(!introVideo.muted));
        soundToggle.innerHTML = introVideo.muted
            ? '<i class="fas fa-volume-mute" aria-hidden="true"></i><span>Tap for sound</span>'
            : '<i class="fas fa-volume-up" aria-hidden="true"></i><span>Mute</span>';
    };
    updateSoundLabel();

    if (soundToggle) {
        soundToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            introVideo.muted = !introVideo.muted;
            updateSoundLabel();
        });
    }

    frame.addEventListener('click', () => {
        if (introVideo.paused) introVideo.play().catch(() => {});
        else introVideo.pause();
    });

    frame.classList.add('is-paused');
    introVideo.addEventListener('play', () => frame.classList.remove('is-paused'));
    introVideo.addEventListener('pause', () => frame.classList.add('is-paused'));

    // Only auto-start playback for visitors who haven't asked for reduced
    // motion, and only while the video is actually scrolled into view.
    if (!prefersReducedMotion && 'IntersectionObserver' in window) {
        const videoObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    introVideo.play().catch(() => {});
                } else {
                    introVideo.pause();
                }
            });
        }, { threshold: 0.5 });
        videoObserver.observe(introVideo);
    }
}

// Subtle tilt-on-hover for project cards.
if (!prefersReducedMotion && window.matchMedia('(hover: hover)').matches) {
    const maxTilt = 6;
    document.querySelectorAll('.project-card').forEach(card => {
        card.addEventListener('mousemove', (event) => {
            const rect = card.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            const rotateY = (x - 0.5) * maxTilt * 2;
            const rotateX = (0.5 - y) * maxTilt * 2;
            card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}
