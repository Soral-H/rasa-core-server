import requests

class InfoBook:
    BASE_URL_BOOK_NAME = "https://openlibrary.org/search.json?q="
    BASE_URL_SUBJECT = "https://openlibrary.org/subjects/"
    BASE_URL_AUTHOR_NAME = "https://openlibrary.org/search/authors.json?q="
    BASE_URL_AUTHOR_KEY = "https://openlibrary.org/authors/"

    @staticmethod
    def get_info_on_book(title: str):
        url_name = f"{InfoBook.BASE_URL_BOOK_NAME}{SplitFormatter.split(title, False)}"
        return InfoBook._make_request(url_name)

    @staticmethod
    def get_books_by_subject(subject: str):
        url_name = f"{InfoBook.BASE_URL_SUBJECT}{subject}.json"
        return InfoBook._make_request(url_name)

    @staticmethod
    def get_books_by_author_name(author: str):
        url_name = f"{InfoBook.BASE_URL_AUTHOR_NAME}{SplitFormatter.split(author, True)}"
        return InfoBook._make_request(url_name)

    @staticmethod
    def get_books_by_author_key(author_key: str):
        if not author_key or author_key == "N/A":
            return None  # Return None if the author key is invalid
        
        url_key = f"{InfoBook.BASE_URL_AUTHOR_KEY}{author_key}/works.json?limit=9"
        return InfoBook._make_request(url_key)

    @staticmethod
    def fetch_books_by_author(author: str):
        """Fetch books by author name and return the associated books."""
        author_info = InfoBook.get_books_by_author_name(author)
        if author_info and author_info.get("docs"):
            author_key = author_info["docs"][0].get("key", "N/A")
            return InfoBook.get_books_by_author_key(author_key)
        return None

    @staticmethod
    def _make_request(url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error retrieving data from {url}: {e}")
            return None

class CoverBook:
    @staticmethod
    def get_cover_picture(cover_edition_key: str):
        base_url_cover_edition_key = "https://covers.openlibrary.org/b/olid/"
        if cover_edition_key and cover_edition_key != "N/A":
            cover_picture = f"{base_url_cover_edition_key}{cover_edition_key}-M.jpg"
            return cover_picture
        return None

class SplitFormatter:
    @staticmethod
    def split(sentence: str, is_author: bool):
        if not sentence or sentence.strip() == "":
            return None
        return "%20".join(sentence.split()) if is_author else "+".join(sentence.split())
