# Demo Video Script: Active Silence in Beethoven

Target length: 4:30-5:00.

Primary goal: show a reproducible inspection artifact with one author-owned audible example, while keeping the 16-performance professional corpus analytically separate. The video should not present the author recording as a seventeenth corpus row.

## Required Captions

Use burned-in captions or platform captions. Keep them short and technical:

- "Author-owned demo recording; excluded from corpus statistics."
- "Professional corpus audio is not redistributed."
- "MIDI times are aligned to audio by a declared +4.358 s offset."
- "`d_s`: detected sounding span; `d_l`: detected low-energy span."
- "Release gap = audio threshold crossing - aligned MIDI note-off."

## 0:00-0:20 — Opening With Audible Boundary

Screen: public demo page at `https://haroldwangca.github.io/active-silence-pathetique/demo/`.

Action: page loads on `HW_GRAVE_DEMO - Harold Wang (owned demo recording)`, pause `P1`. If it does not auto-load after refresh, click `Show Event`. Press play in the browser audio control. Let the P1 fragment play while the boundary overlay and waveform panel are visible.

Voiceover: "This opening uses an author-owned recording, so the demo can include sound without redistributing commercial recordings. The blue span is detected sounding time, and the red span is the following low-energy interval."

Numbers to show or mention: P1 has `d_s = 3.184 s`, `d_l = 0.380 s`.

## 0:20-0:45 — What The Page Is Reading

Screen: show the opening paragraph, recording dropdown, and selected-event JSON.

Action: briefly open the recording dropdown so viewers see both `HW_GRAVE_DEMO` and the professional recording IDs.

Voiceover: "The page reads derived event tables, detector-boundary metadata, waveform panels, and threshold-sensitivity summaries. The professional recordings are represented by descriptors and boundary metadata only. The playable file is separate: it is an author-owned Grave take used for demonstration and MIDI/audio calibration."

Caption: "Demo recording is not included in Table 1."

## 0:45-1:30 — MIDI/Audio Clock Offset And Release Gap

Screen: show the `MIDI/Audio Release Check` panel for P1, then select P4 and click `Show Event`.

Action: highlight `midi_audio_offset_sec`, `aligned_midi_last_note_off_sec`, `audio_silence_start_sec`, and `audio_minus_midi_release_sec`.

Voiceover: "The audio and MIDI files were not started on the same clock. Rather than trimming the audio, the pipeline declares a constant audio-minus-MIDI offset of 4.358 seconds, with about 30 milliseconds of uncertainty from two onset matches. After alignment, the release gap is physically interpretable: it measures how long after key release the audio falls below the fixed -35 dBFS threshold."

Numbers to mention:

- P1 release gap: `+0.188 s`.
- P2 release gap: `+0.106 s`.
- P3 release gap: `+0.056 s`.
- P4 release gap: `+0.106 s`.

Voiceover continuation: "Those values are all positive, as expected for piano sound: the key is released, the damped sound decays, and only then does the audio threshold crossing occur."

## 1:30-2:15 — Boundary Model And Construct Caution

Screen: keep P4 selected because its waveform is visually clearer. If changing dropdowns, click `Show Event` after each change.

Action: crop around the waveform panel. Point to `event start`, `silence start`, and `silence end`.

Voiceover: "`d_s` and `d_l` are detector-derived descriptors, not direct measurements of intention. The MIDI/audio check makes that limitation concrete. On this controlled recording, the detector's threshold boundary is about a tenth of a second later than the aligned key release. That is the missing construct check the paper says commercial recordings cannot provide."

On-screen text: "Mean release gap across P1-P4: about 0.11 s."

## 2:15-3:00 — Corpus Result: No Supported P2-P3 Contrast

Screen: scroll to the trajectory figure, or show the selected-event panel for a professional recording and then the trajectory figure. If changing the recording dropdown, click `Show Event`.

Voiceover: "The corpus result remains separate from this demo recording. Across sixteen nominally distinct professional recordings, the recording-level low-energy peak falls at P2 in nine recordings and P3 in seven. The binomial test gives p = 0.80, and the paired P2-P3 difference is -0.49 seconds with a confidence interval from -1.42 to +0.43 seconds. The result is not evidence for a stable P2-P3 contrast."

On-screen caption: "Corpus: 16 professional recordings; demo recording excluded."

## 3:00-3:40 — Four-Pause Ordering And P4 Dependence

Screen: trajectory figure.

Action: zoom enough to show P1-P4 labels and the downward P4 tendency.

Voiceover: "There is a broader four-pause ordering: Kendall's W is 0.46 across P1 through P4. But that agreement depends strongly on P4 being short. Removing P4 drops W to 0.14. So the defensible claim is not that every middle pause behaves the same way; it is that the descriptor view exposes where the apparent regularity comes from."

## 3:40-4:20 — Sensitivity And Reproducibility

Screen: show the threshold dropdown and selected-event JSON. Then briefly show repository files: `code/09_demo_recording.py`, `data/demo_recording_manifest.csv`, `data/demo_recording_midi_release.csv`, and `media/harold_grave.m4a`.

Action: change the threshold dropdown once and click `Show Event`. Keep the label visible: "Aggregate threshold summary (does not re-run detection)."

Voiceover: "The threshold dropdown reports aggregate sensitivity metadata; it does not rerun the selected event in the browser. In the paper's corpus analysis, peak normalization moves the paired P2-P3 mean from -0.49 seconds to -0.24 seconds, and individual recordings shift by as much as several seconds. That sensitivity is why the demo emphasizes inspection and reproducibility rather than a single detector boundary as ground truth."

## 4:20-4:55 — Closing

Screen: return to P1 or P4 on the demo page. Press play for a short audible fragment.

Voiceover: "The contribution is a compact inspection tool for active silence. It separates residual sounding time from low-energy duration, keeps copyrighted audio outside the hosted corpus artifact, and uses one author-owned audio-plus-MIDI recording to calibrate what the audio detector is measuring."

Final on-screen text:

```text
Active Silence Viewer
Code and demo: github.com/haroldwangca/active-silence-pathetique
Author-owned playback example; professional corpus audio not redistributed.
```

## Filming Checklist

- Record the browser window at 1080p or higher.
- Use the hosted GitHub Pages page, not a `file://` URL.
- Use browser zoom around 110-125% if JSON or waveform labels are too small.
- Click `Show Event` after every dropdown change before narrating.
- Verify the first audio fragment is audible before recording.
- Do not include commercial audio.
- Do not describe the author-owned take as validating corpus statistics. It illustrates the detector boundary and provides a MIDI/audio construct check.
