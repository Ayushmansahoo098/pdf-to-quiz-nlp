import { useState } from "react";
import InsightPanel from "../components/InsightPanel";
import QuestionSection from "../components/QuestionSection";
import UploadPanel from "../components/UploadPanel";
import { generateQuiz } from "../lib/api";
import { normalizeAnswer } from "../components/QuestionCard";

const QUESTION_ORDER = [
  { key: "mcq", title: "MCQ", description: "Choose the correct option extracted from the PDF." },
  { key: "fill_blank", title: "Fill in the blanks", description: "Type the missing keyword or entity." },
  { key: "wh", title: "WH questions", description: "Answer who, when, where, or what from the sentence context." },
  { key: "true_false", title: "True / False", description: "Judge whether the generated statement is correct." },
];

function groupQuestions(quiz = []) {
  return quiz.reduce((accumulator, item) => {
    accumulator[item.type] = accumulator[item.type] || [];
    accumulator[item.type].push(item);
    return accumulator;
  }, {});
}

function getQuestionTypeLabel(type) {
  return QUESTION_ORDER.find((item) => item.key === type)?.title || type;
}

function normalizeText(value) {
  return normalizeAnswer(value);
}

function isCorrectAnswer(item, value) {
  if (item.type === "true_false") {
    return String(value || "").toLowerCase() === String(item.answer).toLowerCase();
  }

  if (!value) {
    return false;
  }

  if (item.type === "mcq") {
    return String(value) === String(item.answer);
  }

  const expected = normalizeText(item.answer);
  const response = normalizeText(value);
  if (!expected || !response) {
    return false;
  }

  return response === expected || response.includes(expected) || expected.includes(response);
}

