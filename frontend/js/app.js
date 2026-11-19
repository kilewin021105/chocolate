/* =========================================================
   DALAREICH INTEGRATED POS & INVENTORY MANAGEMENT SYSTEM
   Frontend JavaScript
   ========================================================= */

"use strict";

/* =========================================================
   GLOBAL HELPERS
   ========================================================= */

const $ = (selector) => document.querySelector(selector);

const $$ = (selector) => [
    ...document.querySelectorAll(selector)
];


/* =========================================================
   GLOBAL STATE
   ========================================================= */

let currentUser = null;

let products = [];
let customers = [];
let suppliers = [];
let cart = [];


/* =========================================================
   API HELPER
   ========================================================= */

async function api(url, options = {}) {

    const response = await fetch(url, {
        ...options,

        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            ...(options.headers || {})
        }
    });

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {

        throw new Error(
            data.error ||
            data.message ||
            `Request failed (${response.status})`
        );
    }

    return data;
}


/* =========================================================
   FORMATTERS
   ========================================================= */

function money(value) {

    return "₱" +
        Number(value || 0).toLocaleString(
            "en-PH",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        );
}


function escapeHtml(value) {

    return String(value ?? "").replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[character])
    );
}


/* =========================================================
   ROLE HELPERS
   ========================================================= */

/*
 * IMPORTANT:
 *
 * This function makes sure the role sent to Flask is the
 * role that the user actually selected.
 *
 * It supports:
 *
 * #role
 * #roleSelect
 * select[name="role"]
 * input[name="role"]:checked
 *
 * It also checks the visible text of the selected option.
 */

function getSelectedRole() {

    let roleElement =
        $("#role") ||
        $("#roleSelect") ||
        document.querySelector(
            'select[name="role"]'
        );

    let selectedRole = "";

    if (roleElement) {

        /*
         * First get the actual value.
         */
        selectedRole =
            String(
                roleElement.value || ""
            ).trim();

        /*
         * If the value is something unexpected,
         * check the visible option text.
         */
        if (
            roleElement.tagName === "SELECT"
        ) {

            const selectedOption =
                roleElement.options[
                    roleElement.selectedIndex
                ];

            if (selectedOption) {

                const optionText =
                    String(
                        selectedOption.textContent || ""
                    ).trim();

                /*
                 * If the option text says Admin,
                 * use Admin even if its HTML value is
                 * accidentally different.
                 */
                if (
                    optionText.toLowerCase() ===
                    "admin"
                ) {

                    selectedRole = "Admin";

                } else if (
                    optionText.toLowerCase() ===
                    "user"
                ) {

                    selectedRole = "User";
                }
            }
        }
    }


    /*
     * Check radio buttons if no select was found.
     */
    if (!selectedRole) {

        const selectedRadio =
            document.querySelector(
                'input[name="role"]:checked'
            );

        if (selectedRadio) {

            selectedRole =
                String(
                    selectedRadio.value || ""
                ).trim();

            /*
             * Also check label/text when necessary.
             */
            if (
                selectedRole.toLowerCase() !== "admin" &&
                selectedRole.toLowerCase() !== "user"
            ) {

                const label =
                    document.querySelector(
                        `label[for="${selectedRadio.id}"]`
                    );

                const labelText =
                    String(
                        label?.textContent || ""
                    ).trim();

                if (
                    labelText.toLowerCase()
                        .includes("admin")
                ) {

                    selectedRole = "Admin";

                } else if (
                    labelText.toLowerCase()
                        .includes("user")
                ) {

                    selectedRole = "User";
                }
            }
        }
    }


    /*
     * Normalize the role.
     */
    const normalized =
        selectedRole
            .trim()
            .toLowerCase();


    if (
        normalized === "admin" ||
        normalized === "administrator"
    ) {

        return "Admin";
    }


    if (
        normalized === "user" ||
        normalized === "customer"
    ) {

        return "User";
    }


    return "";
}


/* =========================================================
   NORMALIZE BACKEND ROLE
   ========================================================= */

function normalizeRole(role) {

    const normalized =
        String(role || "")
            .trim()
            .toLowerCase();

    if (
        normalized === "admin" ||
        normalized === "administrator"
    ) {
        return "Admin";
    }

    if (
        normalized === "user" ||
        normalized === "customer"
    ) {
        return "User";
    }

    return "";
}


/* =========================================================
   VIEW HELPERS
   ========================================================= */

function showLoginView() {

    const loginView = $("#loginView");
    const signupView = $("#signupView");
    const appView = $("#appView");

    if (loginView) {
        loginView.classList.remove("hidden");
    }

    if (signupView) {
        signupView.classList.add("hidden");
    }

    if (appView) {
        appView.classList.add("hidden");
    }


    /* Clear signup messages */

    if ($("#signupError")) {

        $("#signupError").textContent = "";
        $("#signupError").style.color = "";
    }


    if ($("#signupSuccess")) {

        $("#signupSuccess").textContent = "";
    }


    /* Clear login error */

    if ($("#loginError")) {

        $("#loginError").textContent = "";
        $("#loginError").style.color = "";
    }
}


