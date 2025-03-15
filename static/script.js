document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("joinMeeting").addEventListener("click", async function () {
        try {
            let response = await fetch("/check_recognition");
            let data = await response.json();
            console.log(data); // Debugging in browser console

            if (data.status === "success") {
                alert(data.message);
                window.location.href = "/join_meeting";
            } else {
                alert("Access Denied: Face not recognized.");
            }
        } catch (error) {
            console.error("API Error:", error);
            alert("An error occurred. Please try again.");
        }
    });
});
