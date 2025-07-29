document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("psychometric-form");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Map questions to the Big Five quiz fields
    const answers = {};
    for (let i = 1; i <= 3; i++) {
      const selected = document.querySelector(`input[name="q${i}"]:checked`);
      if (!selected) {
        alert(`Please answer question ${i}`);
        return;
      }
      answers[`q${i}`] = parseInt(selected.value);
    }

    // Split the 3 example questions into 5 traits manually
    // Replace this logic once you add 10 actual trait-mapped questions
    const payload = {
      q1_openness: answers.q1,
      q2_openness: answers.q3,
      q3_conscientiousness: answers.q2,
      q4_conscientiousness: answers.q2,
      q5_extraversion: answers.q1,
      q6_extraversion: answers.q3,
      q7_agreeableness: answers.q1,
      q8_agreeableness: answers.q2,
      q9_neuroticism: answers.q2,
      q10_neuroticism: answers.q3
    };

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/psychometrics/quiz", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to fetch psychometric result.");
      }

      resultDiv.innerHTML = `
        <h2>Results</h2>
        <p><strong>Cluster:</strong> ${data.matched_cluster}</p>
        <p><strong>Description:</strong> ${data.cluster_description}</p>
        <p><strong>Traits:</strong></p>
        <ul>
          <li>Openness: ${data.input_traits.openness.toFixed(2)}</li>
          <li>Conscientiousness: ${data.input_traits.conscientiousness.toFixed(2)}</li>
          <li>Extraversion: ${data.input_traits.extraversion.toFixed(2)}</li>
          <li>Agreeableness: ${data.input_traits.agreeableness.toFixed(2)}</li>
          <li>Neuroticism: ${data.input_traits.neuroticism.toFixed(2)}</li>
        </ul>
        ${data.tied_clusters ? `<p><strong>Tied Clusters:</strong> ${data.tied_clusters.join(", ")}</p>` : ""}
      `;
    } catch (err) {
      console.error(err);
      resultDiv.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
    }
  });
});