function showSignupView() {

    const loginView = $("#loginView");
    const signupView = $("#signupView");
    const appView = $("#appView");

    if (loginView) {
        loginView.classList.add("hidden");
    }

    if (signupView) {
        signupView.classList.remove("hidden");
    }

    if (appView) {
        appView.classList.add("hidden");
    }


    /* Clear old messages */

    if ($("#signupError")) {

        $("#signupError").textContent = "";
        $("#signupError").style.color = "";
    }


    if ($("#signupSuccess")) {

        $("#signupSuccess").textContent = "";
    }


    /* Focus name field */

    setTimeout(() => {

        $("#fullName")?.focus();

    }, 100);
}


/* =========================================================
   LOGIN
   ========================================================= */

async function handleLogin(event) {

    event.preventDefault();

    const loginError =
        $("#loginError");

    const loginButton =
        $("#signInButton");


    if (loginError) {

        loginError.textContent = "";
        loginError.style.color = "";
    }


    /*
     * EMAIL
     */

    const emailInput =
        $("#username");

    const passwordInput =
        $("#password");


    const email =
        emailInput?.value
            .trim()
            .toLowerCase() || "";


    /*
     * NEVER trim passwords.
     */

    const password =
        passwordInput?.value || "";


    /* =====================================================
       VALIDATION
       ===================================================== */

    if (!email) {

        if (loginError) {

            loginError.textContent =
                "Please enter your email.";
        }

        emailInput?.focus();

        return;
    }


    if (!password) {

        if (loginError) {

            loginError.textContent =
                "Please enter your password.";
        }

        passwordInput?.focus();

        return;
    }


    if (
        emailInput &&
        emailInput.type === "email" &&
        !emailInput.checkValidity()
    ) {

        if (loginError) {

            loginError.textContent =
                "Please enter a valid email address.";
        }

        emailInput.focus();

        return;
    }


    /* =====================================================
       GET SELECTED ROLE
       ===================================================== */

    const selectedRole =
        getSelectedRole();


    /*
     * DO NOT silently change an unknown role to User.
     *
     * This was part of the problem.
     */

    if (!selectedRole) {

        if (loginError) {

            loginError.textContent =
                "Please select a valid role: Admin or User.";

            loginError.style.color =
                "red";
        }

        return;
    }


    /* =====================================================
       DISABLE LOGIN BUTTON
       ===================================================== */

    if (loginButton) {

        loginButton.disabled = true;

        loginButton.textContent =
            "Signing In...";
    }


    /* =====================================================
       LOGIN REQUEST
       ===================================================== */

    try {

        /*
         * IMPORTANT:
         *
         * The selected role is now sent exactly as:
         *
         * Admin
         *
         * or
         *
         * User
         */

        const loginData = {

            email: email,

            username: email,

            password: password,

            role: selectedRole
        };


        console.log(
            "LOGIN REQUEST:",
            {
                email: email,
                requestedRole: selectedRole
            }
        );


        const data =
            await api(
                "/api/auth/login",
                {
                    method: "POST",

                    body:
                        JSON.stringify(
                            loginData
                        )
                }
            );

/* =====================================================
   CREATE SUPABASE AUTH SESSION
   ===================================================== */

if (
    data &&
    data.session &&
    data.session.access_token &&
    data.session.refresh_token
) {

    const {
        error: sessionError
    } =
        await supabaseClient.auth.setSession({

            access_token:
                data.session.access_token,

            refresh_token:
                data.session.refresh_token

        });


    if (sessionError) {

        console.error(
            "Supabase session error:",
            sessionError
        );

        throw sessionError;
    }


    console.log(
        "Supabase Auth session established."
    );

}

        console.log(
            "LOGIN RESPONSE:",
            data
        );


        /* =================================================
           GET USER FROM BACKEND
           ================================================= */

        currentUser =
            data.user || data;


        if (!currentUser) {

            throw new Error(
                "Login succeeded but no user information was returned."
            );
        }


        /* =================================================
           GET ACTUAL BACKEND ROLE
           ================================================= */

        /*
         * The backend/Supabase role is the source of truth.
         *
         * We do NOT use email to determine Admin anymore.
         */

        const backendRole =
            normalizeRole(
                currentUser.role ||
                currentUser.user_metadata?.role ||
                currentUser.raw_user_meta_data?.role ||
                data.role
            );


        console.log(
            "REQUESTED ROLE:",
            selectedRole
        );


        console.log(
            "BACKEND ROLE:",
            backendRole
        );


        /*
         * If the backend did not return a valid role,
         * do not allow access.
         */

        if (!backendRole) {

            throw new Error(
                "Your account does not have a valid authorized role."
            );
        }


        /* =================================================
           ROLE MATCH CHECK
           ================================================= */

        /*
         * The selected role MUST match the actual
         * Supabase/backend role.
         */

        if (
            selectedRole !==
            backendRole
        ) {

            throw new Error(
                `This account is registered as ${backendRole}. Please select ${backendRole}.`
            );
        }


        /* =================================================
           SAVE USER SESSION
           ================================================= */

        currentUser.role =
            backendRole;

        currentUser.email =
            String(
                currentUser.email ||
                email
            )
                .trim()
                .toLowerCase();


        /*
         * Save only AFTER successful login.
         *
         * Nothing is saved on page load.
         */

        try {

            localStorage.setItem(
                "dalareichUser",
                JSON.stringify(
                    currentUser
                )
            );

        } catch (storageError) {

            console.warn(
                "Could not save login session:",
                storageError
            );
        }


        /* =================================================
           LOGIN SUCCESS
           ================================================= */

        console.log(
            "Login successful."
        );

        console.log(
            "Logged in email:",
            currentUser.email
        );

        console.log(
            "Final role:",
            backendRole
        );


        /* =================================================
           ROLE-BASED REDIRECTION
           ================================================= */

        if (
            backendRole ===
            "Admin"
        ) {

            window.location.href =
                "./AdminDashboard.html";

            return;
        }


        if (
            backendRole ===
            "User"
        ) {

            window.location.href =
                "./UserDashboard.html";

            return;
        }


        /*
         * Safety fallback.
         */

        throw new Error(
            "Unauthorized role."
        );


    } catch (error) {

        console.error(
            "Login failed:",
            error
        );


        if (loginError) {

            loginError.textContent =
                error.message ||
                "Login failed. Please try again.";

            loginError.style.color =
                "red";
        }

    } finally {

        if (loginButton) {

            loginButton.disabled =
                false;

            loginButton.textContent =
                "Sign In";
        }
    }
}


