(function () {
  const sidebar = document.querySelector('#chapter-sidebar');
  const toggle = document.querySelector('.sidebar-toggle');

  if (sidebar && toggle) {
    toggle.addEventListener('click', () => {
      const isOpen = sidebar.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    sidebar.addEventListener('click', (event) => {
      if (event.target.closest('a') && sidebar.classList.contains('is-open')) {
        sidebar.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Mark code figures that require a live run / secret with an accessible badge.
  document.querySelectorAll('figure.code.needs-secret').forEach((figure) => {
    if (figure.querySelector('.code-badge')) return;
    const badge = document.createElement('span');
    badge.className = 'code-badge';
    badge.textContent = '🔒 Requires a secret / live run';
    const caption = figure.querySelector(':scope > figcaption');
    if (caption) {
      caption.insertBefore(badge, caption.firstChild);
    } else {
      figure.insertBefore(badge, figure.firstChild);
    }
  });

  // Add a copy button to every code block, hosted by its figure or a wrapper div.
  document.querySelectorAll('pre > code').forEach((codeBlock) => {
    const pre = codeBlock.parentElement;
    if (!pre) return;

    const figure = pre.closest('figure.code');
    let host;
    if (figure) {
      host = figure;
    } else if (pre.parentElement.classList.contains('code-block')) {
      host = pre.parentElement;
    } else {
      host = document.createElement('div');
      host.className = 'code-block';
      pre.parentNode.insertBefore(host, pre);
      host.appendChild(pre);
    }
    if (host.querySelector(':scope > .copy-code')) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    host.appendChild(button);

    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(codeBlock.textContent);
        button.textContent = 'Copied';
        window.setTimeout(() => { button.textContent = 'Copy'; }, 1600);
      } catch (_error) {
        button.textContent = 'Copy failed';
        window.setTimeout(() => { button.textContent = 'Copy'; }, 1600);
      }
    });
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const id = link.getAttribute('href').slice(1);
      if (!id) return;
      const target = document.getElementById(decodeURIComponent(id));
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.pushState(null, '', `#${id}`);
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  });

  if (window.hljs) {
    window.hljs.configure({ languages: ['yaml', 'yml', 'bash', 'shell', 'json', 'markdown', 'python', 'javascript', 'http'] });
    window.hljs.highlightAll();
  }
})();
