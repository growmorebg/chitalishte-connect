(function () {
    document.documentElement.classList.remove("no-js");
    document.documentElement.classList.add("js");

    const navToggle = document.querySelector("[data-nav-toggle]");
    const navPanel = document.querySelector("[data-nav-panel]");
    const navGroups = Array.from(document.querySelectorAll("[data-nav-group]"));

    function shouldUseTapSubmenu() {
        return (
            window.matchMedia("(max-width: 760px)").matches ||
            window.matchMedia("(hover: none)").matches ||
            window.matchMedia("(pointer: coarse)").matches
        );
    }

    function setNavGroupState(group, isOpen) {
        group.classList.toggle("is-open", isOpen);
        const trigger = group.querySelector("[data-nav-trigger]");
        if (trigger) {
            trigger.setAttribute("aria-expanded", String(isOpen));
        }
    }

    function closeNavGroups(exceptGroup) {
        navGroups.forEach(function (group) {
            if (group !== exceptGroup) {
                setNavGroupState(group, false);
            }
        });
    }

    if (navToggle && navPanel) {
        navToggle.addEventListener("click", function () {
            const isOpen = navPanel.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", String(isOpen));
            if (!isOpen) {
                closeNavGroups();
            }
        });
    }

    if (navGroups.length) {
        navGroups.forEach(function (group) {
            const trigger = group.querySelector("[data-nav-trigger]");

            if (!trigger) {
                return;
            }

            trigger.addEventListener("click", function (event) {
                if (!shouldUseTapSubmenu()) {
                    return;
                }

                if (!group.classList.contains("is-open")) {
                    event.preventDefault();
                    closeNavGroups(group);
                    setNavGroupState(group, true);
                }
            });
        });

        document.addEventListener("click", function (event) {
            if (!navGroups.some(function (group) {
                return group.contains(event.target);
            })) {
                closeNavGroups();
            }
        });

        window.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeNavGroups();
                if (navPanel && navToggle) {
                    navPanel.classList.remove("is-open");
                    navToggle.setAttribute("aria-expanded", "false");
                }
            }
        });

        window.addEventListener("resize", function () {
            if (!shouldUseTapSubmenu()) {
                closeNavGroups();
                if (navPanel && navToggle) {
                    navPanel.classList.remove("is-open");
                    navToggle.setAttribute("aria-expanded", "false");
                }
            }
        });
    }

    const banner = document.querySelector("[data-cookie-banner]");
    const dialog = document.querySelector("[data-cookie-dialog]");
    const openButton = document.querySelector("[data-cookie-open]");

    if (openButton && dialog && typeof dialog.showModal === "function") {
        openButton.addEventListener("click", function (event) {
            event.preventDefault();
            dialog.showModal();
        });
    }

    if (dialog) {
        document.querySelectorAll("[data-cookie-close]").forEach(function (button) {
            button.addEventListener("click", function () {
                dialog.close();
            });
        });
    }

    const lightbox = document.querySelector("[data-lightbox]");
    const lightboxTarget = document.querySelector("[data-lightbox-target]");
    const lightboxCaption = document.querySelector("[data-lightbox-caption]");

    if (lightbox && lightboxTarget) {
        document.querySelectorAll("[data-lightbox-link]").forEach(function (link) {
            link.addEventListener("click", function (event) {
                event.preventDefault();
                const image = link.querySelector("[data-lightbox-image]");
                if (!image) {
                    return;
                }
                lightboxTarget.src = image.getAttribute("data-lightbox-src") || image.getAttribute("src") || "";
                lightboxTarget.alt = image.getAttribute("alt") || "";
                if (lightboxCaption) {
                    lightboxCaption.textContent = image.getAttribute("data-lightbox-caption") || "";
                }
                lightbox.hidden = false;
                document.body.style.overflow = "hidden";
            });
        });

        function closeLightbox() {
            lightbox.hidden = true;
            lightboxTarget.src = "";
            document.body.style.overflow = "";
        }

        document.querySelectorAll("[data-lightbox-close]").forEach(function (button) {
            button.addEventListener("click", closeLightbox);
        });

        window.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !lightbox.hidden) {
                closeLightbox();
            }
        });
    }
})();