/* =========================================================
   SIGN UP BUTTON
   ========================================================= */

function setupSignUpButton() {

    const signUpButton =
        $("#signUpButton");

    if (signUpButton) {

        signUpButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSignupView();
            }
        );
    }
}


/* =========================================================
   BACK TO LOGIN
   ========================================================= */

function setupBackToLoginButton() {

    const backToLoginButton =
        $("#backToLoginButton");

    if (backToLoginButton) {

        backToLoginButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showLoginView();
            }
        );
    }
}


/* =========================================================
   SIGNUP FORM
   ========================================================= */

async function handleSignUp(event) {

    event.preventDefault();


    const fullNameInput =
        $("#fullName");

    const emailInput =
        $("#signupEmail");

    const passwordInput =
        $("#signupPassword");

    const confirmPasswordInput =
        $("#confirmPassword");

    const errorElement =
        $("#signupError");

    const successElement =
        $("#signupSuccess");

    const createAccountButton =
        $("#createAccountButton");


    /* =====================================================
       CLEAR MESSAGES
       ===================================================== */

    if (errorElement) {

        errorElement.textContent = "";
        errorElement.style.color = "";
    }


    if (successElement) {

        successElement.textContent = "";
    }


    /* =====================================================
       GET VALUES
       ===================================================== */

    const fullName =
        fullNameInput?.value.trim() ||
        "";


    const email =
        emailInput?.value
            .trim()
            .toLowerCase() ||
        "";


    /*
     * Passwords are NEVER trimmed.
     */

    const password =
        passwordInput?.value ||
        "";


    const confirmPassword =
        confirmPasswordInput?.value ||
        "";


    console.log(
        "Signup validation:",
        {
            fullName: fullName,
            email: email,
            passwordLength:
                password.length,
            confirmPasswordLength:
                confirmPassword.length,
            passwordsMatch:
                password ===
                confirmPassword
        }
    );


    /* =====================================================
       FULL NAME
       ===================================================== */

    if (!fullName) {

        if (errorElement) {

            errorElement.textContent =
                "Please enter your full name.";
        }

        fullNameInput?.focus();

        return;
    }


    /* =====================================================
       EMAIL
       ===================================================== */

    if (!email) {

        if (errorElement) {

            errorElement.textContent =
                "Please enter your email address.";
        }

        emailInput?.focus();

        return;
    }


    if (
        emailInput &&
        !emailInput.checkValidity()
    ) {

        if (errorElement) {

            errorElement.textContent =
                "Please enter a valid email address.";
        }

        emailInput.focus();

        return;
    }


    /* =====================================================
       PASSWORD
       ===================================================== */

    if (!password) {

        if (errorElement) {

            errorElement.textContent =
                "Please enter a password.";
        }

        passwordInput?.focus();

        return;
    }


    if (password.length < 6) {

        if (errorElement) {

            errorElement.textContent =
                "Password must be at least 6 characters.";
        }

        passwordInput?.focus();

        return;
    }


    /* =====================================================
       CONFIRM PASSWORD
       ===================================================== */

    if (!confirmPassword) {

        if (errorElement) {

            errorElement.textContent =
                "Please confirm your password.";
        }

        confirmPasswordInput?.focus();

        return;
    }


    if (
        password !==
        confirmPassword
    ) {

        if (errorElement) {

            errorElement.textContent =
                "Passwords do not match.";
        }

        confirmPasswordInput?.focus();

        return;
    }


    /* =====================================================
       DISABLE BUTTON
       ===================================================== */

    if (createAccountButton) {

        createAccountButton.disabled =
            true;

        createAccountButton.textContent =
            "Creating Account...";
    }


    try {

        /* =================================================
           SEND TO FLASK
           ================================================= */

        const data =
            await api(
                "/api/auth/signup",
                {
                    method: "POST",

                    body:
                        JSON.stringify({

                            full_name:
                                fullName,

                            email:
                                email,

                            password:
                                password,

                            confirm_password:
                                confirmPassword
                        })
                }
            );


        console.log(
            "Signup successful:",
            data
        );


        /* =================================================
           SUCCESS MESSAGE
           ================================================= */

        if (errorElement) {

            errorElement.textContent = "";
        }


        if (successElement) {

            successElement.textContent =
                data.message ||
                "Account created successfully.";
        }


        /* =================================================
           PUT EMAIL INTO LOGIN FORM
           ================================================= */

        if ($("#username")) {

            $("#username").value =
                email;
        }


        /* =================================================
           CLEAR PASSWORDS
           ================================================= */

        if (passwordInput) {

            passwordInput.value =
                "";
        }


        if (confirmPasswordInput) {

            confirmPasswordInput.value =
                "";
        }


        /* =================================================
           RETURN TO LOGIN
           ================================================= */

        setTimeout(
            function () {

                if (signupForm) {

                    signupForm.reset();
                }


                showLoginView();


                if ($("#username")) {

                    $("#username").value =
                        email;
                }


                if ($("#loginError")) {

                    $("#loginError").style.color =
                        "#d8ffd8";

                    $("#loginError").textContent =
                        data.message ||
                        "Account created successfully. Please sign in.";
                }

            },
            1500
        );


    } catch (error) {

        console.error(
            "Signup error:",
            error
        );


        if (successElement) {

            successElement.textContent =
                "";
        }


        if (errorElement) {

            errorElement.style.color =
                "#ffd0d0";

            errorElement.textContent =
                error.message ||
                "Unable to create account.";
        }


    } finally {

        if (createAccountButton) {

            createAccountButton.disabled =
                false;

            createAccountButton.textContent =
                "Create Account";
        }
    }
}


