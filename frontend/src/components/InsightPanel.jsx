function chipColor(label) {
  const upper = String(label || "").toUpperCase();
  if (upper === "PERSON") return "border-fuchsia-400/30 bg-fuchsia-400/10 text-fuchsia-100";
  if (upper === "DATE" || upper === "TIME") return "border-amber-400/30 bg-amber-400/10 text-amber-100";
  if (upper === "GPE" || upper === "LOC") return "border-violet-400/30 bg-violet-400/10 text-violet-100";
  if (upper === "ORG") return "border-cyan-400/30 bg-cyan-400/10 text-cyan-100";
  return "border-white/10 bg-white/5 text-zinc-100";
}

function InsightPanel({ result }) {
  if (!result) {
    return (
      <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl">
        <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">Analysis</p>
        <h2 className="mt-2 text-2xl font-bold text-white">Document insights will appear here</h2>
        <p className="mt-3 text-sm leading-6 text-zinc-200">
          After processing a PDF, this panel shows document stats, top keywords, extracted
          entities, and whether the spaCy model was loaded successfully.
        </p>
      </section>
    );
  }

  const { document, keywords = [], entities = [], pipeline = {} } = result;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">Analysis</p>
          <h2 className="mt-2 text-2xl font-bold text-white">Pipeline output</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-200">
            Everything below is produced locally from the uploaded PDF. No external APIs are
            used at any stage.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-zinc-950/50 px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">spaCy model</p>
          <p className="mt-1 text-sm font-semibold text-white">
            {pipeline.spaCy_model_loaded ? "Loaded" : "Fallback mode"}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-white/10 bg-zinc-950/40 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Pages</p>
          <p className="mt-2 text-2xl font-bold text-white">{document.page_count}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-zinc-950/40 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Sentences</p>
          <p className="mt-2 text-2xl font-bold text-white">{document.sentence_count}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-zinc-950/40 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Words</p>
          <p className="mt-2 text-2xl font-bold text-white">{document.word_count}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-zinc-950/40 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Quiz items</p>
          <p className="mt-2 text-2xl font-bold text-white">{result.quiz.length}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-zinc-950/40 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Top keywords</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {keywords.length ? (
              keywords.map((keyword) => (
                <span
                  key={keyword.text}
                  className="rounded-full border border-fuchsia-300/20 bg-fuchsia-400/10 px-3 py-1 text-sm text-fuchsia-100"
                >
                  {keyword.text}
                  <span className="ml-2 mono text-xs text-fuchsia-200/70">
                    {keyword.score.toFixed(2)}
                  </span>
                </span>
              ))
            ) : (
              <span className="text-sm text-zinc-300">No keywords extracted.</span>
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-zinc-950/40 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-zinc-400">Named entities</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {entities.length ? (
              entities.map((entity) => (
                <span
                  key={`${entity.text}-${entity.label}-${entity.start}`}
                  className={`rounded-full border px-3 py-1 text-sm ${chipColor(entity.label)}`}
                >
                  {entity.text}
                  <span className="ml-2 mono text-xs opacity-75">{entity.label}</span>
                </span>
              ))
            ) : (
              <span className="text-sm text-zinc-300">No entities detected.</span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export default InsightPanel;
