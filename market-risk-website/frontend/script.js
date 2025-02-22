document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("riskForm").addEventListener("submit", function (event) {
        event.preventDefault();
        let inputData = document.getElementById("inputData").value;

        try {
            let jsonData = JSON.parse(inputData); // Ensure valid JSON
            fetch("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jsonData),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("result").innerText = "Risk Score: " + (data.risk_score ?? data.error);
            })
            .catch(error => console.error("Error:", error));
        } catch (e) {
            alert("Invalid JSON format. Please enter valid JSON.");
        }
    });
});
