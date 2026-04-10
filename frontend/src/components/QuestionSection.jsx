import QuestionCard from "./QuestionCard";

function QuestionSection({ title, description, questions, answers, onAnswerChange, revealed, feedback }) {
  if (!questions.length) {
    return null;
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">{title}</p>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-200">{description}</p>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-zinc-100">
          {questions.length} question{questions.length === 1 ? "" : "s"}
        </div>
      </div>

      <div className="space-y-4">
        {questions.map((item) => (
          <QuestionCard
            key={item.id}
            item={item}
            value={answers[item.id] ?? ""}
            onChange={(value) => onAnswerChange(item.id, value)}
            revealed={revealed}
            correct={feedback[item.id] ?? false}
          />
        ))}
      </div>
    </section>
  );
}

export default QuestionSection;