/* =========================================================
   PASSWORD TOGGLE
   ========================================================= */

function setupPasswordToggle(
    inputId,
    buttonId
) {

    const input =
        document.getElementById(
            inputId
        );

    const button =
        document.getElementById(
            buttonId
        );


    if (!input || !button) {

        return;
    }


    button.addEventListener(
        "click",
        function (event) {

            event.preventDefault();


            if (
                input.type ===
                "password"
            ) {

                input.type =
                    "text";

                button.textContent =
                    "";

                button.setAttribute(
                    "aria-label",
                    "Hide password"
                );

                button.setAttribute(
                    "title",
                    "Hide password"
                );

            } else {

                input.type =
                    "password";

                button.textContent =
                    "";

                button.setAttribute(
                    "aria-label",
                    "Show password"
                );

                button.setAttribute(
                    "title",
                    "Show password"
                );
            }
        }
    );
}


/* =========================================================
   LOGOUT
   ========================================================= */

async function handleLogout() {

    try {

        await fetch(
            "/api/auth/logout",
            {
                method: "POST"
            }
        ).catch(
            () => {}
        );

    } catch (error) {

        console.warn(
            "Logout request failed:",
            error
        );
    }


    /*
     * Clear frontend session.
     */

    currentUser =
        null;

    products =
        [];

    customers =
        [];

    suppliers =
        [];

    cart =
        [];


    /*
     * IMPORTANT:
     *
     * Remove stored login information.
     */

    try {

        localStorage.removeItem(
            "dalareichUser"
        );

    } catch (error) {

        console.warn(
            "Unable to clear localStorage:",
            error
        );
    }


    /*
     * Hide application.
     */

    if ($("#appView")) {

        $("#appView")
            .classList
            .add("hidden");
    }


    /*
     * Show login.
     */

    showLoginView();


    /*
     * Clear login fields.
     */

    if ($("#username")) {

        $("#username").value =
            "";
    }


    if ($("#password")) {

        $("#password").value =
            "";
    }


    /*
     * Reset password visibility.
     */

    if ($("#password")) {

        $("#password").type =
            "password";
    }


    if ($("#togglePassword")) {

        $("#togglePassword").textContent =
            "";
    }


    /*
     * Reset login button.
     */

    if ($("#signInButton")) {

        $("#signInButton").disabled =
            false;

        $("#signInButton").textContent =
            "Sign In";
    }


    /*
     * Return to dashboard page internally.
     */

    showPage(
        "dashboard"
    );
}


