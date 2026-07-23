async function readCsv(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Could not load ${path} (${response.status})`);
  }
  const text = await response.text();
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",");
  return lines.map((line) => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] ?? "";
    });
    return row;
  });
}

async function loadAudioPaths() {
  try {
    return await fetch("audio_paths.json").then((response) => response.json());
  } catch (error) {
    return {};
  }
}

async function main() {
  const recordingSelect = document.getElementById("recording");
  const output = document.getElementById("output");
  const events = await readCsv("../data/events.csv");
  const audioPaths = await loadAudioPaths();
  const sourceEvents = events.filter((row) => row.condition === "source");
  const recordings = [...new Set(sourceEvents.map((row) => row.recording_id))];

  recordings.forEach((recordingId) => {
    const option = document.createElement("option");
    option.value = recordingId;
    option.textContent = recordingId;
    recordingSelect.appendChild(option);
  });

  document.getElementById("show").addEventListener("click", () => {
    const selected = sourceEvents.find(
      (row) => row.recording_id === recordingSelect.value && row.pause === pauseSelect.value
    );
    output.textContent = JSON.stringify(
      {
        event: selected ?? null,
        local_audio_path: audioPaths[recordingSelect.value] ?? "not configured"
      },
      null,
      2
    );
  });
}

main().catch((error) => {
  const output = document.getElementById("output");
  output.textContent = [
    "The demo could not load its CSV files.",
    "",
    "Serve over HTTP: run python3 -m http.server 8000 from the repo root, then open http://localhost:8000/demo/",
    "",
    "GitHub does not execute this HTML directly; the demo runs locally (or later via GitHub Pages).",
    "",
    `Technical detail: ${error.message}`
  ].join("\n");
});
