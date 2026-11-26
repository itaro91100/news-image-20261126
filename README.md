[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/itaro91100/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/itaro91100/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# THE WORLD IN ONE PAGE — Thursday 26 November 2026

Entry for [make.fun **news-image-20261126**](https://make.fun/bounty/news-image-20261126):
"Sum up 26 November's world news in one image" ($100 in USDC, shared by the
top 50 entries).

`main.py` is a self-contained Python 3 program (standard library only — no
assets, no network, no dependencies) that draws a newspaper front page in
code and writes it to `entry.png`. The masthead names the day, **Thursday 26
November 2026**, and the page carries six stories from the day's news cycle,
checked against live coverage that morning:

- Russian drones kill 7 across six Ukrainian regions overnight; Kyiv hits
  three Russian refineries and the Savasleyka airbase in reply
- a petroleum tanker overturns and burns on Cairo's ring road; at least 31
  dead, 27 vehicles burned
- Trump unveils new tariffs aimed at excess factory capacity; stocks fall
  worldwide
- RSF drone strikes kill 19 civilians in Damazin, Blue Nile state, Sudan
- an Israeli dawn strike kills Hamas security chief Mohammed Abu al-Ouf,
  his wife and two daughters, 13 and 15 — the second senior security
  official killed in a day
- Pakistan's first astronaut, Muhammad Zeeshan Ali, flies aboard
  Shenzhou-24 and becomes the first foreigner on China's Tiangong station

The footer adds the rest of the day: Thanksgiving in the US, Colombia
marking 10 years since its peace deal, Bangladesh raising garment pay 36%,
BepiColombo due to shrink its Mercury orbit, and the UN tribunal finding the
UNRWA sackings rested on unproven claims.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs write byte-identical PNGs (1024×1024, 24 KB, well under the 1 MiB
cap). The program draws everything itself — a 5×7 bitmap font, vector
scenes for each story — so the image the grader renders is exactly the
image reviewed here, with no network at run time.

## Verification

Every fact on the page was checked against reporting of 25–26 November
2026 from Reuters, AP, The Guardian, Euronews, Xinhua and ESA/JAXA.
Nothing is invented: tolls are given as reported ("at least 31" in Cairo,
"19" in Damazin per the Emergency Lawyers count), and where a figure was
still preliminary the page does not present it as final. The Shenzhou-24
launch and docking, the overnight Ukraine strikes, the Cairo fire, the
Sudan strikes and the Gaza strike were all first reported on 25 November
and lead the morning editions of 26 November; BepiColombo's orbit-shrinking
manoeuvre and Thanksgiving fall on 26 November itself.

## Referral

Built for [make.fun](https://make.fun/r/vg0kgv1n) — join with referral code `vg0kgv1n`.

## License

MIT — see [LICENSE](LICENSE).