/* =========================================================
   NAVIGATION
   ========================================================= */

function setupNavigation() {

    $$(".nav").forEach(
        button => {

            button.addEventListener(
                "click",
                function () {

                    const page =
                        button.dataset.page;

                    showPage(page);
                }
            );
        }
    );
}


/* =========================================================
   LOAD ALL DATA
   ========================================================= */

async function loadAll() {

    try {

        const results =
            await Promise.all([

                api(
                    "/api/products"
                ),

                api(
                    "/api/customers"
                ),

                api(
                    "/api/suppliers"
                )
            ]);


        products =
            Array.isArray(
                results[0]
            )
                ? results[0]
                : [];


        customers =
            Array.isArray(
                results[1]
            )
                ? results[1]
                : [];


        suppliers =
            Array.isArray(
                results[2]
            )
                ? results[2]
                : [];


        /* =================================================
           DATABASE STATUS
           ================================================= */

        try {

            const health =
                await api(
                    "/api/health"
                );


            if ($("#dbStatus")) {

                $("#dbStatus").textContent =
                    health.database ===
                    "supabase"

                        ? "● Supabase Connected"

                        : "● Demo Mode";
            }

        } catch (error) {

            console.warn(
                "Health check failed:",
                error
            );


            if ($("#dbStatus")) {

                $("#dbStatus").textContent =
                    "● Connection Error";
            }
        }


        /* =================================================
           RENDER
           ================================================= */

        renderDashboard();

        renderPOS();

        renderProducts();

        renderCustomers();

        renderSuppliers();

        renderReports();


    } catch (error) {

        console.error(
            "Failed to load application data:",
            error
        );


        if ($("#dbStatus")) {

            $("#dbStatus").textContent =
                "● Connection Error";
        }


        throw error;
    }
}


/* =========================================================
   PAGE NAVIGATION
   ========================================================= */

function showPage(name) {

    /*
     * Hide all pages.
     */

    $$(".page").forEach(
        page => {

            page.classList.add(
                "hidden"
            );
        }
    );


    /*
     * Show selected page.
     */

    const selectedPage =
        $(`#page-${name}`);


    if (selectedPage) {

        selectedPage.classList.remove(
            "hidden"
        );
    }


    /*
     * Page titles.
     */

    const titles = {

        dashboard:
            "Dashboard",

        pos:
            "Point of Sale",

        products:
            "Inventory",

        customers:
            "Customers",

        suppliers:
            "Suppliers",

        reports:
            "Reports"
    };


    if ($("#pageTitle")) {

        $("#pageTitle").textContent =
            titles[name] ||
            "Dashboard";
    }


    /*
     * Active navigation.
     */

    $$(".nav").forEach(
        button => {

            button.classList.toggle(
                "active",
                button.dataset.page ===
                    name
            );
        }
    );
}


/* =========================================================
   DASHBOARD
   ========================================================= */

async function renderDashboard() {

    const page =
        $("#page-dashboard");


    if (!page) {

        return;
    }


    try {

        const dashboard =
            await api(
                "/api/dashboard"
            );


        page.innerHTML = `

            <div class="grid">

                <div class="card">

                    <div class="muted">
                        Total Products
                    </div>

                    <div class="metric">
                        ${dashboard.total_products ?? 0}
                    </div>

                </div>


                <div class="card">

                    <div class="muted">
                        Customers
                    </div>

                    <div class="metric">
                        ${dashboard.total_customers ?? 0}
                    </div>

                </div>


                <div class="card">

                    <div class="muted">
                        Recorded Sales
                    </div>

                    <div class="metric">
                        ${money(
                            dashboard.total_sales
                        )}
                    </div>

                </div>


                <div class="card">

                    <div class="muted">
                        Low Stock Items
                    </div>

                    <div class="metric ${
                        dashboard.low_stock_count
                            ? "low"
                            : ""
                    }">

                        ${
                            dashboard.low_stock_count ??
                            0
                        }

                    </div>

                </div>

            </div>


            <div class="section-title">

                <h3>
                    Low Stock Alerts
                </h3>

                <span class="muted">
                    Stock ≤ reorder level
                </span>

            </div>


            <div class="table-wrap">

                <table class="table">

                    <thead>

                        <tr>

                            <th>Code</th>

                            <th>Product</th>

                            <th>Stock</th>

                            <th>Reorder</th>

                            <th>Status</th>

                        </tr>

                    </thead>


                    <tbody>

                        ${
                            dashboard.low_stock_items
                                ?.map(
                                    product => `

                                        <tr>

                                            <td>
                                                ${escapeHtml(
                                                    product.product_code
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHtml(
                                                    product.product_name
                                                )}
                                            </td>

                                            <td>
                                                ${
                                                    product.stock_quantity
                                                }
                                            </td>

                                            <td>
                                                ${
                                                    product.reorder_level
                                                }
                                            </td>

                                            <td class="low">
                                                LOW STOCK
                                            </td>

                                        </tr>

                                    `
                                )
                                .join("")
                            ||

                            `

                                <tr>

                                    <td colspan="5">
                                        No low stock items.
                                    </td>

                                </tr>

                            `
                        }

                    </tbody>

                </table>

            </div>
        `;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );
    }
}


