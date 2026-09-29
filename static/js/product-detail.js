document.addEventListener("DOMContentLoaded", function () {

  /* =========================================================
     GET VARIANT DATA
  ========================================================= */

  const variantDataEl = document.getElementById("variants-data");

  if (!variantDataEl) {
    console.warn(
      "product-detail.js: #variants-data not found on page."
    );
    return;
  }

  const variants = JSON.parse(variantDataEl.textContent);


  /* =========================================================
     DOM ELEMENTS
  ========================================================= */

  const primaryImageEl =
    document.getElementById("primaryImage");

  const primaryImagePlaceholder =
    document.getElementById("primaryImagePlaceholder");
  
  const productPriceEl =
    document.getElementById("productPrice");

  const galleryEl =
    document.getElementById("galleryThumbnails");

  const stockStatusEl =
    document.getElementById("stockStatus");

  const colorOptions =
    document.querySelectorAll(".color-option");

  const qtyInput =
    document.getElementById("qtyInput");

  const qtyMinus =
    document.getElementById("qtyMinus");

  const qtyPlus =
    document.getElementById("qtyPlus");

  const addToCartBtn =
    document.getElementById("addToCartBtn");

  const wishlistBtn =
    document.getElementById("wishlistBtn");


  /* =========================================================
     CSRF COOKIE
  ========================================================= */

  function getCookie(name) {

    const match = document.cookie.match(
      new RegExp("(^| )" + name + "=([^;]+)")
    );

    return match
      ? decodeURIComponent(match[2])
      : null;
  }


  /* =========================================================
     GALLERY
  ========================================================= */

  function renderGallery(imageUrls) {

    if (!galleryEl) {
      return;
    }

    galleryEl.innerHTML = "";

    imageUrls.forEach(function (url, index) {

      const img = document.createElement("img");

      img.className =
        "thumbnail" +
        (index === 0 ? " active" : "");

      img.src = url;

      img.dataset.full = url;

      galleryEl.appendChild(img);

    });
  }


  /* =========================================================
     PRIMARY IMAGE
  ========================================================= */

  function setPrimaryImage(url) {

    if (!primaryImageEl) {
      return;
    }

    if (url) {

      primaryImageEl.src = url;

      primaryImageEl.style.display = "";

      if (primaryImagePlaceholder) {
        primaryImagePlaceholder.style.display = "none";
      }

    } else {

      primaryImageEl.style.display = "none";

      if (primaryImagePlaceholder) {
        primaryImagePlaceholder.style.display = "";
      }

    }
  }


  /* =========================================================
     APPLY SELECTED VARIANT
  ========================================================= */

  function applyVariant(variantId) {

    const data = variants[variantId];

    if (!data) {
      return;
    }


    /* ---------------------------------------------------------
       STOCK
    --------------------------------------------------------- */

    const inStock = data.stock > 0;

    if (productPriceEl) {
    productPriceEl.textContent =
        `₹${data.price}`;
    }

    if (stockStatusEl) {

      stockStatusEl.textContent =
        inStock
          ? "In Stock"
          : "Out of Stock";

      stockStatusEl.classList.toggle(
        "in-stock",
        inStock
      );

      stockStatusEl.classList.toggle(
        "out-of-stock",
        !inStock
      );
    }


    /* ---------------------------------------------------------
       IMAGE
    --------------------------------------------------------- */

    setPrimaryImage(data.primary_image);

    renderGallery(
      data.gallery_images || []
    );


    /* ---------------------------------------------------------
       COLOR
    --------------------------------------------------------- */

    colorOptions.forEach(function (btn) {

      btn.classList.toggle(
        "active",
        btn.dataset.variantId === String(variantId)
      );

    });


    /* ---------------------------------------------------------
       QUANTITY
    --------------------------------------------------------- */

    if (qtyInput) {

      /*
       * If this variant is already in the cart, start the
       * stepper at whatever quantity is currently stored
       * there instead of whatever was left over from the
       * previously selected variant.
       */

      const startingQuantity =
        data.is_in_cart && data.quantity
          ? data.quantity
          : (parseInt(qtyInput.value, 10) || 1);

      qtyInput.max = data.stock;

      qtyInput.value = Math.min(
        startingQuantity,
        Math.max(data.stock, 1)
      );
    }


    /* ---------------------------------------------------------
       ADD TO CART BUTTON
    --------------------------------------------------------- */

    if (addToCartBtn) {

      addToCartBtn.dataset.variantId =
        variantId;

      addToCartBtn.dataset.url =
        data.cart_url ||
        `/cart/add/${variantId}/`;


      /*
       * Store whether this specific variant
       * is currently in the cart, and at what
       * quantity — so a later click can tell
       * whether the selected quantity has
       * actually changed.
       */

      if (data.is_in_cart) {

        addToCartBtn.dataset.inCart = "true";

        addToCartBtn.dataset.cartQuantity =
          data.quantity || 1;

        addToCartBtn.textContent =
          "Go to Cart 🛒";

        /*
         * If the element is an <a>,
         * update its href.
         */

        if (addToCartBtn.tagName === "A") {

          addToCartBtn.href = "/cart/";

        }

        /*
         * Button should remain clickable.
         */

        addToCartBtn.disabled = false;

      } else {

        addToCartBtn.dataset.inCart = "false";

        addToCartBtn.dataset.cartQuantity = "0";

        addToCartBtn.textContent =
          "Add to Cart 🛒";

        /*
         * If the element is an <a>,
         * point it to the add-to-cart URL.
         */

        if (addToCartBtn.tagName === "A") {

          addToCartBtn.href =
            addToCartBtn.dataset.url;

        }

        /*
         * Disable only if the variant is out of stock.
         */

        addToCartBtn.disabled =
          !inStock;

      }
    }


    /* ---------------------------------------------------------
       WISHLIST BUTTON
    --------------------------------------------------------- */

    if (wishlistBtn) {

      wishlistBtn.dataset.variantId =
        variantId;

      wishlistBtn.dataset.url =
        data.wishlist_url ||
        `/wishlist/add/${variantId}/`;


      if (data.is_wishlisted) {

        wishlistBtn.dataset.inWishlist =
          "true";

        wishlistBtn.textContent =
          "❤️ Wishlisted";

        if (wishlistBtn.tagName === "A") {

          wishlistBtn.href =
            "/wishlist/";

        }

      } else {

        wishlistBtn.dataset.inWishlist =
          "false";

        wishlistBtn.textContent =
          "🤍 Add to Wishlist";

        if (wishlistBtn.tagName === "A") {

          wishlistBtn.href =
            wishlistBtn.dataset.url;

        }
      }
    }

  }


  /* =========================================================
     COLOR / VARIANT SELECTION
  ========================================================= */

  colorOptions.forEach(function (btn) {

    btn.addEventListener(
      "click",
      function () {

        const variantId =
          btn.dataset.variantId;

        applyVariant(variantId);

      }
    );

  });


  /* =========================================================
     INITIAL VARIANT
  ========================================================= */

  const activeVariantId =
    document.querySelector(
      ".color-option.active"
    )?.dataset.variantId
    ||
    Object.keys(variants)[0];


  if (activeVariantId) {

    applyVariant(activeVariantId);

  }


  /* =========================================================
     QUANTITY STEPPER
  ========================================================= */

  function currentStock() {

    if (!qtyInput) {
      return 1;
    }

    return (
      parseInt(qtyInput.max, 10) || 1
    );
  }


  /* ---------------------------------------------------------
     DECREASE QUANTITY
  --------------------------------------------------------- */

  if (qtyMinus && qtyInput) {

    qtyMinus.addEventListener(
      "click",
      function () {

        const value =
          parseInt(qtyInput.value, 10) || 1;

        if (value > 1) {

          qtyInput.value =
            value - 1;

        }

      }
    );

  }


  /* ---------------------------------------------------------
     INCREASE QUANTITY
  --------------------------------------------------------- */

  if (qtyPlus && qtyInput) {

    qtyPlus.addEventListener(
      "click",
      function () {

        const value =
          parseInt(qtyInput.value, 10) || 1;

        if (value < currentStock()) {

          qtyInput.value =
            value + 1;

        }

      }
    );

  }


  /* ---------------------------------------------------------
     MANUAL QUANTITY INPUT
  --------------------------------------------------------- */

  if (qtyInput) {

    qtyInput.addEventListener(
      "change",
      function () {

        let value =
          parseInt(qtyInput.value, 10) || 1;

        const stock =
          currentStock();

        /*
         * Minimum quantity = 1
         */

        if (value < 1) {
          value = 1;
        }

        /*
         * Maximum quantity = stock
         */

        if (value > stock) {
          value = stock;
        }

        qtyInput.value = value;

      }
    );

  }


  /* =========================================================
     GALLERY THUMBNAIL CLICK
  ========================================================= */

  if (galleryEl) {

    galleryEl.addEventListener(
      "click",
      function (e) {

        if (
          !e.target.classList.contains(
            "thumbnail"
          )
        ) {
          return;
        }


        setPrimaryImage(
          e.target.dataset.full
        );


        galleryEl
          .querySelectorAll(".thumbnail")
          .forEach(function (thumbnail) {

            thumbnail.classList.remove(
              "active"
            );

          });


        e.target.classList.add(
          "active"
        );

      }
    );

  }


  /* =========================================================
     ADD TO CART
  ========================================================= */

  if (addToCartBtn) {

    addToCartBtn.addEventListener(
      "click",
      function (event) {

        event.preventDefault();


        /* -----------------------------------------------------
           GET VARIANT
        ----------------------------------------------------- */

        const variantId =
          addToCartBtn.dataset.variantId;


        if (!variantId) {

          alert(
            "Please select a product variant."
          );

          return;
        }


        /* -----------------------------------------------------
           GET QUANTITY
        ----------------------------------------------------- */

        const quantity =
          qtyInput
            ? parseInt(
                qtyInput.value,
                10
              )
            : 1;


        if (!quantity || quantity < 1) {

          alert(
            "Please select a valid quantity."
          );

          return;
        }


        /* -----------------------------------------------------
           ALREADY IN CART, SAME QUANTITY?

           Only skip the request and jump straight to the
           cart page if this variant is already in the cart
           AND the selected quantity hasn't changed. If the
           user bumped the quantity up (or down) using the
           stepper, that change still needs to be sent to
           the server.
        ----------------------------------------------------- */

        const currentCartQuantity =
          parseInt(
            addToCartBtn.dataset.cartQuantity,
            10
          ) || 0;

        if (
          addToCartBtn.dataset.inCart === "true" &&
          quantity === currentCartQuantity
        ) {

          window.location.href =
            "/cart/";

          return;
        }


        /* -----------------------------------------------------
           URL
        ----------------------------------------------------- */

        const url =
          addToCartBtn.dataset.url ||
          `/cart/add/${variantId}/`;


        /* -----------------------------------------------------
           FORM DATA
        ----------------------------------------------------- */

        const formData =
          new FormData();

        formData.append(
          "quantity",
          quantity
        );


        /* -----------------------------------------------------
           BUTTON LOADING STATE
        ----------------------------------------------------- */

        const originalText =
          addToCartBtn.textContent;

        addToCartBtn.disabled = true;

        addToCartBtn.textContent =
          "Adding...";


        /* -----------------------------------------------------
           SEND REQUEST
        ----------------------------------------------------- */

        fetch(url, {

          method: "POST",

          headers: {
            "X-CSRFToken":
              getCookie("csrftoken"),
          },

          body: formData,

        })

          .then(
            async function (response) {

              const data =
                await response.json();


              if (
                !response.ok ||
                !data.success
              ) {

                throw new Error(
                  data.message ||
                  "Unable to add item to cart."
                );

              }


              return data;

            }
          )


          /* ---------------------------------------------------
             SUCCESS
          --------------------------------------------------- */

          .then(
            function (data) {

              console.log(
                "Cart updated:",
                data
              );


              /*
               * This variant is now in the cart at the
               * quantity the server just confirmed.
               */

              addToCartBtn.dataset.inCart =
                "true";

              addToCartBtn.dataset.cartQuantity =
                data.quantity ?? quantity;


              /*
               * Change button.
               */

              addToCartBtn.textContent =
                "Go to Cart 🛒";


              /*
               * Re-enable button.
               */

              addToCartBtn.disabled =
                false;


              /*
               * If it is an anchor,
               * update href as well.
               */

              if (
                addToCartBtn.tagName ===
                "A"
              ) {

                addToCartBtn.href =
                  "/cart/";

              }


              /* -----------------------------------------------
                 UPDATE HEADER CART COUNT
              ------------------------------------------------ */

              const cartCountEl =
                document.getElementById(
                  "cartCount"
                );


              if (cartCountEl) {

                cartCountEl.textContent =
                  data.cart_count;

              }

            }
          )


          /* ---------------------------------------------------
             ERROR
          --------------------------------------------------- */

          .catch(
            function (error) {

              console.error(
                "Add to cart error:",
                error
              );


              alert(
                error.message
              );


              /*
               * Restore button.
               */

              addToCartBtn.disabled =
                false;

              addToCartBtn.textContent =
                originalText;

            }
          );

      }
    );

  }


  /* =========================================================
     WISHLIST
  ========================================================= */

  if (wishlistBtn) {

    wishlistBtn.addEventListener(
      "click",
      function (event) {

        event.preventDefault();


        /*
         * If already wishlisted,
         * go to wishlist page.
         */

        if (
          wishlistBtn.dataset.inWishlist ===
          "true"
        ) {

          window.location.href =
            "/wishlist/";

          return;
        }


        const variantId =
          wishlistBtn.dataset.variantId;


        if (!variantId) {

          alert(
            "Please select a product variant."
          );

          return;
        }


        const url =
          wishlistBtn.dataset.url ||
          `/wishlist/add/${variantId}/`;


        /*
         * Disable while processing.
         */

        wishlistBtn.disabled =
          true;


        const originalText =
          wishlistBtn.textContent;


        wishlistBtn.textContent =
          "Adding...";


        fetch(url, {

          method: "POST",

          headers: {

            "Content-Type":
              "application/json",

            "X-CSRFToken":
              getCookie("csrftoken"),

          },

          body: JSON.stringify({
            variant_id: variantId
          }),

        })


          .then(
            async function (response) {

              const data =
                await response.json();


              if (
                !response.ok ||
                data.success === false
              ) {

                throw new Error(
                  data.message ||
                  "Unable to update wishlist."
                );

              }


              return data;

            }
          )


          .then(
            function (data) {

              console.log(
                "Wishlist updated:",
                data
              );


              /*
               * Mark this variant
               * as wishlisted.
               */

              wishlistBtn.dataset.inWishlist =
                "true";


              /*
               * Update button.
               */

              wishlistBtn.textContent =
                "❤️ Wishlisted";


              wishlistBtn.disabled =
                false;


              /*
               * If anchor, update href.
               */

              if (
                wishlistBtn.tagName ===
                "A"
              ) {

                wishlistBtn.href =
                  "/wishlist/";

              }

            }
          )


          .catch(
            function (error) {

              console.error(
                "Wishlist error:",
                error
              );


              alert(
                error.message
              );


              wishlistBtn.disabled =
                false;


              wishlistBtn.textContent =
                originalText;

            }
          );

      }
    );

  }

});