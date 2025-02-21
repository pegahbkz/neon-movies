# Neon Films
Analysing audience preferences for movies

## Table of Contents

## Installation

Clone the repository:

```sh
git clone https://github.com/pegahbkz/neon-movies.git
cd neon-movies
```

## Install Dependencies:

```sh
pip install pandas numpy matplotlib seaborn requests tqdm trendspy openpyxl python-dateutil
```

## Usage

Run the Script:

```sh
python neon-films.py
```


## Automate with CRON Jobs:

To automate the script, add a cron job:

```sh
crontab -e
```

Then add

```sh
0 0 * * 1 /usr/bin/python3 /path/to/main.py
```

