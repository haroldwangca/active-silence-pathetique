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
  const bundledPaths = {
    HW_GRAVE_DEMO: "../media/harold_grave.m4a"
  };
  try {
    const configuredPaths = await fetch("audio_paths.json").then((response) => response.json());
    return { ...bundledPaths, ...configuredPaths };
  } catch (error) {
    return bundledPaths;
  }
}

function drawTimeline(boundary) {
  const canvas = document.getElementById("timeline");
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.font = "13px Georgia";
  context.fillStyle = "#181512";
  if (!boundary || typeof boundary === "string") {
    context.fillText("Boundary metadata unavailable for this selection.", 24, 62);
    return;
  }
  const eventStart = Number(boundary.event_start);
  const silenceStart = Number(boundary.silence_start);
  const silenceEnd = Number(boundary.silence_end);
  const total = Math.max(silenceEnd - eventStart, 0.001);
  const left = 80;
  const width = 610;
  const y = 48;
  const xSilence = left + ((silenceStart - eventStart) / total) * width;
  context.strokeStyle = "#222";
  context.lineWidth = 1;
  context.strokeRect(left, y, width, 22);
  context.fillStyle = "#587ca3";
  context.fillRect(left, y, Math.max(0, xSilence - left), 22);
  context.fillStyle = "#b95d4f";
  context.fillRect(xSilence, y, Math.max(0, left + width - xSilence), 22);
  context.fillStyle = "#181512";
  context.fillText(`event start ${eventStart.toFixed(3)}s`, left, 30);
  context.fillText(`silence start ${silenceStart.toFixed(3)}s`, xSilence - 46, 88);
  context.fillText(`event end ${silenceEnd.toFixed(3)}s`, left + width - 90, 30);
  context.fillStyle = "#587ca3";
  context.fillText("sounding d_s", 24, 108);
  context.fillStyle = "#b95d4f";
  context.fillText("low-energy d_l", 150, 108);
}

function safeWaveformName(pianist, pause) {
  return `${pianist.replaceAll(" ", "_")}_${pause}.png`;
}

async function main() {
  const recordingSelect = document.getElementById("recording");
  const pauseSelect = document.getElementById("pause");
  const thresholdSelect = document.getElementById("threshold");
  const audio = document.getElementById("audio");
  const output = document.getElementById("output");
  const releaseOutput = document.getElementById("release-output");
  const waveform = document.getElementById("waveform");
  const waveformNote = document.getElementById("waveform-note");
  const events = await readCsv("../data/events.csv");
  const demoEvents = await readCsv("../data/demo_recording_events.csv").catch(() => []);
  const boundaries = await readCsv("../data/pause_boundaries_source.csv").catch(() => []);
  const demoBoundaries = await readCsv("../data/demo_recording_boundaries.csv").catch(() => []);
  const demoReleaseRows = await readCsv("../data/demo_recording_midi_release.csv").catch(() => []);
  const thresholdRows = await readCsv("../data/threshold_sweep.csv").catch(() => []);
  const audioPaths = await loadAudioPaths();
  const sourceEvents = events.filter((row) => row.condition === "source");
  const inspectableEvents = [...demoEvents, ...sourceEvents];
  const inspectableBoundaries = [...demoBoundaries, ...boundaries];
  const recordings = [...new Set(inspectableEvents.map((row) => row.recording_id))];
  const labelByRecording = new Map(
    inspectableEvents.map((row) => [
      row.recording_id,
      row.condition === "demo_recording"
        ? `${row.recording_id} - ${row.pianist} (owned demo recording)`
        : `${row.recording_id} - ${row.pianist}`
    ])
  );

  recordings.forEach((recordingId) => {
    const option = document.createElement("option");
    option.value = recordingId;
    option.textContent = labelByRecording.get(recordingId) ?? recordingId;
    recordingSelect.appendChild(option);
  });

  thresholdRows.forEach((row) => {
    const option = document.createElement("option");
    option.value = row.threshold_setting;
    option.textContent = row.threshold_setting;
    option.selected = row.threshold_setting === "-35dB_0.10s";
    thresholdSelect.appendChild(option);
  });

  document.getElementById("show").addEventListener("click", () => {
    const selected = inspectableEvents.find(
      (row) => row.recording_id === recordingSelect.value && row.pause === pauseSelect.value
    );
    const boundary = inspectableBoundaries.find(
      (row) => row.recording_id === recordingSelect.value && row.pause === pauseSelect.value
    );
    const releaseCheck = demoReleaseRows.find(
      (row) => row.recording_id === recordingSelect.value && row.pause === pauseSelect.value
    );
    const threshold = thresholdRows.find((row) => row.threshold_setting === thresholdSelect.value);
    const audioPath = audioPaths[recordingSelect.value] ?? "";
    if (audioPath) {
      const start = boundary?.event_start ?? "";
      const end = boundary?.event_end ?? "";
      audio.src = start && end ? `${audioPath}#t=${start},${end}` : audioPath;
      audio.hidden = false;
    } else {
      audio.removeAttribute("src");
      audio.hidden = true;
    }
    if (selected) {
      const waveformPath = `../figures/waveform_panels/${safeWaveformName(selected.pianist, selected.pause)}`;
      waveform.src = waveformPath;
      waveform.hidden = false;
      waveformNote.textContent = `Waveform panel: ${selected.pianist} ${selected.pause}`;
      waveform.onerror = () => {
        waveform.hidden = true;
        waveformNote.textContent = "No waveform panel is bundled for this selection. Regenerate all panels with code/07_waveform_panels.py.";
      };
    } else {
      waveform.removeAttribute("src");
      waveform.hidden = true;
      waveformNote.textContent = "No event row is available for this selection.";
    }
    drawTimeline(boundary);
    releaseOutput.textContent = releaseCheck
      ? JSON.stringify(releaseCheck, null, 2)
      : "MIDI/audio release comparison is available only for the author-owned demo recording.";
    output.textContent = JSON.stringify(
      {
        event: selected ?? null,
        detector_boundaries: boundary ?? "run code/05_boundaries.py with local audio to regenerate",
        midi_audio_release_check: releaseCheck ?? "not available for this recording",
        threshold_summary: threshold ?? "aggregate threshold summary not available",
        local_audio_path: audioPath || "not configured"
      },
      null,
      2
    );
  });
  document.getElementById("show").click();
}

main().catch((error) => {
  const output = document.getElementById("output");
  output.textContent = [
    "The demo could not load its CSV files.",
    "",
    "Serve over HTTP: run python3 -m http.server 8000 from the repo root, then open http://localhost:8000/demo/",
    "",
    "The public demo is available through GitHub Pages; local viewing requires an HTTP server.",
    "",
    `Technical detail: ${error.message}`
  ].join("\n");
});
