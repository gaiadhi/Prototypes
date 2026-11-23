# Soil Moisture Downscaling: Project Summary

## The goal

NASA's SME2 product gives soil moisture in 200 m squares. A grower needs finer detail than that. We used the sharper radar
images from the same NISAR satellite (10 m pixels) to estimate soil moisture in 100 m and 50 m squares, while always keeping
NASA's 200 m value as the anchor.

## 1. Preparing the data

**Lining the data up with NASA's grid.** The radar images arrived in three different map coordinate systems, because the
farm sits right on the boundary between two map zones. The SME2 file has no coordinates at all, only square numbers. We
brought both onto NASA's own map, EASE-Grid 2.0. Each radar pixel goes to latitude and longitude, then to EASE-Grid metres,
and drops into the 200 m square its centre falls in (NASA's "drop-in-bucket" method). The client's square centres go
through the same steps and land within half a metre of NASA's square centres. That is what ties the SME2 square numbers
to the radar pixels.

NASA's squares keep area, not shape. At this latitude a "200 m" square is about 185 m wide and 217 m tall on the ground,
with the same area as a 200 m square, so it still holds about 400 radar pixels.

**Checking the alignment on all six dates.**

- Pixel counts per square agree within a few percent across the three coordinate systems.
- The orchard edge drops brightness by about 10 dB at the same latitude on every date.
- Sliding each image against Feb 4 gives the best match at zero shift on every date, within 5 m.
- Even if every image were off by a whole pixel (10 m), the clean fallow squares would change by at most 0.14 dB, under
  0.003 m³/m³ of soil moisture.

**Keeping the ground clean.** The orchard edge runs 70% of the way down the second row of squares. We labelled each square
clean, mixed (partly orchard) or edge (under 80% covered by the image). Mixed squares look about 6 dB brighter than clean
fallow on the same day while NASA's moisture is only 0.02 higher, so trees, not water, cause most of that brightness.
Neither label uses NASA's moisture.

**Which records are used.** 20 squares × 6 dates = 120 records. 48 are clean: 24 fallow and 24 almond. The model learns
from the 24 clean fallow records only, and those four squares are the ones we map. The 60 fallow-row records (clean, mixed
and edge) are a stress test, not training data.

**Three features from the radar:**

- **HH brightness (HH_dB)**, the main moisture signal. Wetter soil reflects more radar energy, so it looks brighter.
- **HV brightness (HV_dB)**, the vegetation signal. It reacts mainly to plants and rough surfaces.
- **HV/HH ratio**, the vegetation discriminator. It is high for rough tree canopies and low for bare soil, which helps tell
  "bright because wet" apart from "bright because rough".

**Spatial anomalies.** On any one day, rain, temperature and the satellite's viewing angle affect the whole field at once.
To remove those day-wide effects, for each date we subtracted the field's average from every square, for the radar features
and for soil moisture. What is left is the pattern inside the field: which squares are wetter or drier than their neighbours
that day.

## 2. Two ways of training the models

We trained two common models, Ridge regression and Random Forest, in two ways:

- **Absolute prediction:** the model guesses the exact soil moisture from scratch.
- **Anomaly (delta) prediction:** the model only predicts how much wetter a square is than the field average on the same
  day.

Every test hid one whole date at a time, so the model was always judged on a day it had never seen, just like a new
satellite pass. The model settings were tuned on the training dates only. Each anomaly uses that same date's field average,
never other dates. To prove nothing leaked, we scrambled each hidden date's data: the slope learned without it did not move.

**What we found.** Guessing the exact moisture from scratch does not work on new dates: the absolute models miss by 0.049
to 0.061 m³/m³, three times worse than simply using the field's own NASA value (0.017). Radar alone cannot tell how wet the
whole field is on a new day. That is why the method starts from NASA's number and only adds the pattern inside the field.

## 3. Machine learning learns one number; NASA's equation does the downscaling

We did not use machine learning to predict the 50 m squares directly. The models have one job: to learn **β (beta)**, how
much soil moisture changes for every 1 dB of radar brightness. Ridge gives this slope directly. A Random Forest has no single
slope, so we fit a straight line through its predictions.

β then goes into NASA's own downscaling equation, taken from NASA's algorithm document for SME2:

> small-square moisture = NASA's 200 m moisture + β × (small square's brightness − 200 m square's brightness)

In plain words: start from NASA's number, then nudge each smaller square up if it is brighter than its 200 m square and down
if it is darker. A final small shift makes the smaller squares average back exactly to NASA's value.

## 4. Results

Each β was put into NASA's equation and tested on hidden dates, on the clean fallow squares:

| Where β came from | β across the hidden dates | Share of the pattern explained | Error vs no downscaling |
|---|---|---|---|
| Absolute, Ridge | 0.016 to 0.022 | 45% | 26% lower |
| Absolute, Random Forest | 0.013 to 0.022 | 45% | 26% lower |
| Anomaly, Random Forest | 0.003 to 0.011 | 24% | 13% lower |
| Anomaly, Ridge | 0.002 to 0.013 | 8% | 4% lower |

**The surprise:** the absolute models are bad at guessing soil moisture, but the slope they learn is the most stable and
works best. That slope comes from how the field gets wetter and drier over time, which is also how NASA learns β. The anomaly
slope depends heavily on one day (Mar 1, the day with the biggest differences between squares): when that day is hidden,
the slope almost disappears, because the squares barely differ on the other days.

**One day carries the gain.** Scored one hidden date at a time, the method beats "no downscaling" only on Mar 1, the one day
when the squares really differ. On the five uniform days the slope adds a pattern NASA does not show, mostly radar speckle.

**Ridge or Random Forest?** The Ridge and Random Forest slopes tie (45% each, three hidden dates each). A Random Forest given
only HH brightness scores a little higher on its own at 200 m (49%) and wins five of six dates, mostly by predicting almost
no pattern. On Mar 1 it finds only a third of the pattern, and its error is eight times Ridge's. We use Ridge's slope for the
maps for three reasons. A forest cannot predict beyond the brightest or darkest square it trained on, and 14% of the 50 m
squares fall outside that range. Ridge's slope moves less when a date is left out (14% against 19%). And NASA's equation is
itself a straight line.

**Clean ground matters.** Adding the mixed and edge squares weakens every method (8% to 27% explained), because orchard trees
and partial coverage add brightness that has nothing to do with moisture.

**Final maps:** β = 0.0171 from the absolute Ridge model trained on all clean data, giving 96 squares at 100 m and 384 at
50 m for each date. On the wettest, most varied date the maps sharpen a pattern NASA already shows; on the most uniform
dates much of the extra detail at 50 m is radar noise.

## 5. What we can and cannot claim

**We can claim:** on dates the model never saw, the method explains 45% of the pattern inside the field in NASA's data
over all six dates, almost all of it from the one varied date. It works best on clean fallow ground, and the maps always
agree with NASA at 200 m.

**We cannot claim yet:** that the 100 m and 50 m values match real measured soil moisture. There are no ground sensors at
those scales, and NASA's data comes from the same radar. Six dates is also a small sample, and it mixes morning and evening
passes, which give somewhat different slopes.

**Next steps:** more radar dates (NASA has 73), a separate β for each satellite pass, and soil probe readings at a few 50 m
squares for a first real-world check.
