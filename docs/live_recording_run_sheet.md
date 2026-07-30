# Live Recording Run Sheet

Use this document while recording the demo video in one pass. It pairs each spoken line with the screen operation that should happen at the same time.

Target runtime: 3:45-4:15.

Demo page: https://haroldwangca.github.io/active-silence-pathetique/demo/

## Before Recording

1. Open the demo page in a clean browser window.
2. Set browser zoom to 110%. If the JSON text is still too small, use 125%.
3. Confirm the recording dropdown is on `HW_GRAVE_DEMO - Harold Wang (owned demo recording)`.
4. Confirm the pause dropdown is on `P1`.
5. Click `Show Event` once before starting the screen recording.
6. Test the audio once. P1 should include playing, a low-energy pause, and the following attack.
7. Open the repository README in a second tab:
   `https://github.com/haroldwangca/active-silence-pathetique`
8. Have the title card and closing card ready in your editor or slides.

## 0:00-0:18 -- Title Card, Then Question

Screen operation:

- Start on the title card for about 6 seconds.
- At about 0:06, cut to the live demo page with `HW_GRAVE_DEMO` and `P1` already loaded.
- Do not click yet. Let the viewer orient to the page.

Say:

> A written rest tells a pianist to stop. It does not tell them for how long. This demo measures what an energy-based detector finds inside four pauses in the Grave of the Pathetique, and how far that measurement sits from what the performer actually did.

Screen should show:

- Boundary overlay.
- `HW_GRAVE_DEMO`.
- `P1`.
- Ideally `silence_start = 14.722 s` somewhere visible.

## 0:18-0:48 -- What The Detector Reports

Screen operation:

- Click `Show Event`.
- Press play on the audio control.
- Let the P1 fragment play through the pause and next attack.
- Keep the boundary overlay visible while speaking.

Say while the audio finishes:

> Each pause is split into two spans. The blue span, `d_s`, is sounding time before the detector's threshold is crossed. The red span, `d_l`, is how long the signal stays below that threshold.

Say after the audio is done:

> For this pause, `d_l` is 0.380 seconds. Both are detector outputs. Neither is a measurement of musical intention, and that distinction matters.

On-screen caption:

```text
d_l = 0.380 s
```

If something goes wrong:

- If the audio does not play, click the audio control once, wait, and restart the sentence from "For this pause..."
- If the page looks unchanged, click `Show Event` again before speaking about P1.

## 0:48-1:30 -- The Result: The Hypothesis Was Not Supported

Screen operation:

- Scroll down to the trajectory figure.
- Keep the figure still; do not scroll while giving the statistical result.
- If possible, add the lower-third numbers during editing. If doing live captions, show them now.

Say:

> My hypothesis was that the second pause is systematically longest. Across sixteen professional recordings it is not supported. The longest pause falls at P2 in nine recordings and P3 in seven, a two-sided binomial p of 0.80.

Pause very briefly while the figure remains still.

Say:

> The paired P2-P3 difference is minus 0.49 seconds, ninety-five percent interval minus 1.42 to plus 0.43. It contains zero. Sixteen performances cannot separate these pauses, which is weaker than showing them equal, so I report a null.

Say:

> Across all four pauses the ordering is moderate, Kendall's W of 0.46. Remove P4 and W drops to 0.14, so the ordering is close to the single statement that the final caesura is shortest.

On-screen caption:

```text
9 of 16 / 7 of 16 · p = 0.80 · -0.49 s
95% CI [-1.42, +0.43] · W = 0.46 -> 0.14
```

On-screen note:

```text
Line groups are split post hoc by within-recording d_s/d_l covariance.
Exploratory descriptor, not a tested grouping.
```

If timing is tight:

- Do not read the on-screen note aloud.
- Keep the figure on screen and continue.

## 1:30-2:10 -- Why The Null Is The Interesting Part

Screen operation:

- Scroll to the threshold dropdown and sensitivity summary.
- Keep the label visible: `Aggregate threshold summary (does not re-run detection)`.
- Change the threshold dropdown once.
- Immediately click `Show Event`.

Say while changing the dropdown:

> The null matters because the detector uses an absolute decibel threshold, which makes it sensitive to how loud the file is.

Say after clicking `Show Event`:

> Normalising all sixteen files to minus 1 dBFS moves the within-recording P2-P3 difference by 0.25 seconds on average, and by 3.62 seconds in one recording. The effect I was measuring is 0.49 seconds.

