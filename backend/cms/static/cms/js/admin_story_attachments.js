(function () {
    function trashIcon() {
        return [
            '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">',
            '<path d="M3 6h18"></path>',
            '<path d="M8 6V4h8v2"></path>',
            '<path d="M19 6l-1 14H6L5 6"></path>',
            '<path d="M10 11v5"></path>',
            '<path d="M14 11v5"></path>',
            '</svg>',
        ].join("");
    }

    function enhanceRow(row) {
        if (!row || row.dataset.attachmentDeleteEnhanced) {
            return;
        }

        const checkbox = row.querySelector('td.delete input[type="checkbox"][name$="-DELETE"]');
        if (!checkbox) {
            return;
        }

        const deleteCell = checkbox.closest("td.delete");
        if (!deleteCell) {
            return;
        }

        row.dataset.attachmentDeleteEnhanced = "true";
        checkbox.classList.add("cc-inline-delete-checkbox");

        const button = document.createElement("button");
        button.type = "button";
        button.className = "cc-inline-delete-button";
        button.title = "Премахни файла";
        button.setAttribute("aria-label", "Премахни файла");
        button.dataset.inlineDeleteEnhanced = "true";
        button.innerHTML = trashIcon();
        button.addEventListener("click", function () {
            checkbox.checked = true;
            row.classList.add("cc-inline-row-removed");
            row.setAttribute("aria-hidden", "true");
        });

        deleteCell.appendChild(button);
    }

    function enhanceStackedDeleteButton(button) {
        if (!button || button.dataset.inlineDeleteEnhanced) {
            return;
        }

        const row = button.closest(".inline-related");
        if (!row) {
            return;
        }

        const checkbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (!checkbox) {
            return;
        }

        button.dataset.inlineDeleteEnhanced = "true";
        checkbox.classList.add("cc-inline-delete-checkbox");
        button.addEventListener("click", function () {
            checkbox.checked = true;
            button.classList.add("cc-inline-delete-button--selected");
            row.classList.add("cc-inline-row-removed");
            row.setAttribute("aria-hidden", "true");
        });
    }

    function buildDeleteButton(onClick) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "cc-inline-delete-button";
        button.title = "Премахни файла";
        button.setAttribute("aria-label", "Премахни файла");
        button.innerHTML = trashIcon();
        button.addEventListener("click", onClick);
        return button;
    }

    function enhanceClearableFileInput(checkbox) {
        if (!checkbox || checkbox.dataset.clearButtonEnhanced) {
            return;
        }

        const label = document.querySelector('label[for="' + checkbox.id + '"]');
        if (!label) {
            return;
        }

        checkbox.dataset.clearButtonEnhanced = "true";
        checkbox.classList.add("cc-inline-delete-checkbox");
        label.classList.add("cc-clear-file-label");
        label.setAttribute("aria-hidden", "true");

        const button = buildDeleteButton(function () {
            checkbox.checked = true;
            button.classList.add("cc-inline-delete-button--selected");
        });
        label.after(button);
    }

    function enhanceClearableFileInputs(root) {
        const scope = root || document;
        scope.querySelectorAll('input[type="checkbox"][id="cover_image-clear_id"]').forEach(enhanceClearableFileInput);
    }

    function enhanceRows(root) {
        const scope = root || document;
        const tabularInlineSelector = [
            "tr.dynamic-attachments",
            "tr[id^='attachments-']",
            "tr.dynamic-schedule_entries",
            "tr[id^='schedule_entries-']",
            "tr.dynamic-pricing_options",
            "tr[id^='pricing_options-']",
            "tr.dynamic-gallery_items",
            "tr[id^='gallery_items-']",
        ].join(", ");

        if (scope.matches && scope.matches(tabularInlineSelector)) {
            enhanceRow(scope);
        }
        scope.querySelectorAll(tabularInlineSelector).forEach(enhanceRow);
        scope.querySelectorAll(".inline-related button.cc-inline-delete-button").forEach(enhanceStackedDeleteButton);
    }

    document.addEventListener("DOMContentLoaded", function () {
        enhanceRows(document);
        enhanceClearableFileInputs(document);
    });

    document.addEventListener("formset:added", function (event) {
        enhanceRows(event.target);
        enhanceClearableFileInputs(event.target);
    });
})();
