(function () {
    "use strict";

    // =========================================================
    // DALAREICH ADMIN PRODUCT MANAGEMENT
    // =========================================================

    /**
     * Open the Add Product modal.
     */
    function openAddProductForm() {
        // Remove existing modal if one is already open
        const existingModal = document.getElementById("productModal");

        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement("div");

        modal.id = "productModal";
        modal.className = "modal-overlay";

        modal.innerHTML = `
            <div class="modal-content product-modal">
                <div class="modal-header">
                    <div>
                        <h2>Add New Product</h2>
                        <p>Enter the product information below.</p>
                    </div>

                    <button
                        type="button"
                        class="modal-close"
                        id="closeProductModal"
                        aria-label="Close"
                    >
                        &times;
                    </button>
                </div>

                <form id="productForm">

                    <div class="form-group">
                        <label for="productCode">
                            Product Code
                        </label>

                        <input
                            type="text"
                            id="productCode"
                            name="product_code"
                            placeholder="Enter product code"
                            autocomplete="off"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label for="productName">
                            Product Name
                        </label>

                        <input
                            type="text"
                            id="productName"
                            name="product_name"
                            placeholder="Enter product name"
                            autocomplete="off"
                            required
                        >
                    </div>

                    <div class="form-row">

                        <div class="form-group">
                            <label for="productCategory">
                                Category
                            </label>

                            <input
                                type="text"
                                id="productCategory"
                                name="category"
                                placeholder="e.g. Chocolate"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label for="productUnit">
                                Unit
                            </label>

                            <input
                                type="text"
                                id="productUnit"
                                name="unit"
                                placeholder="e.g. pcs, box, pack"
                                value="pcs"
                                required
                            >
                        </div>

                    </div>

                    <div class="form-row">

                        <div class="form-group">
                            <label for="productPrice">
                                Price
                            </label>

                            <input
                                type="number"
                                id="productPrice"
                                name="price"
                                placeholder="0.00"
                                min="0"
                                step="0.01"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label for="stockQuantity">
                                Stock Quantity
                            </label>

                            <input
                                type="number"
                                id="stockQuantity"
                                name="stock_quantity"
                                placeholder="0"
                                min="0"
                                step="1"
                                required
                            >
                        </div>

                    </div>

                    <div class="form-row">

                        <div class="form-group">
                            <label for="reorderLevel">
                                Reorder Level
                            </label>

                            <input
                                type="number"
                                id="reorderLevel"
                                name="reorder_level"
                                placeholder="0"
                                min="0"
                                step="1"
                                value="0"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label for="batchNumber">
                                Batch Number
                            </label>

                            <input
                                type="text"
                                id="batchNumber"
                                name="batch_number"
                                placeholder="Optional"
                                autocomplete="off"
                            >
                        </div>

                    </div>

                    <div class="form-group">
                        <label for="expirationDate">
                            Expiration Date
                        </label>

                        <input
                            type="date"
                            id="expirationDate"
                            name="expiration_date"
                        >
                    </div>

                    <div
                        id="productFormError"
                        class="form-error"
                        style="display: none;"
                    ></div>

                    <div class="modal-actions">

                        <button
                            type="button"
                            class="btn btn-secondary"
                            id="cancelProductBtn"
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            class="btn btn-primary"
                            id="saveProductBtn"
                        >
                            Save Product
                        </button>

                    </div>

                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // -----------------------------------------------------
        // CLOSE BUTTON
        // -----------------------------------------------------

        const closeButton = document.getElementById("closeProductModal");

        if (closeButton) {
            closeButton.addEventListener("click", closeProductForm);
        }

        // -----------------------------------------------------
        // CANCEL BUTTON
        // -----------------------------------------------------

        const cancelButton = document.getElementById("cancelProductBtn");

        if (cancelButton) {
            cancelButton.addEventListener("click", closeProductForm);
        }

        // -----------------------------------------------------
        // FORM SUBMIT
        // -----------------------------------------------------

        const productForm = document.getElementById("productForm");

        if (productForm) {
            productForm.addEventListener("submit", saveProduct);
        }

        // -----------------------------------------------------
        // CLICK OUTSIDE MODAL
        // -----------------------------------------------------

        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                closeProductForm();
            }
        });

        // -----------------------------------------------------
        // FOCUS PRODUCT CODE
        // -----------------------------------------------------

        const productCodeInput = document.getElementById("productCode");

        if (productCodeInput) {
            setTimeout(function () {
                productCodeInput.focus();
            }, 100);
        }
    }

    /**
     * Close the Add Product modal.
     */
    function closeProductForm() {
        const modal = document.getElementById("productModal");

        if (modal) {
            modal.remove();
        }
    }

    /**
     * Save a new product.
     */
    async function saveProduct(event) {
        event.preventDefault();

        const saveButton = document.getElementById("saveProductBtn");

        try {
            // -------------------------------------------------
            // GET FORM VALUES
            // -------------------------------------------------

            const productCodeInput =
                document.getElementById("productCode");

            const productNameInput =
                document.getElementById("productName");

            const categoryInput =
                document.getElementById("productCategory");

            const unitInput =
                document.getElementById("productUnit");

            const priceInput =
                document.getElementById("productPrice");

            const stockInput =
                document.getElementById("stockQuantity");

            const reorderInput =
                document.getElementById("reorderLevel");

            const batchInput =
                document.getElementById("batchNumber");

            const expirationInput =
                document.getElementById("expirationDate");

            const productCode =
                productCodeInput
                    ? productCodeInput.value.trim()
                    : "";

            const productName =
                productNameInput
                    ? productNameInput.value.trim()
                    : "";

            const category =
                categoryInput
                    ? categoryInput.value.trim()
                    : "";

            const unit =
                unitInput
                    ? unitInput.value.trim()
                    : "";

            const price =
                priceInput
                    ? Number(priceInput.value)
                    : 0;

            const stock =
                stockInput
                    ? Number(stockInput.value)
                    : 0;

            const reorderLevel =
                reorderInput
                    ? Number(reorderInput.value)
                    : 0;

            const batchNumber =
                batchInput
                    ? batchInput.value.trim()
                    : "";

            const expirationDate =
                expirationInput
                    ? expirationInput.value
                    : "";

            // -------------------------------------------------
            // VALIDATION
            // -------------------------------------------------

            if (!productCode) {
                throw new Error("Product code is required.");
            }

            if (!productName) {
                throw new Error("Product name is required.");
            }

            if (!category) {
                throw new Error("Category is required.");
            }

            if (!unit) {
                throw new Error("Unit is required.");
            }

            if (!Number.isFinite(price) || price < 0) {
                throw new Error(
                    "Please enter a valid product price."
                );
            }

            if (!Number.isFinite(stock) || stock < 0) {
                throw new Error(
                    "Please enter a valid stock quantity."
                );
            }

            if (
                !Number.isFinite(reorderLevel) ||
                reorderLevel < 0
            ) {
                throw new Error(
                    "Please enter a valid reorder level."
                );
            }

            // -------------------------------------------------
            // DISABLE SAVE BUTTON
            // -------------------------------------------------

            if (saveButton) {
                saveButton.disabled = true;
                saveButton.textContent = "Saving...";
            }

            // -------------------------------------------------
            // PRODUCT DATA
            // -------------------------------------------------

            const productData = {
                product_code: productCode,
                product_name: productName,
                category: category,
                price: price,
                stock_quantity: stock,
                reorder_level: reorderLevel,
                unit: unit,
                batch_number: batchNumber || null,
                expiration_date: expirationDate || null
            };

            // -------------------------------------------------
            // SEND TO FLASK API
            // -------------------------------------------------

            const response = await fetch("/api/products", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(productData)
            });

            // -------------------------------------------------
            // READ RESPONSE
            // -------------------------------------------------

            let result = {};

            try {
                result = await response.json();
            } catch (jsonError) {
                result = {};
            }

            if (!response.ok) {
                throw new Error(
                    result.error ||
                    result.message ||
                    "Failed to save product."
                );
            }

            // -------------------------------------------------
            // CLOSE MODAL
            // -------------------------------------------------

            closeProductForm();

            // -------------------------------------------------
            // SHOW SUCCESS MESSAGE
            // -------------------------------------------------

            const successMessage =
                result.message ||
                "Product added successfully.";

            if (
                typeof window.showToast === "function"
            ) {
                window.showToast(
                    successMessage,
                    "success"
                );
            } else {
                alert(successMessage);
            }

            // -------------------------------------------------
            // REFRESH PRODUCT LIST
            // -------------------------------------------------

            if (
                typeof window.renderProducts === "function"
            ) {
                await window.renderProducts();
            }

        } catch (error) {

            console.error(
                "Error saving product:",
                error
            );

            showProductError(
                error.message ||
                "Failed to save product."
            );

            // Re-enable save button
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.textContent = "Save Product";
            }
        }
    }

    /**
     * Display an error inside the product form.
     */
    function showProductError(message) {
        const errorBox =
            document.getElementById(
                "productFormError"
            );

        if (!errorBox) {
            alert(message);
            return;
        }

        errorBox.textContent = message;
        errorBox.style.display = "block";
    }

    // =========================================================
    // ADD PRODUCT BUTTON
    // =========================================================

    document.addEventListener("click", function (event) {
        const addButton =
            event.target.closest("#addProductBtn");

        if (!addButton) {
            return;
        }

        event.preventDefault();

        openAddProductForm();
    });

    // =========================================================
    // ESCAPE KEY
    // =========================================================

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") {
            return;
        }

        const modal =
            document.getElementById("productModal");

        if (modal) {
            closeProductForm();
        }
    });

    // =========================================================
    // EXPOSE PRODUCT FORM
    // =========================================================

    window.productForm = openAddProductForm;

})();