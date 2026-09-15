
    const settingsBtn = document.querySelector(".settings-btn");
    const settingsDropdown = document.querySelector(".settings-dropdown");

    const notificationContainer = document.querySelector(".notification-container");
    const notificationBtn = notificationContainer ? notificationContainer.querySelector(".icon-btn") : null;
    const notificationDropdown = document.querySelector(".notification-dropdown");

    // Toggle settings dropdown
    if (settingsBtn && settingsDropdown) {
        settingsBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            settingsDropdown.classList.toggle("show");
        });
    }

    // Toggle notification dropdown
    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            notificationDropdown.classList.toggle("show");
        });
    }

    // Close buttons: delegated handler to catch clicks reliably
    document.addEventListener('click', (e) => {
        try {
            // Ensure we have an Element (click on text nodes can make e.target a Text node)
            let el = e.target;
            while (el && el.nodeType !== 1) el = el.parentNode;
            if (!el) return;
            const btn = el.closest('.dropdown-close');
            if (!btn) return;
            e.stopPropagation();
            const dropdown = btn.closest('.settings-dropdown, .notification-dropdown');
            // Close the dropdown when a close button is clicked
            if (dropdown) {
                dropdown.classList.remove('show');
            }
        } catch (err) {
            // swallow unexpected errors to avoid breaking other handlers
            console.error('Dropdown close handler error', err);
        }
    });


    // Close when clicking outside any dropdown
    document.addEventListener("click", (e) => {
        document.querySelectorAll(".settings-dropdown, .notification-dropdown").forEach((dropdown) => {
            const trigger = dropdown.classList.contains("settings-dropdown") ? settingsBtn : notificationBtn;
            if (dropdown && !dropdown.contains(e.target) && !(trigger && trigger.contains(e.target))) {
                dropdown.classList.remove("show");
            }
        });
    });

    document.querySelectorAll(".settings-dropdown a, .notification-dropdown a").forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault(); // stop JS from swallowing the click
        const dropdown = link.closest(".settings-dropdown, .notification-dropdown");
        if (dropdown) dropdown.classList.remove("show");
        // force navigation
        window.location.href = link.href;
    });
});

    // Extra: ensure Account Settings link always navigates (defensive)
    const accountSettingsLink = document.getElementById('accountSettingsLink');
    if (accountSettingsLink) {
        accountSettingsLink.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            const href = accountSettingsLink.href || accountSettingsLink.getAttribute('href');
            const dropdown = accountSettingsLink.closest('.settings-dropdown');
            if (dropdown) dropdown.classList.remove('show');
            setTimeout(() => {
                if (href) window.location.href = href;
            }, 10);
        });
    }


    // Dark mode toggle: persist choice in localStorage
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        const enableDark = () => {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
        };

        const disableDark = () => {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
        };

        darkModeToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (document.body.classList.contains('dark-mode')) {
                disableDark();
            } else {
                enableDark();
            }
        });

        // Initialize based on saved preference
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
        }
    }
