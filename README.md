[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/jarcokpahang5-ai/solmara-news-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/jarcokpahang5-ai/solmara-news-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# Solmara News — 26 November 2026

One image summing up the world news of Thursday 26 November 2026, drawn as a
newspaper front page. Entry for make.fun's News Image bounty ($100 in USDC).

The five stories on the page:

1. **US hikes tariffs on China, EU, Brazil and others** — the Trump
   administration unveils broad new tariffs on imports over subsidised
   factories (AP).
2. **Fuel tanker fire kills at least 30 in Cairo** — a fuel tanker crash
   sparks a massive highway blaze around the Egyptian capital (AP).
3. **Gaza strike kills a senior Hamas official** — an Israeli airstrike
   kills a senior Hamas official and his family (Reuters).
4. **Sudan drone strikes kill 19 civilians** — drone strikes hit Blue Nile
   state (Reuters).
5. **First Pakistani astronaut reaches Tiangong** — Pakistan's first
   astronaut joins China's space station aboard Shenzhou-24 (BBC).

## How it was made

`main.py` is pure Python 3.13 standard library — a hand-defined 5x7 bitmap
font and a hand-written PNG encoder (`struct` + `zlib`), no third-party
packages, no network, no randomness. It is fully deterministic: running it
twice writes byte-identical output.

```sh
python3.13 main.py   # writes entry.png (1024x1024)
```

`entry.png` is the generated front page (1024x1024, 16,611 bytes).
