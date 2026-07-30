# Demo Video Script: Active Silence in Beethoven

Target length: 4:00-4:20.

Primary goal: present the demo as a reproducible inspection artifact, with one author-owned audio-plus-MIDI recording used as a construct check. The author-owned recording is audible in the video but is not part of the 16-recording professional corpus.

## Required Captions

Use burned-in captions or platform captions. Keep them short and technical:

- "Author-owned demo recording; excluded from corpus statistics."
- "Professional corpus audio is not redistributed."
- "MIDI times are aligned to audio by a declared +4.358 s offset."
- "`d_s`: detected sounding span; `d_l`: detected low-energy span."
- "Release gap = audio threshold crossing - aligned MIDI note-off."
- "Post-hoc trajectory split: descriptive grouping, not a tested performer type."

## 0:00-0:18 -- Title Card, Then The Question

Screen: static title card for about 6 seconds, then cut to the live viewer.

Title card:

```text
Active Silence in Beethoven
Pause Strategies in the Grave of the Pathetique

Harold Wang
West Point Grey Academy, Vancouver

ISMIR 2026 Late-Breaking Demo (non-archival)
```

Action: cut to the public viewer with `HW_GRAVE_DEMO - Harold Wang (owned demo recording)` already loaded.

Voiceover: "A written rest tells a pianist to stop. It does not tell them for how long. This demo measures what an energy-based detector actually finds inside four pauses in the Grave of the Pathetique, and how far that measurement sits from what the performer actually did."

## 0:18-0:50 -- What The Detector Reports

Screen: boundary overlay for corrected P1, with `silence_start = 14.722 s` visible. Use browser zoom around 110% so `event start`, `silence start`, and `silence end` are legible.

Action: select `HW_GRAVE_DEMO`, select `P1`, click `Show Event`, and let the audio play through the pause: real playing, then silence, then the next attack.

Voiceover: "Each pause is split into two spans. The blue span, `d_s`, is sounding time before the detector's threshold is crossed. The red span, `d_l`, is how long the signal stays below that threshold. For this pause, `d_l` is 0.380 seconds. Both are detector outputs. Neither is a measurement of musical intention, and that distinction matters."

Speak or caption: "`d_l = 0.380 s`."

## 0:50-1:35 -- The Result: The Initial Hypothesis Was Not Supported

Screen: scroll to the trajectory figure. Hold on it long enough for the pause labels and line styles to be visible.

Action: add a lower-third text block with the main numbers as they are spoken.

Voiceover: "The initial hypothesis was that the second pause would be systematically longest. Across sixteen professional recordings, that is not supported. The longest pause falls at P2 in nine recordings and at P3 in seven, giving a two-sided binomial p of 0.80. The paired P2-P3 difference is -0.49 seconds, with a 95 percent interval from -1.42 to +0.43 seconds. The interval contains zero. Sixteen performances cannot separate these two pauses; that is weaker than showing them equal, so I report it as a null result."

Voiceover continuation: "Across all four pauses there is a moderate ordering, with Kendall's W of 0.46. But removing P4 drops W to 0.14. The apparent ordering is therefore close to the single statement that the final caesura is shortest."

Speak or caption: "`9 of 16 / 7 of 16`, `p = 0.80`, `-0.49 s`, `95% CI [-1.42, +0.43]`, `W = 0.46 -> 0.14`."

On-screen note: "The figure's two line groups are split post hoc by the sign of the within-recording covariance between `d_s` and `d_l`. This is an exploratory descriptor, not a tested grouping."

## 1:35-2:15 -- Why The Null Is The Interesting Part

Screen: threshold dropdown and sensitivity summary. Keep the page label "Aggregate threshold summary (does not re-run detection)" visible.

Action: change the threshold dropdown once, then click `Show Event`.

Voiceover: "The null result matters because the detector uses an absolute decibel threshold. That makes it sensitive to how loud the source file is. Normalising all sixteen files to -1 dBFS moves the within-recording P2-P3 difference by 0.25 seconds on average, and by as much as 3.62 seconds in one recording. The effect I was trying to measure is 0.49 seconds. At this precision, a claim about which middle pause is longer would also be a claim about file level and mastering."

