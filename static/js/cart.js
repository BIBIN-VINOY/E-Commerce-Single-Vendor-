document.addEventListener("DOMContentLoaded", () => {

    /* ---------- Helpers ---------- */

    const getCsrfToken = () => {
        const input = document.querySelector("[name=csrfmiddlewaretoken]");
        return input ? input.value : "";
    };

    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    };

    const formatMoney = (value) => "₹" + Number(value).toFixed(2);

    const updateSummary = (data) => {
        setText("summary-count", data.cart_count);
        setText(
            "cart-count",
            `(${data.cart_count} item${data.cart_count !== 1 ? "s" : ""})`
        );
        setText("cart-subtotal", formatMoney(data.total));
        setText("cart-total", formatMoney(data.total));
    };


    /* ---------- Increase / decrease quantity ---------- */

    document.querySelectorAll(".qty-btn").forEach(btn => {

        btn.addEventListener("click", () => {

            const card = btn.closest(".cart-card");

            // Prevent double-clicks while the request is running
            btn.disabled = true;

            fetch(btn.dataset.url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {

                if (!data.success) {
                    alert(data.error || "Could not update quantity.");
                    return;
                }

                // Decreasing from quantity 1 removes the item
                if (data.deleted) {
                    card.remove();

                    if (data.cart_count === 0) {
                        window.location.reload();   // show empty state
                        return;
                    }
                } else {
                    card.querySelector(".item-quantity").textContent =
                        data.quantity;
                    card.querySelector(".item-subtotal span").textContent =
                        Number(data.item_subtotal).toFixed(2);
                }

                updateSummary(data);

            })
            .catch(error => {
                console.error(error);
                alert("Something went wrong while updating the quantity.");
            })
            .finally(() => {
                btn.disabled = false;
            });

        });

    });


    /* ---------- Remove item ---------- */

    document.querySelectorAll(".remove-form").forEach(form => {

        form.addEventListener("submit", function (e) {

            e.preventDefault();

            if (!confirm("Remove this item from your cart?")) {
                return;
            }

            fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken":
                        form.querySelector("[name=csrfmiddlewaretoken]").value,
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {

                if (!data.success) return;

                // Remove the card
                form.closest(".cart-card").remove();

                // Update counts and totals
                updateSummary(data);

                // If the cart becomes empty, reload to show the empty state
                if (data.cart_count === 0) {
                    window.location.reload();
                }

            })
            .catch(error => {
                console.error(error);
                alert("Something went wrong while removing the item.");
            });

        });

    });

});