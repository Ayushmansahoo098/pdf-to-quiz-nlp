import { useRef, useState } from "react";

function UploadPanel({
  file,
  onFileChange,
  questionsPerType,
  onQuestionsPerTypeChange,
  onGenerate,
  loading,
}) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const openFilePicker = () => {
    inputRef.current?.click();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    const droppedFile = event.dataTransfer.files?.[0];
    if (droppedFile) {
      onFileChange(droppedFile);
    }
  };

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300/80">Input</p>
          <h2 className="mt-2 text-2xl font-bold text-white">Upload a PDF</h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-zinc-200">
            The document stays local. The backend extracts text with PyMuPDF, processes it
            with NLTK and spaCy, then builds quiz items from TF-IDF keywords and WordNet
            distractors.
          </p>
        </div>
        <div className="hidden rounded-full border border-violet-400/30 bg-violet-400/10 px-3 py-1 text-xs font-medium text-violet-200 sm:block">
          Offline only
        </div>
      </div>

      <div
        className={`mt-6 rounded-3xl border border-dashed p-6 transition ${
          dragActive
            ? "border-fuchsia-300 bg-fuchsia-400/10"
            : "border-white/15 bg-zinc-950/30 hover:border-fuchsia-300/50"
        }`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={(event) => onFileChange(event.target.files?.[0] || null)}
        />

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm text-zinc-200">
              {file ? "Selected file" : "Drop your PDF here or choose a file manually."}
            </p>
            <p className="mt-1 text-lg font-semibold text-white">
              {file ? file.name : "No file selected"}
            </p>
            <p className="mt-1 text-xs text-zinc-300">PDF only, processed locally.</p>
          </div>

          <button
            type="button"
            onClick={openFilePicker}
            className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/10 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/15"
          >
            Choose PDF
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
        <label className="block">
          <span className="text-sm text-zinc-200">Questions per type</span>
          <input
            type="range"
            min="1"
            max="8"
            value={questionsPerType}
            onChange={(event) => onQuestionsPerTypeChange(Number(event.target.value))}
            className="mt-3 w-full accent-fuchsia-400"
          />
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-300">
            <span>1</span>
            <span className="mono rounded-full border border-white/10 bg-zinc-950/50 px-3 py-1 text-zinc-100">
              {questionsPerType} per type
            </span>
            <span>8</span>
          </div>
        </label>

        <button
          type="button"
          onClick={onGenerate}
          disabled={loading || !file}
          className="inline-flex min-w-36 items-center justify-center rounded-2xl bg-gradient-to-r from-fuchsia-400 to-violet-400 px-5 py-3 text-sm font-semibold text-zinc-950 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Generating..." : "Generate quiz"}
        </button>
      </div>
    </section>
  );
}

export default UploadPanel;
