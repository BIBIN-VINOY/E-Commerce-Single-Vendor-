/**
 * product-detail.js
 *
 * Handles:
 *   1. Quantity +/- stepper (bounded by the active variant's stock)
 *   2. Color/variant switching — updates stock, primary image, gallery
 *      (price is NOT variant-specific in this schema, so it never changes)
 *
 * Expects a <script type="application/json" id="variants-data"> tag,
 * rendered via Django's json_script filter, built in the view like:
 *
 *   def build_variants_data(product):
 *       data = {}
 *       for variant in product.variants.filter(is_active=True):
 *           images = list(variant.images.all())
 *           primary = next((i for i in images if i.is_primary), images[0] if images else None)
 *           data[str(variant.id)] = {
 *               "stock": variant.stock,
 *               "color": variant.color.name,
 *               "color_hex": variant.color.hex_code,
 *               "primary_image": primary.image.url if primary else "",
 *               "gallery_images": [i.image.url for i in images],
 *           }
 *       return data
 *
 *   context["variants_data"] = build_variants_data(product)
 */

document.addEventListener("DOMContentLoaded", function () {
  const variantDataEl = document.getElementById("variants-data");
  if (!variantDataEl) {
    console.warn("product-detail.js: #variants-data not found on page.");
    return;
  }

  const variants = JSON.parse(variantDataEl.textContent);

  const primaryImageEl = document.getElementById("primaryImage");
  const primaryImagePlaceholder = document.getElementById("primaryImagePlaceholder");
  const galleryEl = document.getElementById("galleryThumbnails");
  const stockStatusEl = document.getElementById("stockStatus");
  const colorOptions = document.querySelectorAll(".color-option");
  const qtyInput = document.getElementById("qtyInput");
  const qtyMinus = document.getElementById("qtyMinus");
  const qtyPlus = document.getElementById("qtyPlus");
  const addToCartBtn = document.getElementById("addToCartBtn");
  const wishlistBtn = document.getElementById("wishlistBtn");

  /* ---------------- Variant switching ---------------- */

  function renderGallery(imageUrls) {
    if (!galleryEl) return;
    galleryEl.innerHTML = "";
    imageUrls.forEach(function (url, index) {
      const img = document.createElement("img");
      img.className = "thumbnail" + (index === 0 ? " active" : "");
      img.src = url;
      img.dataset.full = url;
      galleryEl.appendChild(img);
    });
  }

  function setPrimaryImage(url) {
    if (!primaryImageEl) return;
    if (url) {
      primaryImageEl.src = url;
      primaryImageEl.style.display = "";
      if (primaryImagePlaceholder) primaryImagePlaceholder.style.display = "none";
    } else {
      primaryImageEl.style.display = "none";
      if (primaryImagePlaceholder) primaryImagePlaceholder.style.display = "";
    }
  }

  function applyVariant(variantId) {
    const data = variants[variantId];
    if (!data) return;

    const inStock = data.stock > 0;
    if (stockStatusEl) {
      stockStatusEl.textContent = inStock ? "In Stock" : "Out of Stock";
      stockStatusEl.classList.toggle("in-stock", inStock);
      stockStatusEl.classList.toggle("out-of-stock", !inStock);
    }

    setPrimaryImage(data.primary_image);
    renderGallery(data.gallery_images || []);

    colorOptions.forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.variantId === String(variantId));
    });

    if (qtyInput) {
      qtyInput.value = 1;
      qtyInput.max = data.stock;
    }

    if (addToCartBtn) {
      addToCartBtn.dataset.variantId = variantId;
      addToCartBtn.dataset.url = data.cart_url || `/cart/add/${variantId}/`;
      if (addToCartBtn.tagName === "A") {
        addToCartBtn.href = data.is_in_cart ? "/cart/" : addToCartBtn.dataset.url;
      }
      if (data.is_in_cart) {
        addToCartBtn.textContent = "Go to Cart 🛒";
        if (addToCartBtn.tagName === "BUTTON") addToCartBtn.disabled = false;
      } else {
        addToCartBtn.textContent = "Add to Cart 🛒";
        if (addToCartBtn.tagName === "BUTTON") addToCartBtn.disabled = !inStock;
      }
    }

    if (wishlistBtn) {
      wishlistBtn.dataset.variantId = variantId;
      wishlistBtn.dataset.url = data.wishlist_url || `/wishlist/add/${variantId}/`;
      if (wishlistBtn.tagName === "A") {
        wishlistBtn.href = data.is_wishlisted ? "/wishlist/" : wishlistBtn.dataset.url;
      }
      if (data.is_wishlisted) {
        wishlistBtn.textContent = "❤️ Wishlisted";
      } else {
        wishlistBtn.textContent = "🤍 Add to Wishlist";
      }
    }
  }

  colorOptions.forEach(function (btn) {
    btn.addEventListener("click", function () {
      applyVariant(btn.dataset.variantId);
    });
  });

  const activeVariantId = document.querySelector(".color-option.active")?.dataset.variantId || Object.keys(variants)[0];
  if (activeVariantId) {
    applyVariant(activeVariantId);
  }

  /* ---------------- Quantity stepper ---------------- */

  function currentStock() {
    return parseInt(qtyInput.max, 10) || 1;
  }

  qtyMinus.addEventListener("click", function () {
    const value = parseInt(qtyInput.value, 10) || 1;
    if (value > 1) qtyInput.value = value - 1;
  });

  qtyPlus.addEventListener("click", function () {
    const value = parseInt(qtyInput.value, 10) || 1;
    if (value < currentStock()) {
      qtyInput.value = value + 1;
    }
  });

  /* ---------------- Gallery thumbnail click -> swap primary image ---------------- */

  if (galleryEl) {
    galleryEl.addEventListener("click", function (e) {
      if (!e.target.classList.contains("thumbnail")) return;
      setPrimaryImage(e.target.dataset.full);
      galleryEl.querySelectorAll(".thumbnail").forEach(function (t) {
        t.classList.remove("active");
      });
      e.target.classList.add("active");
    });
  }

  /* ---------------- Add to cart / wishlist (placeholders) ---------------- */
  /* Point these at your real endpoints once you share cart/wishlist views. */

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  if (addToCartBtn) {
    addToCartBtn.addEventListener("click", function (event) {
      event.preventDefault();
      const variantId = addToCartBtn.dataset.variantId;
      const quantity = qtyInput ? qtyInput.value : 1;
      const url = addToCartBtn.dataset.url || `/cart/add/${variantId}/`;

      console.log("Add to cart clicked");
      console.log(url);
      fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ variant_id: variantId, quantity: quantity }),
      })
        .then((res) => res.json())
        .then((data) => {
          addToCartBtn.outerHTML =
            `<a href="/cart/" id="addToCartBtn" class="cart-btn">
            Go to Cart 🛒
          </a>`;
        });
    });
  }

  if (wishlistBtn) {
    wishlistBtn.addEventListener("click", function (event) {
      event.preventDefault();
      const variantId = wishlistBtn.dataset.variantId;
      const url = wishlistBtn.dataset.url || `/wishlist/add/${variantId}/`;

      console.log("Wishlist clicked");
      console.log(url);
      fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ variant_id: variantId }),
      })
        .then((res) => res.json())
        .then((data) => {
          wishlistBtn.outerHTML =
            `<a href="/wishlist/" id="wishlistBtn" class="wishlist-btn">
            ❤️ Wishlisted
          </a>`;
        });
    });
  }
});

