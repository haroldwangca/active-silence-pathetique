# Demo Video Script: Active Silence in Beethoven

Target length: 3:45-4:15.

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

Screen: static title card for about 6 seconds, then cut to the live viewer with `HW_GRAVE_DEMO - Harold Wang (owned demo recording)` loaded.

Title card:

```text
Active Silence in Beethoven
Pause Strategies in the Grave of the Pathetique

Harold Wang
West Point Grey Academy, Vancouver

ISMIR 2026 Late-Breaking Demo (non-archival)
```

Voiceover: "A written rest tells a pianist to stop. It does not tell them for how long. This demo measures what an energy-based detector finds inside four pauses in the Grave of the Pathetique, and how far that measurement sits from what the performer actually did."

## 0:18-0:48 -- What The Detector Reports

Screen: boundary overlay, corrected P1, with `silence_start = 14.722 s` visible. Use browser zoom around 110% so `event start`, `silence start`, and `silence end` are legible.

Action: select `HW_GRAVE_DEMO`, select `P1`, click `Show Event`, and let the audio play through the pause: real playing, then silence, then the next attack.

Voiceover: "Each pause is split into two spans. The blue span, `d_s`, is sounding time before the detector's threshold is crossed. The red span, `d_l`, is how long the signal stays below that threshold. For this pause, `d_l` is 0.380 seconds. Both are detector outputs. Neither is a measurement of musical intention, and that distinction matters."

Caption: "`d_l = 0.380 s`."

## 0:48-1:30 -- The Result: The Hypothesis Was Not Supported

Screen: scroll to the trajectory figure. Hold long enough for the pause labels and line styles to read.

Action: add a lower-third text block with the numbers as they are spoken.

Voiceover: "My hypothesis was that the second pause is systematically longest. Across sixteen professional recordings it is not supported. The longest pause falls at P2 in nine recordings and P3 in seven, a two-sided binomial p of 0.80. The paired P2-P3 difference is minus 0.49 seconds, ninety-five percent interval minus 1.42 to plus 0.43. It contains zero. Sixteen performances cannot separate these pauses, which is weaker than showing them equal, so I report a null."

Voiceover continuation: "Across all four pauses the ordering is moderate, Kendall's W of 0.46. Remove P4 and W drops to 0.14, so the ordering is close to the single statement that the final caesura is shortest."

Caption: "`9 of 16 / 7 of 16`, `p = 0.80`, `-0.49 s`, `95% CI [-1.42, +0.43]`, `W = 0.46 -> 0.14`."

On-screen note: "The figure's two line groups are split post hoc by the sign of the within-recording covariance between `d_s` and `d_l`. An exploratory descriptor, not a tested grouping."

## 1:30-2:10 -- Why The Null Is The Interesting Part

Screen: threshold dropdown, then the sensitivity summary. Keep the page label "Aggregate threshold summary (does not re-run detection)" visible.

Action: change the threshold dropdown once, then click `Show Event`.

Voiceover: "The null matters because the detector uses an absolute decibel threshold, which makes it sensitive to how loud the file is. Normalising all sixteen files to minus 1 dBFS moves the within-recording P2-P3 difference by 0.25 seconds on average, and by 3.62 seconds in one recording. The effect I was measuring is 0.49 seconds. At this precision, a claim about which middle pause is longer is also a claim about file level and mastering."

Voiceover continuation: "This control reports aggregate metadata only. It does not rerun the selected event, and it does not let me pick a more favourable setting."

Caption: "`-1 dBFS`, `0.25 s average shift`, `3.62 s largest shift`, `0.49 s P2-P3 effect`."

## 2:10-3:05 -- The Ground-Truth Check

Screen: `MIDI/Audio Release Check` panel on the author-owned recording.

Action: step through P1, P2, P3, and P4, clicking `Show Event` after each dropdown change so the four gap values appear in turn.

Voiceover: "Everything so far rests on one unmeasured assumption: that where the energy falls below threshold is where the pianist stopped. On a piano it cannot be, because the strings keep ringing after the key is released."

Voiceover continuation: "So I recorded the Grave myself, capturing audio and MIDI. The MIDI note-off is the moment my finger left the key; the detector boundary is what the audio algorithm reports. Their difference is the error I could not see in the commercial recordings."

Voiceover continuation: "Across the four pauses the boundary lands between 0.056 and 0.188 seconds after the aligned note-off, about 0.11 seconds. It is late in every pause, which is what damped string decay predicts."

Voiceover continuation: "Two caveats. This is one performance by one pianist, excluded from the corpus statistics: a construct check, not a seventeenth recording. And the two files were not started on the same clock, so the pipeline declares a constant offset of 4.358 seconds, with about 30 milliseconds of uncertainty. That is the noise floor on a 0.11 second measurement."

Caption: "`+0.188 / +0.106 / +0.056 / +0.106 s`, `mean about 0.11 s`, `offset uncertainty about +/- 0.03 s`."

On-screen caption: "Author-owned recording. Excluded from corpus statistics."

## 3:05-3:28 -- What Reproduces, And What Does Not

Screen: repository README, at the reproduction section.

Voiceover: "The statistics and figures regenerate from the shipped CSVs with no audio. Regenerating the event table, the boundary table, or the waveform panels needs your own local copies, because the corpus recordings are commercial and are not redistributed. The one playable file is my own performance."

## 3:28-3:45 -- Close

Screen: return to the boundary overlay, select corrected P4 at `silence_start = 36.037 s`, click `Show Event`, play the last two seconds, then show the closing card.

Voiceover: "The contribution is a small, reproducible inspection interface for active silence, plus one measured estimate of how far an energy threshold sits from a real key release. The next step is to replace order-selected event recovery with score alignment, so the pauses are located by the score rather than by their position in time."

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

- Do a timed dry run of the voiceover alone before filming. If it exceeds 4:15, read the caption lines silently rather than cutting content.
- Record the browser window at 1920x1080 or higher.
- Use the hosted GitHub Pages page, not a `file://` URL.
- Use browser zoom around 110-125% if JSON or waveform labels are too small.
- Click `Show Event` after every dropdown change before narrating that event.
- Check each audio fragment before recording. The P1 fragment should contain playing, detected low energy, and the following attack, not room tone. Verified: 11.539 to 15.102 measures -14.8 dBFS mean, peak -0.3 dB.
- Do not include commercial audio.
- Do not describe the detector-performer discrepancy as a performance error. It is a property of the detector and the signal model.
- Export captions as WebVTT or burn them in. Include the spoken numbers; they carry the argument.
- Export as MP4, H.264 High, 1920x1080, CRF 20 or similar, AAC 128 kbps mono.
- Check the final runtime is under 5:00 with at least 20 seconds to spare.
