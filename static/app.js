(function () {
    const layout = document.getElementById('analyzeLayout');
    const form = document.getElementById('predictForm');
    const panel = document.getElementById('resultPanel');
    const content = document.getElementById('resultContent');
    const closeBtn = document.getElementById('resultClose');
    const errorSlot = document.getElementById('errorSlot');
    const submitBtn = document.getElementById('analyzeBtn');

    if (!layout || !form || !panel || !content || !closeBtn || !errorSlot || !submitBtn) {
        return;
    }

    function openPanel() {
        layout.classList.add('has-result');
        panel.setAttribute('aria-hidden', 'false');
    }

    function closePanel() {
        layout.classList.remove('has-result');
        panel.setAttribute('aria-hidden', 'true');
    }

    function showError(message) {
        errorSlot.innerHTML = '';
        const box = document.createElement('div');
        box.className = 'error-box';
        const strong = document.createElement('strong');
        strong.textContent = 'Error: ';
        box.appendChild(strong);
        box.appendChild(document.createTextNode(message));
        errorSlot.appendChild(box);
    }

    function replayContentAnimation() {
        content.classList.remove('animate');
        void content.offsetWidth;
        content.classList.add('animate');
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        if (submitBtn.disabled) {
            return;
        }

        errorSlot.innerHTML = '';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing…';
        form.classList.add('is-loading');

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new FormData(form)
            });
            const data = await response.json();

            if (data.status !== 'success') {
                showError(data.message || 'Analysis failed. Please try again.');
                return;
            }

            content.innerHTML = data.html;
            replayContentAnimation();
            openPanel();

            if (window.matchMedia('(max-width: 900px)').matches) {
                panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } catch (err) {
            showError('Could not reach the server. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analyze';
            form.classList.remove('is-loading');
        }
    });

    closeBtn.addEventListener('click', function () {
        closePanel();
        form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
})();

(function () {
    const enabled = window.matchMedia('(pointer: fine) and (prefers-reduced-motion: no-preference)').matches;
    if (!enabled) {
        return;
    }

    const glow = document.querySelector('.cursor-glow');
    const ring = document.querySelector('.cursor-ring');
    if (!glow || !ring) {
        return;
    }

    let mouseX = -100;
    let mouseY = -100;
    let glowX = -100;
    let glowY = -100;
    let ringX = -100;
    let ringY = -100;

    function showCursor(visible) {
        glow.style.opacity = visible ? '1' : '0';
        ring.style.opacity = visible ? '1' : '0';
    }

    window.addEventListener('pointermove', function (event) {
        mouseX = event.clientX;
        mouseY = event.clientY;
        showCursor(true);
    }, { passive: true });

    document.addEventListener('mouseleave', function () {
        showCursor(false);
    });

    window.addEventListener('blur', function () {
        showCursor(false);
    });

    const interactive = 'a, button, input, select, textarea, label';

    document.addEventListener('pointerover', function (event) {
        if (event.target.closest && event.target.closest(interactive)) {
            ring.classList.add('is-hover');
        }
    });

    document.addEventListener('pointerout', function (event) {
        if (event.target.closest && event.target.closest(interactive)) {
            ring.classList.remove('is-hover');
        }
    });

    (function frame() {
        glowX += (mouseX - glowX) * 0.09;
        glowY += (mouseY - glowY) * 0.09;
        ringX += (mouseX - ringX) * 0.3;
        ringY += (mouseY - ringY) * 0.3;

        glow.style.transform = 'translate(' + glowX + 'px,' + glowY + 'px) translate(-50%,-50%)';
        ring.style.transform = 'translate(' + ringX + 'px,' + ringY + 'px) translate(-50%,-50%)';

        requestAnimationFrame(frame);
    })();
})();
