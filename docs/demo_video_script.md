# Demo Video Script: Active Silence in Beethoven

Target length: 2:30-3:00.

Primary goal: show that the artifact is an inspectable demo, not just a static paper supplement. The video should open with sound from the author-owned Grave recording, then show how the same detector-boundary representation used in the paper separates sounding duration (`d_s`) from low-energy duration (`d_l`).

## 0:00-0:08 — Opening With Sound

Screen: public demo page at `https://haroldwangca.github.io/active-silence-pathetique/demo/`.

Action: page loads on `HW_GRAVE_DEMO - Harold Wang (owned demo recording)`, pause `P1`. Press play in the browser audio control. Let the first event play for about six seconds while the boundary overlay and waveform panel are visible.

Voiceover: "This demo inspects what happens inside a notated pause. The blue portion marks detected sounding time, and the red portion marks the following low-energy interval."

Visual emphasis: keep the waveform panel and boundary overlay centered. Do not start with the trajectory figure.

## 0:08-0:28 — What The Demo Reads

Screen: slowly scroll or point to the opening paragraph and controls.

Action: show the recording dropdown, pause dropdown, and selected-event JSON.

Voiceover: "The hosted page reads derived event tables, detector-boundary metadata, and a threshold summary. The professional recordings in the study remain metadata-only because the source recordings are copyrighted. The playable file here is a separate author-owned Grave recording used for demonstration and MIDI/audio checking, not as a seventeenth corpus performance."

On-screen note if editing captions: "Author-owned demo recording; excluded from corpus statistics."

## 0:28-0:55 — Boundary Model On One Pause

Screen: select `P1`, then show the boundary overlay and waveform panel.

Action: zoom/crop so the waveform labels `event start`, `silence start`, and `silence end` are readable.

Voiceover: "`d_s` is the interval from the local event start to the detector's silence start. `d_l` is the detected low-energy duration. These are detector-derived descriptors. They are useful for inspection, but they are not direct measurements of musical intention."

Numbers to mention for current demo extraction: P1 has `d_s = 0.656 s` and `d_l = 2.414 s`.

## 0:55-1:20 — MIDI/Audio Release Check

Screen: show the "MIDI/Audio Release Check" panel for P1, then briefly switch to P4.

Action: highlight `midi_last_note_off_sec`, `audio_silence_start_sec`, and `audio_minus_midi_release_sec`.

Voiceover: "Because this recording has simultaneous MIDI, the demo can compare the audio threshold crossing with the last MIDI note-off in the same event window. In this take, the audio threshold often crosses before the final note-off. That does not invalidate the detector, but it shows why the paper treats these as energy-threshold descriptors rather than direct release measurements."

Numbers to mention:
- P1: audio minus MIDI release = `-2.340 s`.
- P4: audio minus MIDI release = `-0.343 s`.

Interpretation: say this as a construct check. Do not frame it as a performer error.

## 1:20-1:50 — Corpus-Level View

Screen: scroll to the trajectory figure.

Action: switch the dropdown from `HW_GRAVE_DEMO` to one professional recording, then return to the trajectory figure.

Voiceover: "The paper's corpus analysis stays separate. The trajectory figure summarizes sixteen nominally distinct professional recordings. The demo recording is not pooled with them. Its role is to make the boundary logic audible and to expose what the detector can and cannot distinguish."

Visual emphasis: use the figure to show that the paper's result concerns relative trajectories across P1-P4, not a single playback example.

## 1:50-2:15 — Sensitivity And Reproducibility

Screen: show the threshold dropdown and selected-event JSON.

Action: change the threshold dropdown once. Keep the label visible: "Aggregate threshold summary (does not re-run detection)."

Voiceover: "The threshold control reports aggregate sensitivity metadata. It does not silently rerun the selected event or choose a more favorable setting. The shipped CSVs and scripts regenerate the event table, boundary table, waveform panels, and the author-owned demo-recording check."

Optional screen: repository file list showing `code/09_demo_recording.py`, `data/demo_recording_midi_release.csv`, and `media/harold_grave.m4a`.

## 2:15-2:45 — Closing Claim

Screen: return to the boundary overlay with audio controls visible.

Action: play a short segment again, preferably P4 because it has a clearer waveform and a compact pause.

Voiceover: "The contribution is a small, reproducible inspection interface for active silence. It separates residual sounding time from low-energy duration, keeps copyrighted recordings external, and uses an author-owned recording to make the demo audible while keeping the corpus analysis intact."

Final on-screen text:

```text
Active Silence Viewer
Code and demo: github.com/haroldwangca/active-silence-pathetique
Author-owned playback example; professional corpus audio not redistributed.
```

## Recording Notes

- Record the browser window at 1080p or higher.
- Use the hosted GitHub Pages page, not a local file URL.
- Use browser zoom around 110-125% if the JSON or waveform labels are too small.
- Keep the first eight seconds visually simple: waveform, overlay, audio control.
- Do not include commercial audio in the video.
- Do not say the author-owned take validates the corpus statistics. Say it illustrates the detector boundary and provides a MIDI/audio construct check.
