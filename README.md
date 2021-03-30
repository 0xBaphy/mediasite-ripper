# Mediasite Ripper

I needed a way top download the contents from [this site](https://mediasite.osu.edu/Mediasite/Catalog/catalogs/fll-japanese)

First I went with Selenium, then I realized I was able to do it in a simpler way.

## Using it

- Create a python virtual enviroment:

```py
python -m venv .venv; source .venv/bin/activate
```

- Install the required libraries:

```py
python -m pip install aigpy request os shutil
```

- Run it:

```py
python main.py
```
