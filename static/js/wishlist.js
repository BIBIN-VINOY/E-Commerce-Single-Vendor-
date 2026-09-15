/**
 * wishlist.js
 * Handles: Add to Cart (AJAX), and client-side search filtering of the
 * wishlist that's already rendered on the page.
 *
 * Note: "Remove" is a plain <form method="post"> in the template, so it
 * does a normal full-page reload on submit — no JS needed for that.
 *
 * Backend contract for Add to Cart:
 *   POST  <cart_add url>  -> JSON { ok: true } on success
 *   Non-2xx / JSON { ok: false, message: "..." } on failure.
 */

(function () {
  "use strict";

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  const CSRF_TOKEN = getCookie("csrftoken");

  function postJSON(url) {
    return fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": CSRF_TOKEN,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    }).then((res) => {
      if (!res.ok) throw new Error("Request failed");
      return res.json().catch(() => ({ ok: true }));
    });
  }

  function showToast(message) {
    const toast = document.getElementById("wl-toast");
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    void toast.offsetWidth; // re-trigger transition on repeated calls
    toast.classList.add("is-visible");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => {
      toast.classList.remove("is-visible");
      setTimeout(() => { toast.hidden = true; }, 200);
    }, 2200);
  }

  function handleAddToCart(e) {
    const btn = e.currentTarget;
    const url = btn.dataset.url;
    const cartUrl = btn.dataset.cartUrl || "/cart/";
    const originalText = btn.textContent;

    btn.disabled = true;
    btn.textContent = "Adding…";

    postJSON(url)
      .then(() => {
        const link = document.createElement("a");
        link.href = cartUrl;
        link.className = "wl-btn wl-btn--primary";
        link.textContent = "Go to Cart 🛒";

        btn.replaceWith(link);
        showToast("Added to cart");
      })
      .catch(() => {
        btn.textContent = originalText;
        btn.disabled = false;
        showToast("Couldn't add to cart. Please try again.");
      });
  }

  function initAddToCart() {
    document.querySelectorAll(".js-add-to-cart").forEach((btn) => {
      btn.addEventListener("click", handleAddToCart);
    });
  }

  /* ---------- Search: filters the wishlist cards already on the page ---------- */
  function initSearch() {
    const input = document.getElementById("wl-search-input");
    const grid = document.getElementById("wl-grid");
    const noResults = document.getElementById("wl-no-results");
    if (!input || !grid) return;

    const cards = Array.from(grid.querySelectorAll(".wl-card"));

    input.addEventListener("input", () => {
      const term = input.value.trim().toLowerCase();
      let visibleCount = 0;

      cards.forEach((card) => {
        const name = card.dataset.name || "";
        const matches = name.includes(term);
        card.hidden = !matches;
        if (matches) visibleCount += 1;
      });

      if (noResults) {
        noResults.hidden = visibleCount !== 0;
      }
      grid.hidden = visibleCount === 0 && term !== "";
    });
  }

  function init() {
    initAddToCart();
    initSearch();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();