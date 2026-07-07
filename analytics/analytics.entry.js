// Cookieless Azure Application Insights (RUM) for the gh-aw book.
//
// Uses the dependency-free BEACON transport from @webmaxru/cookieless-insights:
// no cookies, no local/session storage, no persistent id -> no consent banner.
// The connection string is a PUBLIC client key injected at build time by
// site/generate.py as `window.__APPINSIGHTS_CONNECTION_STRING__` (empty in local
// builds, so analytics is a no-op unless a key is present).
//
// Bundled to site/assets/analytics.js via `npm run build:analytics` (esbuild).

import {
  init,
  trackEvent,
  trackChangeDebounced,
  getClient,
} from '@webmaxru/cookieless-insights';

// ─────────────────────────────────────────────────────────────────────────
// KILL SWITCH: set to false to disable ALL telemetry (no beacon, no events).
const ANALYTICS_ENABLED = true;
// ─────────────────────────────────────────────────────────────────────────

const connectionString =
  (typeof window !== 'undefined' && window.__APPINSIGHTS_CONNECTION_STRING__) || '';

// Safe no-op when disabled or when no connection string is present. Sends an
// automatic page view on init (cookieless, in-memory session id per page load).
init({
  connectionString,
  enabled: ANALYTICS_ENABLED,
  cloudRole: 'gh-aw-book',
});

// Coarse, non-PII page context attached to every custom event.
function context() {
  const isHome = !!(document.body && document.body.classList.contains('home'));
  return { page: isHome ? 'home' : 'chapter', path: location.pathname };
}

function langOf(codeEl) {
  const cls = (codeEl && codeEl.className) || '';
  const match = cls.match(/(?:language|lang)-([a-z0-9]+)/i);
  return match ? match[1].toLowerCase() : 'text';
}

function trackLink(link) {
  const href = link.getAttribute('href') || '';
  if (!href || href.startsWith('javascript:')) return;

  // In-page anchor: reader jumped to a section (TOC, "Contents", section links).
  if (href.startsWith('#')) {
    trackEvent('Section Navigated', { ...context(), hash: href.slice(0, 80) });
    return;
  }

  let url;
  try {
    url = new URL(href, location.href);
  } catch {
    return;
  }

  if (url.origin !== location.origin) {
    // Outbound: book repo, gh-aw, docs, author links, etc.
    trackEvent('Outbound Link Clicked', { ...context(), host: url.host, href: url.href });
    return;
  }

  // Same-origin navigation between book pages (chapter cards, pager, brand).
  const label = (link.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  trackEvent('Internal Link Clicked', { ...context(), to: url.pathname + url.hash, label });
}

function onClick(event) {
  const el = event.target instanceof Element ? event.target : null;
  if (!el) return;

  const themeBtn = el.closest('.theme-opt');
  if (themeBtn) {
    trackEvent('Theme Changed', { ...context(), theme: themeBtn.dataset.themeValue || 'unknown' });
    return;
  }

  const sidebarBtn = el.closest('.sidebar-toggle');
  if (sidebarBtn) {
    // aria-expanded still holds the pre-toggle state at click time; invert it.
    const willOpen = sidebarBtn.getAttribute('aria-expanded') !== 'true';
    trackEvent('Chapter Sidebar Toggled', { ...context(), open: String(willOpen) });
    return;
  }

  const copyBtn = el.closest('.copy-code');
  if (copyBtn) {
    const host = copyBtn.closest('figure.code, .code-block');
    const codeEl = host ? host.querySelector('code') : null;
    trackEvent('Code Copied', { ...context(), language: codeEl ? langOf(codeEl) : 'text' });
    return;
  }

  const link = el.closest('a[href]');
  if (link) trackLink(link);
}

// Debounced typing / slider drags. The site has no such inputs today; this
// future-proofs any range slider, search box, or textarea by collapsing rapid
// changes into a single event per control.
function onInput(event) {
  const el = event.target instanceof Element ? event.target : null;
  if (!el) return;
  const tag = el.tagName;
  const type = (el.getAttribute && el.getAttribute('type')) || '';
  const isTextInput =
    tag === 'INPUT' && ['range', 'text', 'search', 'number', ''].includes(type);
  if (isTextInput || tag === 'TEXTAREA' || el.getAttribute('contenteditable') === 'true') {
    const key = el.id || el.getAttribute('name') || type || tag.toLowerCase();
    trackChangeDebounced('Input Changed', String(key));
  }
}

function wire() {
  // "Opened via shared link": arrived on a deep link to a specific section.
  if (location.hash && location.hash.length > 1) {
    trackEvent('Opened Via Shared Link', { ...context(), hash: location.hash.slice(0, 80) });
  }
  // Capture phase so we still see events even if a handler stops propagation.
  document.addEventListener('click', onClick, true);
  document.addEventListener('input', onInput, true);
}

// Only attach listeners when telemetry is actually live (no-op otherwise).
if (getClient() && getClient().enabled) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire, { once: true });
  } else {
    wire();
  }
}
