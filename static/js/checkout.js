document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("checkoutForm");
    const errorBox = document.getElementById("checkoutError");

    if (!form) {
        return;
    }


    function showError(message) {

        errorBox.textContent = message;
        errorBox.style.display = "block";

        errorBox.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }


    function clearError() {

        errorBox.textContent = "";
        errorBox.style.display = "none";
    }


    /*
    --------------------------------------------------
    ADDRESS SELECTION
    --------------------------------------------------
    */

    const addressCards = document.querySelectorAll(
        ".address-card"
    );

    addressCards.forEach(card => {

        card.addEventListener("click", () => {

            clearError();

            addressCards.forEach(otherCard => {
                otherCard.classList.remove("selected");
            });

            card.classList.add("selected");
        });

    });


    /*
    --------------------------------------------------
    PAYMENT SELECTION
    --------------------------------------------------
    */

    const paymentOptions = document.querySelectorAll(
        ".payment-option"
    );

    paymentOptions.forEach(option => {

        option.addEventListener("click", () => {

            clearError();

            paymentOptions.forEach(otherOption => {
                otherOption.classList.remove("selected");
            });

            option.classList.add("selected");
        });

    });


    /*
    --------------------------------------------------
    FORM VALIDATION
    --------------------------------------------------
    */

    form.addEventListener("submit", (event) => {

        clearError();

        const selectedAddress = document.querySelector(
            'input[name="address_id"]:checked'
        );

        const selectedPayment = document.querySelector(
            'input[name="payment_method"]:checked'
        );


        if (!selectedAddress) {

            event.preventDefault();

            showError(
                "Please select a delivery address."
            );

            return;
        }


        if (!selectedPayment) {

            event.preventDefault();

            showError(
                "Please select a payment method."
            );

            return;
        }


        /*
        Card / UPI are not connected to a payment
        gateway yet.

        We allow the request to reach the backend,
        where payment_status remains "pending".
        */

        const submitButtons = document.querySelectorAll(
            "#placeOrderBtn, .place-order-mobile"
        );

        submitButtons.forEach(button => {

            button.disabled = true;
            button.textContent = "Processing...";

        });

    });

});