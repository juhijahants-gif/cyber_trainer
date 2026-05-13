let score = 0;
let index = 0;
let time = 30;
let timerRunning = true;

// LOAD QUESTION

function loadQ() {
    let quiz = document.getElementById("quiz");

    if (index >= questions.length) {
        finishQuiz();
        return;
    }

    let q = questions[index];

    let optionsHTML = "";

    q.options.forEach(option => {
       optionsHTML += `
    <button onclick="checkAnswer('${option}', '${q.answer}', this)">
        ${option}
    </button>
`;
    });

    quiz.innerHTML = `
        <h3>${q.q}</h3>
        <div>${optionsHTML}</div>
    `;
}
// CHECK ANSWER
function checkAnswer(selected, correct, btn) {
    let buttons = document.querySelectorAll("#quiz button");

    // Disable all buttons after click
    buttons.forEach(b => b.disabled = true);

    if (selected.trim().toLowerCase() === correct.trim().toLowerCase()) {
        btn.classList.add("correct"); // green glow
        document.getElementById("wrongSound").play();
        score++;
    } else {
        btn.classList.add("wrong"); // red glow
        document.getElementById("correctSound").play();

        // Highlight correct answer also
        buttons.forEach(b => {
            if (b.innerText.trim().toLowerCase() === correct.trim().toLowerCase()) {
                b.classList.add("correct");
            }
        });
    }

    // Wait 1 second before next question
    setTimeout(() => {
        index++;
        loadQ();
    }, 1000);
}

// SUBMIT
function submitQuiz() {
    if (!timerRunning) return;
    timerRunning = false;

    let totalQ = questions ? questions.length : 0;

    let form = document.createElement("form");
    form.method = "POST";
    form.action = "/result";

    form.innerHTML += `<input type="hidden" name="score" value="${score}">`;
    form.innerHTML += `<input type="hidden" name="total" value="${totalQ}">`;
    form.innerHTML += `<input type="hidden" name="name" value="Player">`;

    document.body.appendChild(form);

    console.log("Submitting:", score, totalQ);

    form.submit();
}

// TIMER
let timer = setInterval(() => {
    if (!timerRunning) {
        clearInterval(timer);
        return;
    }

    time--;

    let timerEl = document.getElementById("timer");
    if (timerEl) {
        timerEl.innerText = "Time: " + time;
    }

    if (time <= 0) {
        submitQuiz();
    }
}, 1000);

// START
window.onload = function () {
    if (typeof questions === "undefined") {
        console.error("Questions not loaded!");
        return;
    }

    loadQ();
};
function finishQuiz() {
    let form = document.createElement("form");
    form.method = "POST";
    form.action = "/result";

    let scoreInput = document.createElement("input");
    scoreInput.name = "score";
    scoreInput.value = score;

    let totalInput = document.createElement("input");
    totalInput.name = "total";
    totalInput.value = questions.length;

    form.appendChild(scoreInput);
    form.appendChild(totalInput);

    document.body.appendChild(form);
    form.submit();
}