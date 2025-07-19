# Optimal Play in Chopsticks
**This project is a work in progress.**

This is an independent research project, undertaken out of personal interest and curiosity. The repository is not a polished Python package, and the accompanying paper is incomplete and unreviewed. It contains exploratory ideas-many of which are rough or unfinished. The code reflects the development process and is not intended for reuse.

## Project Overview
This project explores the game of *Chopsticks*, a simple two-player hand game. The primary goal was to investigate whether there was a way to guarantee a win. To do so, I implemented a simple class for the game, and exhaustively searched the transition graph under optimal responses. We found no meaningful attractors beyond trivial terminal states, suggesting that the game may lack interesting long-run dynamics under best play.

---

## Background and Motivation
This project was a single late-night effort because I couldn't figure out if there was a way of forcing a win, I figured that the game would probably loop under perfect play but I wasn't sure. I figured that it wouldn't be that hard to do a quick search and the entire implementation and searh only took a few hours. I later cleaned the repository up because I thought the project was a nice bit of fun.

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/dbruwel/chopsticks-optimal-play.git
cd chopsticks-optimal-play
pip install -e .
```

---

## Repository Structure

```
chopsticks-optimal-play/
│
├── notebooks/                # Jupyter notebooks for exploration and results
│   └── *.ipynb
│
├── paper/                    # Draft paper, figures, and supplementary material
│   ├── main.pdf
│   └── ...
│
├── src/
│   └── chopsticks_optimal_play/
│       ├── __init__.py
│       └── ...
│
├── setup.py
├── pyproject.toml
└── README.md
```

---

## Disclamer
This is research-grade code, not a production package. It was completed over a few weeks to explore a specific question of interest. The project does not aim to be novel or comprehensive and was not initially intended for public release. It uses various freely available Python packages under open licenses.

---

## License

MIT License. See `LICENSE` for details.
