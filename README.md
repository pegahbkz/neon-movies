# Project Title
Neon Films Audience Movie Preference Analysis
## Table of Contents

## Installation

Clone the repository:

```sh
git clone https://github.com/yourusername/movie-data-automation.git
cd movie-data-automation
```

## Install Dependencies:

```sh
pip install pandas numpy matplotlib seaborn requests tqdm trendspy openpyxl python-dateutil
```

## Usage

Run the Script:

```sh
python main.py
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

