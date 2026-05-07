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
        button.innerHTML = trashIcon();
        button.addEventListener("click", function () {
            checkbox.checked = true;
            row.classList.add("cc-inline-row-removed");
            row.setAttribute("aria-hidden", "true");
        });

        deleteCell.appendChild(button);
    }

    function enhanceRows(root) {
        const scope = root || document;
        if (scope.matches && scope.matches("tr.dynamic-attachments, tr[id^='attachments-']")) {
            enhanceRow(scope);
        }
        scope.querySelectorAll("tr.dynamic-attachments, tr[id^='attachments-']").forEach(enhanceRow);
    }

    document.addEventListener("DOMContentLoaded", function () {
        enhanceRows(document);
    });

    document.addEventListener("formset:added", function (event) {
        enhanceRows(event.target);
    });
})();
