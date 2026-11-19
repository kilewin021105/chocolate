/* =========================================================
   ADMIN CUSTOMER REPORTS
   ========================================================= */


/* =========================================================
   LOAD CUSTOMER REPORTS PAGE
   ========================================================= */

async function loadCustomerReports() {

    const page =
        document.getElementById("page-reports");

    if (!page) {
        return;
    }


    /* -----------------------------------------------------
       REPLACE THE OLD REPORT CARDS
       ----------------------------------------------------- */

    page.innerHTML = `

        <div class="admin-customer-reports">

            <div class="customer-reports-header">

                

                <button
                    type="button"
                    id="refreshCustomerReports">

                    ↻ Refresh

                </button>

            </div>


            <div
                id="customerReportsList"
                class="customer-reports-list">

                <div class="customer-report-loading">

                    Loading customer reports...

                </div>

            </div>

        </div>

    `;


    /* -----------------------------------------------------
       REFRESH BUTTON
       ----------------------------------------------------- */

    const refreshButton =
        document.getElementById(
            "refreshCustomerReports"
        );


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadCustomerReports
        );

    }


    /* -----------------------------------------------------
       GET CUSTOMER REPORTS
       ----------------------------------------------------- */

    await fetchCustomerReports();

}


/* =========================================================
   FETCH CUSTOMER REPORTS FROM DATABASE
   ========================================================= */

async function fetchCustomerReports() {

    const list =
        document.getElementById(
            "customerReportsList"
        );


    if (!list) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/reports/customer",
                {
                    method: "GET",

                    credentials: "include",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message ||
                "Failed to load customer reports."
            );

        }


        const reports =
            Array.isArray(result.reports)
                ? result.reports
                : [];


        /* -------------------------------------------------
           NO REPORTS
           ------------------------------------------------- */

        if (reports.length === 0) {

            list.innerHTML = `

                <div class="no-customer-reports">

                    <div class="no-report-icon">
                        📋
                    </div>

                    <h3>
                        No Customer Reports
                    </h3>

                    <p>
                        There are currently no
                        reports or complaints submitted
                        by customers.
                    </p>

                </div>

            `;

            return;
        }


        /* -------------------------------------------------
           DISPLAY CUSTOMER REPORTS
           ------------------------------------------------- */

        list.innerHTML =
            reports
                .map(
                    report => {

                        const date =
                            report.date
                                ? new Date(
                                    report.date
                                ).toLocaleString(
                                    "en-PH"
                                )
                                : "—";


                        const status =
                            report.status ||
                            "Pending";


                        const statusClass =
                            String(status)
                                .toLowerCase()
                                .replace(
                                    /\s+/g,
                                    "-"
                                );


                        return `

    <div
        class="customer-report-card"
        data-report-id="${escapeHtml(
            report.id
        )}">


        <!-- REPORT HEADER -->

        <div class="customer-report-top">

            <div>

                <h3>
                    ${escapeHtml(
                        report.subject ||
                        "Untitled Report"
                    )}
                </h3>

                <div class="customer-report-date">

                    ${escapeHtml(
                        date
                    )}

                </div>

            </div>


            

        </div>


        <!-- REPORT INFORMATION -->

        <div class="customer-report-info">


            <!-- REPORT TYPE -->

            <div>

                <strong>
                    Report Type
                </strong>

                <span>

                    ${escapeHtml(
                        report.type ||
                        "—"
                    )}

                </span>

            </div>


            <!-- ORDER ID -->

            <div>

                <strong>
                    Order ID
                </strong>

                <span>

                    ${escapeHtml(
                        report.order_id ||
                        "—"
                    )}

                </span>

            </div>


        </div>


        <!-- COMPLAINT / REPORT -->

        <div
            class="customer-report-message">

            <strong>
                Complaint / Report
            </strong>

            <p>

                ${escapeHtml(
                    report.message ||
                    ""
                )}

            </p>

        </div>


    </div>

`;

                    }
                )
                .join("");


    } catch (error) {

        console.error(
            "Customer reports error:",
            error
        );


        list.innerHTML = `

            <div
                class="customer-reports-error">

                Unable to load customer reports.

                <br>

                <small>

                    ${escapeHtml(
                        error.message ||
                        "Unknown error"
                    )}

                </small>

            </div>

        `;

    }

}


/* =========================================================
   WHEN ADMIN CLICKS REPORTS
   ========================================================= */

document.addEventListener(
    "click",
    function (event) {

        const reportsButton =
            event.target.closest(
                '[data-page="reports"]'
            );


        if (!reportsButton) {
            return;
        }


        /*
         * app.js loads the old report cards first.
         * This runs afterward and replaces them
         * with the customer reports page.
         */

        setTimeout(
            function () {

                loadCustomerReports();

            },
            0
        );

    }
);


/* =========================================================
   MAKE FUNCTION AVAILABLE
   ========================================================= */

window.loadCustomerReports =
    loadCustomerReports;