/* =========================================================
   POINT OF SALE
   ========================================================= */

function renderPOS() {

    const page =
        $("#page-pos");


    if (!page) {

        return;
    }


    page.innerHTML = `

        <div class="pos-grid">

            <div class="card">

                <div class="toolbar">

                    <input
                        id="posSearch"
                        placeholder="Search product or barcode..."
                    >

                </div>


                <div
                    id="posProducts"
                    class="product-grid"
                ></div>

            </div>


            <div class="card">

                <h3>
                    Current Sale
                </h3>


                <div id="cart"></div>


                <div class="cart-total">

                    Total:

                    <span id="cartTotal">
                        ₱0.00
                    </span>

                </div>


                <select
                    id="payment"
                    style="
                        width:100%;
                        padding:11px;
                        border:1px solid #ddd2c5;
                        border-radius:10px;
                    "
                >

                    <option value="Cash">
                        Cash
                    </option>

                    <option value="GCash">
                        GCash
                    </option>

                    <option value="Card">
                        Card
                    </option>

                </select>


                <button
                    class="primary"
                    style="
                        width:100%;
                        margin-top:12px;
                    "
                    id="checkout"
                    type="button"
                >
                    Confirm Payment
                </button>


                <div id="receipt"></div>

            </div>

        </div>
    `;


    renderPOSProducts();

    renderCart();


    $("#posSearch")?.addEventListener(
        "input",
        renderPOSProducts
    );


    $("#checkout")?.addEventListener(
        "click",
        checkoutSale
    );
}


/* =========================================================
   POS PRODUCTS
   ========================================================= */

function renderPOSProducts() {
    const container =
        $("#posProducts");

    if (!container) {
        return;
    }

    const search =
        ($("#posSearch")?.value || "")
            .trim()
            .toLowerCase();

    const filtered =
        products.filter(
            product => {
                const name =
                    String(
                        product.product_name ||
                        ""
                    )
                        .toLowerCase();

                const code =
                    String(
                        product.product_code ||
                        ""
                    )
                        .toLowerCase();

                return (
                    name.includes(search) ||
                    code.includes(search)
                );
            }
        );

    container.innerHTML =
        filtered.map(
            product => {

                /*
                 * Use the product image if one exists.
                 * Supports both "image" and "image_url".
                 */
                const productImage =
                    product.image ||
                    product.image_url ||
                    "";

                const productVisual =
                    productImage
                        ? `
                            <img
                                src="${escapeHtml(productImage)}"
                                alt="${escapeHtml(product.product_name)}"
                                class="pos-product-image"
                                onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                            >
                            <div
                                class="pos-product-image-placeholder"
                                style="display:none;"
                            >
                                🍫
                            </div>
                        `
                        : `
                            <div class="pos-product-image-placeholder">
                                🍫
                            </div>
                        `;

                return `
                    <div
                        class="product-card"
                        data-product-id="${product.id}"
                    >

                        <div class="pos-product-image-wrap">
                            ${productVisual}
                        </div>

                        <strong>
                            ${escapeHtml(
                                product.product_name
                            )}
                        </strong>

                        <div class="muted">
                            ${escapeHtml(
                                product.product_code ||
                                ""
                            )}
                        </div>

                        <div class="price">
                            ${money(
                                product.price
                            )}
                        </div>

                        <div class="muted">
                            Stock:
                            ${product.stock_quantity}
                        </div>

                    </div>
                `;
            }
        ).join("");

    $$(".product-card").forEach(
        card => {
            card.addEventListener(
                "click",
                function () {
                    const product =
                        products.find(
                            item =>
                                String(
                                    item.id
                                ) ===
                                String(
                                    card.dataset.productId
                                )
                        );

                    if (product) {
                        addToCart(
                            product
                        );
                    }
                }
            );
        }
    );
}


/* =========================================================
   CART
   ========================================================= */

function addToCart(product) {

    const stock =
        Number(
            product.stock_quantity ||
            0
        );


    if (stock <= 0) {

        alert(
            "This product is out of stock."
        );

        return;
    }


    const existing =
        cart.find(
            item =>
                String(item.id) ===
                String(product.id)
        );


    if (existing) {

        if (
            existing.quantity >=
            stock
        ) {

            alert(
                "Not enough stock available."
            );

            return;
        }


        existing.quantity +=
            1;

    } else {

        cart.push({

            ...product,

            quantity:
                1
        });
    }


    renderCart();
}


/* =========================================================
   RENDER CART
   ========================================================= */

