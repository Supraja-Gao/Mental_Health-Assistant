document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('quiz-form');
  const resultDiv = document.getElementById('quiz-result');
  const traitResults = document.getElementById('trait-results');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 🔐 Get token from localStorage (matching login.js)
    const token = localStorage.getItem('token'); // ✅ fixed key

    if (!token) {
      alert("Please login to submit quiz results.");
      window.location.href = "login.html";
      return;
    }

    const formData = new FormData(form);
    const scores = {
      openness: parseInt(formData.get('q1_openness')) || 0,
      conscientiousness: (parseInt(formData.get('q2_conscientiousness')) || 0) + (parseInt(formData.get('q3_conscientiousness')) || 0),
      extraversion: (parseInt(formData.get('q4_extraversion')) || 0) + (parseInt(formData.get('q5_extraversion')) || 0),
      agreeableness: (parseInt(formData.get('q6_agreeableness')) || 0) + (parseInt(formData.get('q7_agreeableness')) || 0),
      neuroticism: (parseInt(formData.get('q8_neuroticism')) || 0) + (parseInt(formData.get('q9_neuroticism')) || 0) + (parseInt(formData.get('q10_neuroticism')) || 0),
    };

    const percentages = {
      openness: (scores.openness / 5) * 100,
      conscientiousness: (scores.conscientiousness / 10) * 100,
      extraversion: (scores.extraversion / 10) * 100,
      agreeableness: (scores.agreeableness / 10) * 100,
      neuroticism: (scores.neuroticism / 15) * 100,
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/quiz/submit', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scores: percentages
        })
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

    } catch (err) {
      alert("Failed to save quiz results: " + err.message);
      return;
    }

    // 📊 Show results
    traitResults.innerHTML = Object.entries(percentages).map(([trait, percent]) => `
      <div>
        <h4 class="font-semibold capitalize">${trait}</h4>
        <p>${percent.toFixed(0)}% - ${getTraitDescription(trait, percent)}</p>
        <div class="w-full bg-gray-300 dark:bg-gray-600 rounded-full h-2.5">
          <div class="bg-blue-500 h-2.5 rounded-full" style="width: ${percent}%"></div>
        </div>
      </div>
    `).join('');

    form.classList.add('hidden');
    resultDiv.classList.remove('hidden');
  });

  function getTraitDescription(trait, percentage) {
    if (percentage >= 80) return `Very high ${trait}`;
    if (percentage >= 60) return `High ${trait}`;
    if (percentage >= 40) return `Moderate ${trait}`;
    if (percentage >= 20) return `Low ${trait}`;
    return `Very low ${trait}`;
  }
});
