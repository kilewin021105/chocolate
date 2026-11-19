/* =========================================================
   USER REPORTS / COMPLAINTS
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const reportForm =
        document.getElementById("reportForm");

    if (!reportForm) {
        return;
    }


    reportForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const subject =
                document
                    .getElementById("reportSubject")
                    .value
                    .trim();


            const type =
                document
                    .getElementById("reportType")
                    .value;


            const orderId =
                document
                    .getElementById("reportOrderId")
                    .value
                    .trim();


            const message =
                document
                    .getElementById("reportMessage")
                    .value
                    .trim();


            const messageBox =
                document.getElementById(
                    "reportMessageBox"
                );


            if (!subject || !type || !message) {

                messageBox.style.display =
                    "block";

                messageBox.textContent =
                    "Please complete all required fields.";

                return;
            }


            const submitButton =
                reportForm.querySelector(
                    'button[type="submit"]'
                );


            submitButton.disabled = true;

            submitButton.textContent =
                "Submitting...";


            try {

                /*
                 * Get the logged-in customer.
                 */

                let currentUser = null;

                try {

                    currentUser =
                        JSON.parse(
                            localStorage.getItem(
                                "dalareichUser"
                            ) ||
                            localStorage.getItem(
                                "dalareichCurrentUser"
                            ) ||
                            "null"
                        );

                } catch (error) {

                    console.warn(
                        "Could not read current user.",
                        error
                    );

                }


                /*
                 * Send report to Flask.
                 */

                const response =
                    await fetch(
                        "/api/reports/customer",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            credentials: "include",

                            body: JSON.stringify({

                                user_id:
                                    currentUser?.id ||
                                    null,

                                customer:
                                    currentUser?.name ||
                                    currentUser?.customer_name ||
                                    "",

                                email:
                                    currentUser?.email ||
                                    "",

                                subject:
                                    subject,

                                type:
                                    type,

                                order_id:
                                    orderId ||
                                    null,

                                message:
                                    message

                            })
                        }
                    );


                const result =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.message ||
                        "Failed to submit report."
                    );

                }


                messageBox.style.display =
                    "block";

                messageBox.textContent =
                    "Your report has been submitted successfully.";


                reportForm.reset();


            } catch (error) {

                console.error(
                    "Report submission error:",
                    error
                );


                messageBox.style.display =
                    "block";

                messageBox.textContent =
                    error.message ||
                    "Unable to submit your report.";

            } finally {

                submitButton.disabled =
                    false;

                submitButton.textContent =
                    "Submit Report";

            }

        }
    );

});