function renderCart() {

    const container =
        $("#cart");

    const totalElement =
        $("#cartTotal");


    if (!container) {

        return;
    }


    let total =
        0;


    if (!cart.length) {

        container.innerHTML = `

            <div class="muted">

                No items in the current sale.

            </div>

        `;

    } else {

        container.innerHTML =
            cart.map(
                (item, index) => {

                    const subtotal =
                        Number(
                            item.price ||
                            0
                        ) *
                        Number(
                            item.quantity ||
                            0
                        );


                    total +=
                        subtotal;


                    return `

                        <div class="cart-row">

                            <div>

                                <strong>

                                    ${escapeHtml(
                                        item.product_name
                                    )}

                                </strong>


                                <div class="muted">

                                    ${item.quantity}

                                    ×

                                    ${money(
                                        item.price
                                    )}

                                </div>

                            </div>


                            <div>

                                <strong>

                                    ${money(
                                        subtotal
                                    )}

                                </strong>


                                <button
                                    type="button"
                                    class="danger"
                                    data-remove-cart="${index}"
                                    style="margin-left:8px;"
                                >
                                    Remove
                                </button>

                            </div>

                        </div>

                    `;
                }
            ).join("");
    }


    if (totalElement) {

        totalElement.textContent =
            money(total);
    }


    $$("[data-remove-cart]")
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function () {

                        const index =
                            Number(
                                button.dataset.removeCart
                            );


                        cart.splice(
                            index,
                            1
                        );


                        renderCart();
                    }
                );
            }
        );
}


/* =========================================================
   CHECKOUT
   ========================================================= */

async function checkoutSale() {

    if (!cart.length) {

        alert(
            "Please add at least one product."
        );

        return;
    }


    const checkoutButton =
        $("#checkout");


    const payment =
        $("#payment")?.value ||
        "Cash";


    const items =
        cart.map(
            item => ({

                product_id:
                    item.id,

                quantity:
                    Number(
                        item.quantity
                    ),

                price:
                    Number(
                        item.price
                    )
            })
        );


    if (checkoutButton) {

        checkoutButton.disabled =
            true;

        checkoutButton.textContent =
            "Processing...";
    }


    try {

        const result =
            await api(
                "/api/sales",
                {
                    method: "POST",

                    body:
                        JSON.stringify({

                            payment_method:
                                payment,

                            items:
                                items
                        })
                }
            );


        if ($("#receipt")) {

            $("#receipt").innerHTML = `

                <div class="receipt">

                    <strong>
                        Sale Completed
                    </strong>

                    <p>
                        Transaction recorded successfully.
                    </p>

                    <p>

                        Total:

                        <strong>

                            ${money(
                                result.total_amount
                            )}

                        </strong>

                    </p>

                </div>

            `;
        }


        cart = [];


        await loadAll();


        showPage("pos");


    } catch (error) {

        console.error(
            "Checkout error:",
            error
        );


        alert(
            error.message ||
            "Unable to complete sale."
        );


    } finally {

        if (checkoutButton) {

            checkoutButton.disabled =
                false;

            checkoutButton.textContent =
                "Confirm Payment";
        }
    }
}


/* =========================================================
   PRODUCTS
   ========================================================= */

function renderProducts() {

    const page =
        $("#page-products");


    if (!page) {

        return;
    }


    page.innerHTML = `

        <div class="section-title">

            <h3>
                Products
            </h3>


            <button
                class="primary"
                type="button"
                id="addProductBtn"
            >
                Add Product
            </button>

        </div>


        <div class="table-wrap">

            <table class="table">

                <thead>

                    <tr>

                        <th>Code</th>

                        <th>Product</th>

                        <th>Price</th>

                        <th>Stock</th>

                        <th>Reorder Level</th>

                    </tr>

                </thead>


                <tbody>

                    ${
                        products.map(
                            product => `

                                <tr>

                                    <td>

                                        ${escapeHtml(
                                            product.product_code
                                        )}

                                    </td>


                                    <td>

                                        ${escapeHtml(
                                            product.product_name
                                        )}

                                    </td>


                                    <td>

                                        ${money(
                                            product.price
                                        )}

                                    </td>


                                    <td>

                                        ${
                                            product.stock_quantity
                                        }

                                    </td>


                                    <td>

                                        ${
                                            product.reorder_level
                                        }

                                    </td>

                                </tr>

                            `
                        ).join("")

                        ||

                        `

                            <tr>

                                <td colspan="5">

                                    No products found.

                                </td>

                            </tr>

                        `
                    }

                </tbody>

            </table>

        </div>
    `;
}


/* =========================================================
   CUSTOMERS
   ========================================================= */

