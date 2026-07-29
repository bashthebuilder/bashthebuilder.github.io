document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.querySelector('.nav-toggle');
    var links = document.querySelector('.nav-links');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
        var isOpen = links.classList.toggle('open');
        toggle.classList.toggle('open', isOpen);
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    function closeMenu() {
        links.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
    }

    links.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', closeMenu);
    });

    document.addEventListener('click', function (e) {
        if (links.classList.contains('open') && !links.contains(e.target) && !toggle.contains(e.target)) {
            closeMenu();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && links.classList.contains('open')) closeMenu();
    });
});
