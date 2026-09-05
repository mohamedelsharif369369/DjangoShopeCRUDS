document.addEventListener("DOMContentLoaded", function () {
    const table = document.querySelector("#result_list");

    if (!table) {
        return;
    }

    const tbody = table.querySelector("tbody");

    if (!tbody) {
        return;
    }

    let draggedRow = null;

    function getCookie(name) {
        const cookies = document.cookie.split(";");

        for (const cookie of cookies) {
            const parts = cookie.trim().split("=");

            if (parts[0] === name) {
                return decodeURIComponent(parts.slice(1).join("="));
            }
        }

        return null;
    }

    function getCategoryId(row) {
        const link = row.querySelector(
            'th.field-name a[href*="/admin/products/category/"]'
        );

        if (!link) {
            return null;
        }

        const match = link.href.match(/\/category\/(\d+)\/change\/$/);

        return match ? match[1] : null;
    }

    async function saveOrder() {
        const categoryIds = Array.from(tbody.querySelectorAll("tr"))
            .map(getCategoryId)
            .filter(Boolean);

        const response = await fetch(
            "/admin/save-category-order/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    category_ids: categoryIds,
                }),
            }
        );

        if (!response.ok) {
            throw new Error("Failed to save category order.");
        }

        return response.json();
    }

    tbody.querySelectorAll("tr").forEach(function (row) {
        const firstCell = row.querySelector("th");

        if (!firstCell) {
            return;
        }

        const handle = document.createElement("span");

        handle.textContent = "☰";
        handle.title = "Drag to reorder";
        handle.className = "category-drag-handle";
        handle.draggable = true;

        firstCell.prepend(handle);

        handle.addEventListener("dragstart", function (event) {
            draggedRow = row;
            row.classList.add("category-dragging");

            event.dataTransfer.effectAllowed = "move";
        });

        handle.addEventListener("dragend", async function () {
            row.classList.remove("category-dragging");

            if (!draggedRow) {
                return;
            }

            draggedRow = null;

            try {
                await saveOrder();
                window.location.reload();
            } catch (error) {
                alert("Could not save category order.");
            }
        });

        row.addEventListener("dragover", function (event) {
            event.preventDefault();

            if (!draggedRow || draggedRow === row) {
                return;
            }

            const rect = row.getBoundingClientRect();
            const middle = rect.top + rect.height / 2;

            if (event.clientY < middle) {
                tbody.insertBefore(draggedRow, row);
            } else {
                tbody.insertBefore(draggedRow, row.nextSibling);
            }
        });
    });
});