function renderCustomers() {

    const page =
        $("#page-customers");


    if (!page) {

        return;
    }


    page.innerHTML = `

        <div class="section-title">

           

        <div class="table-wrap">

            <table class="table">

                <thead>

                    <tr>

                        <th>Name</th>

                        <th>Contact</th>

                        <th>Type</th>

                    </tr>

                </thead>


                <tbody>

                    ${
                        customers.map(
                            customer => `

                                <tr>

                                    <td>

                                        ${escapeHtml(
                                            customer.full_name
                                        )}

                                    </td>


                                    <td>

                                        ${escapeHtml(
                                            customer.contact ||
                                            customer.phone ||
                                            ""
                                        )}

                                    </td>


                                    <td>

                                        ${escapeHtml(
                                            customer.customer_type ||
                                            "Individual"
                                        )}

                                    </td>

                                </tr>

                            `
                        ).join("")

                        ||

                        `

                            <tr>

                                <td colspan="3">

                                    No customers found.

                                </td>

                            </tr>

                        `
                    }

                </tbody>

            </table>

        </div>
    `;
}


/* =========================================================
   SUPPLIERS
   ========================================================= */

function renderSuppliers() {

    const page =
        $("#page-suppliers");


    if (!page) {

        return;
    }


    page.innerHTML = `

        <div class="section-title">

            <h3>
                Suppliers
            </h3>

        </div>


        <div class="table-wrap">

            <table class="table">

                <thead>

                    <tr>

                        <th>Supplier</th>

                        <th>Contact</th>

                        <th>Address</th>

                    </tr>

                </thead>


                <tbody>

                    ${
                        suppliers.map(
                            supplier => `

                                <tr>

                                    <td>

                                        ${escapeHtml(
                                            supplier.name
                                        )}

                                    </td>


                                    <td>

                                        ${escapeHtml(
                                            supplier.contact ||
                                            supplier.phone ||
                                            ""
                                        )}

                                    </td>


                                    <td>

                                        ${escapeHtml(
                                            supplier.address ||
                                            ""
                                        )}

                                    </td>

                                </tr>

                            `
                        ).join("")

                        ||

                        `

                            <tr>

                                <td colspan="3">

                                    No suppliers found.

                                </td>

                            </tr>

                        `
                    }

                </tbody>

            </table>

        </div>
    `;
}


/* =========================================================
   REPORTS
   ========================================================= */

function renderReports() {

    const page =
        $("#page-reports");


    if (!page) {

        return;
    }


    page.innerHTML = `

        <div class="grid">

            <div class="card">

                <div class="muted">
                    Sales Report
                </div>

                <div class="metric">
                    ${money(0)}
                </div>

            </div>


            <div class="card">

                <div class="muted">
                    Inventory Report
                </div>

                <div class="metric">
                    ${products.length}
                </div>

            </div>


            <div class="card">

                <div class="muted">
                    Customers
                </div>

                <div class="metric">
                    ${customers.length}
                </div>

            </div>


            <div class="card">

                <div class="muted">
                    Suppliers
                </div>

                <div class="metric">
                    ${suppliers.length}
                </div>

            </div>

        </div>
    `;
}


/* =========================================================
   INITIALIZATION
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        /*
         * IMPORTANT:
         *
         * DO NOT automatically log in.
         *
         * DO NOT automatically redirect.
         *
         * DO NOT call /api/auth/login here.
         *
         * The user must press Sign In.
         */

        showLoginView();


        /*
         * Dashboard is only the internal default page.
         * This does NOT log the user in.
         */

        showPage(
            "dashboard"
        );


        /*
         * Database status.
         */

        if ($("#dbStatus")) {

            $("#dbStatus").textContent =
                "Checking...";
        }


        /* =================================================
           LOGIN FORM
           ================================================= */

        const loginForm =
            $("#loginForm");


        if (loginForm) {

            loginForm.addEventListener(
                "submit",
                handleLogin
            );
        }


        /* =================================================
           SIGNUP FORM
           ================================================= */

        const signupFormElement =
            $("#signupForm");


        if (signupFormElement) {

            signupFormElement.addEventListener(
                "submit",
                handleSignUp
            );
        }


        /* =================================================
           BUTTONS
           ================================================= */

        setupSignUpButton();

        setupBackToLoginButton();


        /* =================================================
           PASSWORD TOGGLES
           ================================================= */

        setupPasswordToggle(
            "password",
            "togglePassword"
        );


        setupPasswordToggle(
            "signupPassword",
            "toggleSignupPassword"
        );


        setupPasswordToggle(
            "confirmPassword",
            "toggleConfirmPassword"
        );


        /* =================================================
           LOGOUT
           ================================================= */

        const logoutButton =
            $("#logoutBtn");


        if (logoutButton) {

            logoutButton.addEventListener(
                "click",
                handleLogout
            );
        }


        /* =================================================
           NAVIGATION
           ================================================= */

        setupNavigation();


        /*
         * IMPORTANT:
         *
         * loadAll() is NOT called here.
         *
         * The login page must remain a login page.
         */

        console.log(
            "Dalareich POS login page initialized."
        );

        console.log(
            "No automatic login is performed."
        );
    }
);