## Installation

### Option 1: Using Poetry (Recommended)

1. Make sure you have Poetry installed. If not, install it by following the instructions [here](https://python-poetry.org/docs/#installation).


2. Install dependencies using Poetry:
```bash
poetry install
```


### Option 2: Without Poetry

1. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv source venv/bin/activate # On Windows, use venv\Scripts\activate
```


2. Install dependencies:
```bash
pip install selenium-driverless hrequests[all] alive-progress
```


## Usage

The project consists of two main modules: `find_creators` and `get_creator`.

### Find Creators

This module allows you to search for creators based on a keyword.

To run the find_creators module:

python3 -m src.find_creators.main [options]


Options:
- `-k`, `--keyword`: Search keyword (required)
- `-t`, `--type`: Search type (default: "publication")
- `-r`, `--range`: Increase this value to capture more creators (default: 5)

Examples:
```bash
python3 -m src.find_creators.main -k "politics" -t "publication" -r 10 
python3 -m src.find_creators.main --keyword "science" --type "post" --range 15
```

Alternatively, you can set the arguments manually in the code. Open `src/find_creators/main.py` and uncomment and modify lines 18-21:

```python
# args.keyword = "jujutsu kaisen"
# args.type = "publication"
# args.range = 15
```


### Get Creator

This module allows you to get detailed information about a specific creator.

To run the get_creator module:

python3 -m src.get_creator.main [options]


Options:
- `-u`, `--url`: Creator's URL (default: "https://website.com/@jonathanhaidt")

Examples:
```bash
python3 -m src.get_creator.main -u "https://website.com/@yourguru" 
python3 -m src.get_creator.main --url "https://website.com/@specificcreator"
```

Alternatively, you can set the URL manually in the code. Open src/get_creator/main.py and uncomment and modify lines 14-15:

```python
# args.url = "https://website.com/@jonathanhaidt"
```


## Functions

### `start_driver()`
Initializes and returns a Selenium WebDriver instance with specific options.

### `get_creator_page_infos(driver, url)`
Retrieves basic information about a creator's page.

### `get_headers_and_pubid(driver, blog_url, keyword=None)`
Retrieves necessary headers and publication ID for API requests.

### `save_to_csv(data, filename, headers)`
Saves the scraped data to a CSV file.

## Output

The scraped data will be saved in CSV format:
- For `find_creators`: `src/find_creators/creators.csv`
- For `get_creator`: `src/get_creator/creator.csv`

## Notes

- Make sure you have Chrome installed on your system as the scraper uses ChromeDriver.
- The scraper uses Selenium in headless mode by default. To run with a visible browser, uncomment the relevant line in the `start_driver()` function in `utils.py`.