Voiceover continuation: "This control reports aggregate metadata only. It does not rerun the selected event in the browser."

Speak or caption: "`-1 dBFS`, `0.25 s average shift`, `3.62 s largest shift`, `0.49 s P2-P3 effect`."

## 2:15-3:15 -- The Ground-Truth Check

Screen: `MIDI/Audio Release Check` panel on the author-owned recording.

Action: step through P1, P2, P3, and P4, clicking `Show Event` after each dropdown change so the four gap values appear in turn.

Voiceover: "Everything so far has one unmeasured assumption: that the point where audio energy falls below threshold is close to the point where the pianist actually stopped. On a piano it cannot be exact, because strings keep ringing after the key is released."

Voiceover continuation: "To check that construct directly, I recorded the Grave myself while capturing audio and MIDI. The MIDI note-off is the moment my finger left the key. The detector boundary is what the audio algorithm reports. Their difference is the error I could not observe in the commercial recordings."

Voiceover continuation: "Across the four pauses, the detector boundary appears between 0.056 and 0.188 seconds after the aligned MIDI note-off, about 0.11 seconds on average. It is late in every pause, which is what damped string decay predicts."

Voiceover continuation: "Two caveats are important. This is one performance by one pianist, and it is excluded from the corpus statistics; it is a construct check, not a seventeenth corpus recording. Also, the audio and MIDI files were not started on the same clock, so the pipeline declares a constant audio-minus-MIDI offset of 4.358 seconds. The offset estimate carries about 30 milliseconds of uncertainty, which is the noise floor on a roughly 0.11 second measurement."

Speak or caption: "`+0.188 / +0.106 / +0.056 / +0.106 s`, `mean about 0.11 s`, `offset uncertainty about +/- 0.03 s`."

On-screen caption: "Author-owned recording. Excluded from corpus statistics."

## 3:15-3:42 -- What Reproduces, And What Does Not

Screen: repository README, focused on the reproduction section.

Voiceover: "The statistics and figures regenerate from the shipped CSVs without redistributing audio. The event table, boundary table, waveform panels, and threshold summaries document the detector output; recreating the waveform panels for the professional corpus requires local copies of the source recordings. The corpus recordings are commercial, so the demo distributes descriptors and boundary metadata only. The playable audio in the public demo is the author-owned performance used for the MIDI/audio check."

## 3:42-4:00 -- Close

Screen: return to the boundary overlay, select corrected P4 at `silence_start = 36.037 s`, click `Show Event`, and play the last two seconds before the closing card.

Voiceover: "The contribution is a small, reproducible inspection interface for active silence, plus one measured estimate of how far an energy threshold sits from a real key release. The next methodological step is to replace order-selected event recovery with score alignment, so the pauses are located by the score rather than by their position in time."

Closing card:

```text
Active Silence in Beethoven
Harold Wang
ISMIR 2026 Late-Breaking Demo (non-archival)

Code: https://github.com/haroldwangca/active-silence-pathetique
Demo: https://haroldwangca.github.io/active-silence-pathetique/demo/

Corpus recordings are commercial and not redistributed.
Playable audio is the author's own performance.
```

## Recording Checklist

- Record the browser window at 1920x1080 or higher.
- Use the hosted GitHub Pages page, not a `file://` URL.
- Use browser zoom around 110-125% if JSON or waveform labels are too small.
- Click `Show Event` after every dropdown change before narrating that event.
- Check each audio fragment before recording. The P1 fragment should contain playing, detected low energy, and the following attack, not room tone.
- Do not include commercial audio.
- Do not describe the detector-performer discrepancy as a performance error. It is a property of the detector and signal model.
- Export captions as WebVTT or burn them into the video. Include the spoken numbers because they carry the argument.
- Export as MP4, H.264 High, 1920x1080, CRF 20 or similar, AAC 128 kbps mono.
