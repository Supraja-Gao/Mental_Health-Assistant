document.addEventListener("DOMContentLoaded", async () => {
  const recommendationDiv = document.getElementById("recommendations-list");

  const userId = localStorage.getItem("user_id");
  const token = localStorage.getItem("token");

  if (!userId || !token) {
    recommendationDiv.innerHTML = `<p class="text-red-500">🔒 Please log in to view your personalized recommendation.</p>`;
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/recommend/user/me`, {
  headers: {
    Authorization: `Bearer ${token}`
  }
});


    const data = await response.json();
    console.log("🧠 Recommendation API Response:", data);

    if (!response.ok || !data.generated_recommendation) {
      recommendationDiv.innerHTML = `
        <div class="bg-yellow-100 text-yellow-700 p-4 rounded">
          ⚠️ ${data.error || "No recommendation available. Make sure you've submitted both a diary entry and completed the quiz."}
        </div>
      `;
      return;
    }

    recommendationDiv.innerHTML = `
      <div class="bg-blue-100 dark:bg-gray-700 p-4 rounded-md border-l-4 border-blue-500">
        <h3 class="text-lg font-semibold mb-2">🌱 Your Personalized Recommendation</h3>
        <p>${data.generated_recommendation}</p>
      </div>
    `;
  } catch (err) {
    console.error("❌ Fetch error:", err);
    recommendationDiv.innerHTML = `
      <p class="text-red-500">Error loading recommendation: ${err.message}</p>
    `;
  }
});
