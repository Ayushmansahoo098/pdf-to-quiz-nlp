function typeLabel(type) {
  switch (type) {
    case "mcq":
      return "MCQ";
    case "fill_blank":
      return "Fill in the blank";
    case "wh":
      return "WH question";
    case "true_false":
      return "True / False";
    default:
      return type;
  }
}

function normalizeAnswer(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function QuestionCard({ item, value, onChange, revealed, correct }) {
  const answerDisplay = typeof item.answer === "boolean" ? (item.answer ? "True" : "False") : item.answer;

  return (
    <article
      className={`rounded-3xl border p-5 shadow-glow transition ${
        revealed
          ? correct
            ? "border-violet-400/40 bg-violet-400/10"
            : "border-rose-400/40 bg-rose-400/10"
          : "border-white/10 bg-white/5"
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full border border-white/10 bg-zinc-950/50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-fuchsia-200">
              {typeLabel(item.type)}
            </span>
            {item.focus_label ? (
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-zinc-200">
                {item.focus_label}
              </span>
            ) : null}
          </div>
          <h3 className="max-w-3xl text-lg font-semibold leading-7 text-white">{item.prompt}</h3>
        </div>
      </div>

      <div className="mt-5">
        {item.type === "mcq" || item.type === "true_false" ? (
          <div className="grid gap-3 md:grid-cols-2">
            {(item.options?.length ? item.options : ["True", "False"]).map((option) => {
              const optionValue = item.type === "true_false" ? String(option).toLowerCase() : option;
              const selected = String(value || "") === optionValue;
              return (
                <button
                  key={option}
                  type="button"
                  onClick={() => onChange(optionValue)}
                  className={`rounded-2xl border px-4 py-3 text-left text-sm transition ${
                    selected
                      ? "border-fuchsia-300 bg-fuchsia-400/10 text-white"
                      : "border-white/10 bg-zinc-950/30 text-zinc-100 hover:border-fuchsia-300/40"
                  }`}
                >
                  <span className="mr-3 inline-flex h-6 w-6 items-center justify-center rounded-full border border-white/10 bg-white/5 text-[11px] font-semibold text-zinc-100">
                    {item.type === "true_false" ? (optionValue === "true" ? "T" : "F") : option.charAt(0)}
                  </span>
                  {option}
                </button>
              );
            })}
          </div>
        ) : (
          <label className="block">
            <span className="sr-only">Answer</span>
            <input
              type="text"
              value={value || ""}
              onChange={(event) => onChange(event.target.value)}
              placeholder="Type your answer"
              className="w-full rounded-2xl border border-white/10 bg-zinc-950/40 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-400 focus:border-fuchsia-300/60"
            />
          </label>
        )}
      </div>

      <div className="mt-5 rounded-2xl border border-white/10 bg-zinc-950/40 p-4 text-sm text-zinc-200">
        <p className="text-xs uppercase tracking-[0.25em] text-zinc-400">Source sentence</p>
        <p className="mt-2 leading-6">{item.source_sentence}</p>
      </div>

      {revealed ? (
        <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-sm font-semibold text-white">Correct answer:</span>
            <span className="mono rounded-full border border-white/10 bg-zinc-950/60 px-3 py-1 text-sm text-fuchsia-200">
              {answerDisplay}
            </span>
            <span className={`text-sm font-semibold ${correct ? "text-violet-300" : "text-rose-300"}`}>
              {correct ? "Correct" : "Incorrect"}
            </span>
          </div>
          {item.explanation ? <p className="mt-2 text-sm leading-6 text-zinc-200">{item.explanation}</p> : null}
        </div>
      ) : null}
    </article>
  );
}

export { normalizeAnswer };
export default QuestionCard;
