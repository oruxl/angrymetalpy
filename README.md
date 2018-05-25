# AngryMetalPy

Python classes for representing reviews and reviewers from [AngryMetalGuy.com](AngryMetalGuy.com)

The provided script scrapes review data from the site and saves it to a text file.

This text file may be imported by library functions to build lists of reviews and reviewers. See the examples.

### TODO

- Make setup.py more usable
- Python3 compatibility (should work, but untested)
- Command line arguments for scraping tool

### Optional packages

- The scraping tool uses lxml and requests
- Matplotlib is used for plotting and data visualization
- Scipy for fitting and analysis

### Running the scraper

```
# first-time use (get everything! Takes a while...)
python amg_scrape.py

# subsequent use (only add new reviews to your data file)
python amg_scrape.py your_data_file_name.txt
```
