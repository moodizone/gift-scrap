# **Web Scraping Project**

This project is designed for collecting and storing data from websites as JSON files. The repository uses Python and various libraries to interact with web pages, extract data, and handle dynamic content such as JavaScript-rendered pages and lazy loading. It also supports downloading associated assets like images.

---

## **Features**

- Scrape product details such as title, description, price, images, and source.
- Handle dynamic web pages with Playwright.
- Download and store images locally.
- Save scraped data as JSON files.
- Configurable and easy-to-use folder structure.

---

## **Technologies Used**

- **Python 3.9+**
- **Requests**: For making HTTP requests.
- **BeautifulSoup4**: For parsing HTML and extracting data.
- **Playwright**: For handling dynamic pages and JavaScript interactions.
- **JSON**: For structured data storage.

---

## **Scripts**
Run as module:
```
python -m {path to python file in module order}
```
Watch mode (You have to import specific main script manually):
```
npm i -g nodemon 
nodemon --ignore data --exec src/entry.py
```