Say:

> At this precision, a claim about which middle pause is longer is also a claim about file level and mastering. This control reports aggregate metadata only. It does not rerun the selected event, and it does not let me pick a more favourable setting.

On-screen caption:

```text
-1 dBFS · 0.25 s average shift · 3.62 s largest shift
0.49 s P2-P3 effect
```

If something goes wrong:

- If you forget to click `Show Event`, do it before saying "This control reports aggregate metadata only."
- If the dropdown is visually awkward, leave it alone and point verbally to the summary.

## 2:10-3:05 -- The Ground-Truth Check

Screen operation:

- Scroll to the `MIDI/Audio Release Check` panel.
- Stay on the author-owned recording.
- Start on P1.
- As you speak, step through P1, P2, P3, and P4.
- After every pause selection, click `Show Event`.

Say on P1:

> Everything so far rests on one unmeasured assumption: that where the energy falls below threshold is where the pianist stopped. On a piano it cannot be, because the strings keep ringing after the key is released.

Operation during the next sentence:

- Change to P2.
- Click `Show Event`.

Say:

> So I recorded the Grave myself, capturing audio and MIDI. The MIDI note-off is the moment my finger left the key; the detector boundary is what the audio algorithm reports.

Operation during the next sentence:

- Change to P3.
- Click `Show Event`.

Say:

> Their difference is the error I could not see in the commercial recordings. Across the four pauses the boundary lands between 0.056 and 0.188 seconds after the aligned note-off, about 0.11 seconds.

Operation during the next sentence:

- Change to P4.
- Click `Show Event`.

Say:

> It is late in every pause, which is what damped string decay predicts.

Say while holding P4:

> Two caveats. This is one performance by one pianist, excluded from the corpus statistics: a construct check, not a seventeenth recording.

Say:

> And the two files were not started on the same clock, so the pipeline declares a constant offset of 4.358 seconds, with about 30 milliseconds of uncertainty. That is the noise floor on a 0.11 second measurement.

On-screen caption:

```text
+0.188 / +0.106 / +0.056 / +0.106 s
mean about 0.11 s · offset uncertainty about +/- 0.03 s
```

On-screen note:

```text
Author-owned recording. Excluded from corpus statistics.
```

If something goes wrong:

- If the panel does not update, click `Show Event` and repeat the last half-sentence.
- If the timing feels rushed, skip saying the four individual numbers aloud and show them only in the caption.

## 3:05-3:28 -- What Reproduces, And What Does Not

Screen operation:

- Switch to the GitHub repository README tab.
- Scroll to the reproduction section or keep the file list visible if that is easier.
- Do not open any commercial audio files.

Say:

> The statistics and figures regenerate from the shipped CSVs with no audio. Regenerating the event table, the boundary table, or the waveform panels needs your own local copies, because the corpus recordings are commercial and are not redistributed. The one playable file is my own performance.

Screen should show one of:

- README reproduction instructions.
- Repository file list including `data`, `code`, `demo`, and `media`.
- The demo script or data files, if easier to frame.

## 3:28-3:45 -- Close

Screen operation:

- Return to the demo tab.
- Select `HW_GRAVE_DEMO`.
- Select P4.
- Click `Show Event`.
- Press play for the last short audible fragment.
- Cut to closing card.

Say over P4 and closing card:

> The contribution is a small, reproducible inspection interface for active silence, plus one measured estimate of how far an energy threshold sits from a real key release. The next step is to replace order-selected event recovery with score alignment, so the pauses are located by the score rather than by their position in time.

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

## One-Pass Survival Rules

- Every dropdown change needs a `Show Event` click. Treat dropdown then button as one motion.
- Keep the cursor still while saying statistical numbers.
- If you make a wording mistake, pause silently for one second and restart the sentence. That creates an easy edit point.
- If you are running long, stop reading captions aloud. Do not cut the methodological caveats.
- If the page fails to update, click `Show Event` again and keep going.
- Do not play commercial audio at any point.
- Do not describe any detector-performer mismatch as a performance mistake.

## Final Export

- Resolution: 1920x1080 or higher.
- Format: MP4, H.264 High.
- Audio: AAC mono, 128 kbps.
- Runtime: under 5:00, ideally 3:45-4:15.
- Captions: WebVTT or burned-in captions with the numerical claims.
