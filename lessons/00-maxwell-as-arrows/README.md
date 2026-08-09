# Chapter 0 — Maxwell as Arrows (pre-course, optional)

Qualitative electromagnetics: reading Maxwell's equations for directions and
topology before calculating anything. Six questions, answered by hand and
confirmed by reproducible numbers. Recommended for students whose EM course is
a few years behind them; skippable if div, curl, Poynting, and field-line
reasoning are fresh.

- **Read:** [tour.en.md](tour.en.md) · 中文版 [tour.zh-hant.md](tour.zh-hant.md) (~40 minutes)
- **Reproduce every number:** `python tour_numbers.py all` (or one section:
  `python tour_numbers.py 0.4`)
- **Regenerate every figure:** `python tour_figures.py`

Unlike lectures 1–16 this chapter has no lab, no slides, no homework, and no
scikit-rf — numpy (plus scipy's Bessel functions in §0.6) is the whole stack.
Format follows the optimizations course's `00-wind-tour` precedent: figures are
committed to the repo (they are content, not lab byproducts). Both language
versions carry identical measured numbers; the zh-Hant text is parallel
content per course convention, not a literal translation.
