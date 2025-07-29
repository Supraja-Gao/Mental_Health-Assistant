document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("diary-form");
  const diaryInput = document.getElementById("diary-entry");
  const errorMsg = document.getElementById("diary-error");
  const sentimentResult = document.getElementById("sentiment-result");
  const sentimentText = document.getElementById("sentiment-text");
  const historyList = document.getElementById("history-list");

  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const content = diaryInput.value.trim();
    errorMsg.classList.add("hidden");
    sentimentResult.classList.add("hidden");

    if (!content) {
      errorMsg.classList.remove("hidden");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/diary/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ content })
      });

      const result = await res.json();
      if (!res.ok) {
        throw new Error(result.detail || "Failed to save");
      }

      sentimentText.textContent = `Sentiment: ${result.sentiment}`;
      sentimentResult.classList.remove("hidden");
      form.reset();
      fetchHistory();
    } catch (err) {
      console.error("Submit error:", err);
      alert(err.message || "Server error on diary submit");
    }
  });

  async function fetchHistory() {
    try {
      const res = await fetch("http://127.0.0.1:8000/diary/history", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!res.ok) throw new Error(`History fetch failed: ${res.status}`);
      const entries = await res.json();

      historyList.innerHTML = "";
      if (!Array.isArray(entries)) throw new Error("Invalid response");

      for (const entry of entries) {
        const item = document.createElement("li");
        item.className = "bg-gray-200 dark:bg-gray-700 p-3 rounded";
        item.innerHTML = `
          <p><strong>Sentiment:</strong> ${entry.sentiment} </p>
          <p class="text-sm mt-1">${new Date(entry.created_at).toLocaleString()}</p>
          <p class="mt-2">${entry.content}</p>
        `;
        historyList.appendChild(item);
      }
    } catch (err) {
      console.error(err);
      historyList.innerHTML = `<p class="text-sm text-red-500">${err.message}</p>`;
    }
  }

  fetchHistory();
});
