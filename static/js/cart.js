document.addEventListener("DOMContentLoaded", () => {

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

                // Update total items
                const summaryCount = document.getElementById("summary-count");
                if (summaryCount) {
                    summaryCount.textContent = data.cart_count;
                }

                // Update heading count
                const headingCount = document.getElementById("cart-count");
                if (headingCount) {
                    headingCount.textContent =
                        `(${data.cart_count} item${data.cart_count !== 1 ? "s" : ""})`;
                }

                // Update subtotal
                const subtotal = document.getElementById("cart-subtotal");
                if (subtotal) {
                    subtotal.textContent = "₹" + data.total;
                }

                // Update total
                const total = document.getElementById("cart-total");
                if (total) {
                    total.textContent = "₹" + data.total;
                }

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