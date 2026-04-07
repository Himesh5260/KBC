#KBC

from flask import Flask, render_template, request, session, redirect, url_for # type: ignore
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

questions = [
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["A. Venus", "B. Mars", "C. Jupiter", "D. Saturn"],
        "answer": "B"
    },
    {
        "question": "How many sides does a hexagon have?",
        "options": ["A. 5", "B. 7", "C. 6", "D. 8"],
        "answer": "C"
    },
    {
        "question": "What is the chemical symbol for water?",
        "options": ["A. O2", "B. CO2", "C. H2O", "D. HO"],
        "answer": "C"
    },
    {
        "question": "Who wrote the play 'Romeo and Juliet'?",
        "options": ["A. Charles Dickens", "B. William Shakespeare", "C. Mark Twain", "D. Jane Austen"],
        "answer": "B"
    },
    {
        "question": "What is the capital city of Japan?",
        "options": ["A. Beijing", "B. Seoul", "C. Bangkok", "D. Tokyo"],
        "answer": "D"
    },
    {
        "question": "Which gas do plants absorb from the atmosphere?",
        "options": ["A. Oxygen", "B. Nitrogen", "C. Carbon Dioxide", "D. Hydrogen"],
        "answer": "C"
    },
    {
        "question": "How many continents are there on Earth?",
        "options": ["A. 5", "B. 6", "C. 8", "D. 7"],
        "answer": "D"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["A. Atlantic Ocean", "B. Indian Ocean", "C. Pacific Ocean", "D. Arctic Ocean"],
        "answer": "C"
    },
    {
        "question": "Which element has the atomic number 1?",
        "options": ["A. Helium", "B. Oxygen", "C. Carbon", "D. Hydrogen"],
        "answer": "D"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["A. Vincent van Gogh", "B. Pablo Picasso", "C. Leonardo da Vinci", "D. Michelangelo"],
        "answer": "C"
    },
    {
        "question": "What is the speed of light (approximately)?",
        "options": ["A. 300,000 km/s", "B. 150,000 km/s", "C. 500,000 km/s", "D. 1,000,000 km/s"],
        "answer": "A"
    },
    {
        "question": "Which country is the largest by land area?",
        "options": ["A. China", "B. United States", "C. Canada", "D. Russia"],
        "answer": "D"
    },
    {
        "question": "What is the square root of 144?",
        "options": ["A. 11", "B. 12", "C. 13", "D. 14"],
        "answer": "B"
    },
    {
        "question": "Which organ pumps blood through the human body?",
        "options": ["A. Lungs", "B. Liver", "C. Heart", "D. Kidney"],
        "answer": "C"
    },
    {
        "question": "How many zeros are in one crore?",
        "options": ["A. 5", "B. 6", "C. 7", "D. 8"],
        "answer": "C"
    },
]

prize_ladder = [
    1000, 2000, 3000, 5000, 10000,
    20000, 40000, 80000, 160000, 320000,
    640000, 1250000, 2500000, 5000000, 10000000
]

safe_havens = [4, 9]

def format_inr(amount):
    s = str(amount)
    if len(s) <= 3:
        return s
    result = s[-3:]
    s = s[:-3]
    while len(s) > 2:
        result = s[-2:] + "," + result
        s = s[:-2]
    if s:
        result = s + "," + result
    return result

@app.route("/")
def index():
    session.clear()
    session["question_index"] = 0
    session["safe_amount"] = 0
    return render_template("index.html")

@app.route("/play")
def play():
    idx = session.get("question_index", 0)
    if idx >= len(questions):
        return redirect(url_for("result", won=True))
    q = questions[idx]
    prize = prize_ladder[idx]
    safe = session.get("safe_amount", 0)
    return render_template(
        "play.html",
        question=q,
        q_num=idx + 1,
        prize=format_inr(prize),
        prize_raw=prize,
        prize_ladder=prize_ladder,
        safe=format_inr(safe),
        current_idx=idx,
        safe_havens=safe_havens,
        format_inr=format_inr,
        total=len(questions)
    )

@app.route("/answer", methods=["POST"])
def answer():
    idx = session.get("question_index", 0)
    selected = request.form.get("choice")
    correct = questions[idx]["answer"]
    prize = prize_ladder[idx]

    if selected == correct:
        if idx in safe_havens:
            session["safe_amount"] = prize
        session["question_index"] = idx + 1
        if idx + 1 >= len(questions):
            session["final_amount"] = prize
            return redirect(url_for("result", won=True))
        return redirect(url_for("correct_answer", prize=format_inr(prize)))
    else:
        safe = session.get("safe_amount", 0)
        session["final_amount"] = safe
        return redirect(url_for("wrong_answer",
                                correct=correct,
                                selected=selected,
                                safe=format_inr(safe),
                                question_text=questions[idx]["question"]))

@app.route("/correct")
def correct_answer():
    prize = request.args.get("prize", "0")
    return render_template("correct.html", prize=prize)

@app.route("/wrong")
def wrong_answer():
    correct = request.args.get("correct")
    selected = request.args.get("selected")
    safe = request.args.get("safe", "0")
    question_text = request.args.get("question_text", "")
    return render_template("wrong.html", correct=correct, selected=selected,
                           safe=safe, question_text=question_text)

@app.route("/quit")
def quit_game():
    idx = session.get("question_index", 0)
    if idx == 0:
        amount = 0
    else:
        amount = prize_ladder[idx - 1]
    safe = session.get("safe_amount", 0)
    final = max(amount, safe)
    session["final_amount"] = final
    return redirect(url_for("result", won=False, quit=True, amount=format_inr(final)))

@app.route("/result")
def result():
    won = request.args.get("won", "False") == "True"
    quit_game_flag = request.args.get("quit", "False") == "True"
    amount = session.get("final_amount", 0)
    return render_template("result.html", won=won, quit=quit_game_flag,
                           amount=format_inr(amount), amount_raw=amount)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