function HomePage() {
  const [file, setFile] = useState(null);
  const [questionsPerType, setQuestionsPerType] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [answers, setAnswers] = useState({});
  const [revealed, setRevealed] = useState(false);
  const [feedback, setFeedback] = useState({});
  const [score, setScore] = useState({ correct: 0, total: 0, percentage: 0 });

  const handleGenerate = async () => {
    if (!file) {
      setError("Please select a PDF first.");
      return;
    }

    setError("");
    setLoading(true);
    setRevealed(false);
    setFeedback({});
    setScore({ correct: 0, total: 0, percentage: 0 });

    try {
      const payload = await generateQuiz(file, questionsPerType);
      setResult(payload);
      setAnswers({});
    } catch (exception) {
      setError(exception.message || "Quiz generation failed.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckAnswers = () => {
    if (!result?.quiz?.length) {
      return;
    }

    const nextFeedback = {};
    let correctCount = 0;

    for (const item of result.quiz) {
      const correct = isCorrectAnswer(item, answers[item.id]);
      nextFeedback[item.id] = correct;
      if (correct) {
        correctCount += 1;
      }
    }

    setFeedback(nextFeedback);
    setRevealed(true);
    const total = result.quiz.length;
    setScore({
      correct: correctCount,
      total,
      percentage: total ? Math.round((correctCount / total) * 100) : 0,
    });
  };

  const groupedQuestions = groupQuestions(result?.quiz || []);
  const totalQuestions = result?.quiz?.length || 0;

  return (
    <main className="min-h-screen px-4 py-8 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl sm:p-8 animate-float">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs uppercase tracking-[0.35em] text-fuchsia-300/80">Offline NLP</p>
              <h1 className="mt-3 text-4xl font-bold tracking-tight text-white sm:text-5xl">
                Offline NLP-Based PDF Quiz Generator
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-zinc-200">
                Upload any PDF and generate MCQs, fill-in-the-blanks, WH questions, and
                true/false items using a fully local NLP pipeline built with PyMuPDF, NLTK,
                spaCy, scikit-learn, and WordNet.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:w-[28rem]">
              {["PyMuPDF", "NLTK", "spaCy", "TF-IDF"].map((item, i) => (
                <div
                  key={item}
                  className={`rounded-2xl border border-white/10 bg-zinc-950/40 px-4 py-3 text-sm text-zinc-100 ${i % 2 === 0 ? 'animate-float' : 'animate-float-delayed'}`}
                >
                  <p className="mono text-xs uppercase tracking-[0.24em] text-zinc-400">
                    local stack
                  </p>
                  <p className="mt-1 font-semibold text-white">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </header>

        <div className="mt-8 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-8">
            <UploadPanel
              file={file}
              onFileChange={setFile}
              questionsPerType={questionsPerType}
              onQuestionsPerTypeChange={setQuestionsPerType}
              onGenerate={handleGenerate}
              loading={loading}
            />

            {error ? (
              <div className="rounded-3xl border border-rose-400/30 bg-rose-400/10 p-4 text-sm text-rose-100">
                {error}
              </div>
            ) : null}

            {result ? (
              <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">Quiz</p>
                    <h2 className="mt-2 text-2xl font-bold text-white">Generated questions</h2>
                    <p className="mt-2 text-sm leading-6 text-zinc-200">
                      {totalQuestions} questions generated across {QUESTION_ORDER.length} types.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-zinc-950/50 px-4 py-3 text-right">
                    <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Score</p>
                    <p className="mt-1 text-2xl font-bold text-white">
                      {revealed ? `${score.correct}/${score.total}` : "Not graded"}
                    </p>
                    <p className="mono mt-1 text-xs text-zinc-300">
                      {revealed ? `${score.percentage}%` : "Submit to evaluate"}
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex flex-wrap gap-2">
                  {QUESTION_ORDER.map((item) => (
                    <span
                      key={item.key}
                      className="rounded-full border border-white/10 bg-zinc-950/40 px-3 py-1 text-xs uppercase tracking-[0.22em] text-zinc-200"
                    >
                      {getQuestionTypeLabel(item.key)}: {groupedQuestions[item.key]?.length || 0}
                    </span>
                  ))}
                </div>
              </section>
            ) : null}

            {result ? (
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleCheckAnswers}
                  className="rounded-2xl bg-gradient-to-r from-fuchsia-400 to-violet-400 px-5 py-3 text-sm font-semibold text-zinc-950 transition hover:scale-[1.01]"
                >
                  Check answers
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAnswers({});
                    setRevealed(false);
                    setFeedback({});
                    setScore({ correct: 0, total: 0, percentage: 0 });
                  }}
                  className="rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
                >
                  Reset quiz
                </button>
              </div>
            ) : null}

            {QUESTION_ORDER.map((section) => (
              <QuestionSection
                key={section.key}
                title={section.title}
                description={section.description}
                questions={groupedQuestions[section.key] || []}
                answers={answers}
                onAnswerChange={(questionId, value) =>
                  setAnswers((current) => ({
                    ...current,
                    [questionId]: value,
                  }))
                }
                revealed={revealed}
                feedback={feedback}
              />
            ))}
          </div>

          <div className="space-y-8">
            <InsightPanel result={result} />

            <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl">
              <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">How it works</p>
              <div className="mt-4 space-y-3 text-sm leading-6 text-zinc-200">
                <p>1. Extract text from the PDF with PyMuPDF.</p>
                <p>2. Tokenize, remove stopwords, and lemmatize locally with NLTK.</p>
                <p>3. Rank sentences using TF-IDF and extract keywords.</p>
                <p>4. Detect entities with spaCy and build question templates.</p>
                <p>5. Generate distractors from WordNet and related document terms.</p>
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-fuchsia-400/10 to-violet-400/10 p-6 shadow-glow backdrop-blur-xl">
              <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">Outcome</p>
              <h3 className="mt-2 text-2xl font-bold text-white">What you get</h3>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-zinc-100">
                <li>• Local quiz generation without external APIs</li>
                <li>• MCQ, fill-in-the-blank, WH, and true/false question types</li>
                <li>• TF-IDF keywords, named entities, and ranked source sentences</li>
                <li>• A responsive interface for uploads, review, and scoring</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}

export default HomePage;
