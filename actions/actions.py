from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from actions.book_methods import InfoBook, CoverBook  # Import the classes
import json
import random


class ActionCaptureBookName(Action):
    def name(self):
        return "action_capture_book_name"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get('text')
        events = [SlotSet("book_name", user_input)]
        info_on_book = InfoBook.get_info_on_book(user_input)

        if info_on_book and info_on_book.get("docs") and info_on_book.get("numFound") != 0:
            book_info = info_on_book["docs"][0]
            author_name = book_info.get("author_name", ["N/A"])[0]
            first_publish_year = book_info.get("first_publish_year", "N/A")
            cover_edition_key = book_info.get("cover_edition_key", "N/A")

            response_message = self._prepare_book_response(user_input, author_name, first_publish_year)
            dispatcher.utter_message(text=response_message)  # Send the text response

            # Send the cover image if available
            if cover_edition_key and cover_edition_key != "N/A":
                cover_picture = CoverBook.get_cover_picture(cover_edition_key)  # Get the cover picture URL
                if cover_picture:  # Check if the cover picture URL is valid
                    dispatcher.utter_message(image=cover_picture)  # Send the cover image as a separate message

        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any information about that book.")

        return events  # Return the list of events

    def _prepare_book_response(self, book_title, author_name, publish_year):
        """Prepare the response message for the book information."""
        response_message = f"The book you picked is: {book_title}\n"
        response_message += f"This book was written by {author_name} and first published on {publish_year}.\n"
        return response_message  # Return the prepared response message


class ActionCaptureSubject(Action):
    def name(self):
        return "action_capture_subject"

    def run(self, dispatcher, tracker, domain):
        subject = tracker.latest_message.get('text')
        events = [SlotSet("subject", subject)]
        books_by_subject = InfoBook.get_books_by_subject(subject)

        if books_by_subject and books_by_subject.get("works"):
            # Get the list of works
            works = books_by_subject["works"]
            # Select 3 random books from the works
            selected_books = random.sample(works, min(3, len(works)))  # Ensure we don't sample more than available
            
            response_message = f"Here are some books on the subject of '{subject}':\n"
            image_urls = []  # List to collect image URLs
            
            for i, work in enumerate(selected_books):
                title = work.get("title", "N/A")
                cover_edition_key = work.get("cover_edition_key", "N/A")
                
                # Add the book title to the response message
                response_message += f"{i + 1}. {title}\n"
                
                if cover_edition_key and cover_edition_key != "N/A":
                    cover_picture = CoverBook.get_cover_picture(cover_edition_key)
                    if cover_picture:
                        image_urls.append(cover_picture)  # Collect the image URL

            # Send the response message with book titles
            dispatcher.utter_message(text=response_message)

            # Send the images as separate messages
            if image_urls:
                for url in image_urls:
                    dispatcher.utter_message(image=url)  # Send each image as a separate message
        
        else:
            dispatcher.utter_message(text="I'm sorry, I couldn't find any books for that subject.")

        return events  # Return the list of events, including the SlotSet event
    


class ActionCaptureAuthor(Action):
    def name(self):
        return "action_capture_author"

    def run(self, dispatcher, tracker, domain):
        author = tracker.latest_message.get('text')
        events = [SlotSet("author", author)]
        book_by_author_key = InfoBook.fetch_books_by_author(author)

        if book_by_author_key and book_by_author_key.get("entries"):
            # Get the list of entries
            entries = book_by_author_key["entries"]
            # Select 3 random books from the entries
            selected_books = random.sample(entries, min(3, len(entries)))
            response_message = f"Here are some books by {author}:\n"
            image_urls = []  # List to collect image URLs
            for i, entry in enumerate(selected_books):
                title = entry.get("title", "N/A")
                response_message += f"{i + 1}. {title}\n"
                info_on_book = InfoBook.get_info_on_book(title)

                if info_on_book and info_on_book.get("docs") and info_on_book.get("numFound") != 0:
                    cover_edition_key = info_on_book["docs"][0].get("cover_edition_key", "N/A")

                # Send the cover image if available
                if cover_edition_key and cover_edition_key != "N/A":
                    cover_picture = CoverBook.get_cover_picture(cover_edition_key)  # Get the cover picture URL
                    if cover_picture:  # Check if the cover picture URL is valid
                        image_urls.append(cover_picture)  # Collect the image URL

            if selected_books:
                # Send the response message with book titles
                dispatcher.utter_message(text=response_message)

                # Send the images as separate messages
                if image_urls:
                    for url in image_urls:
                        dispatcher.utter_message(image=url)  # Send each image as a separate message

            else:
                dispatcher.utter_message(text="I'm sorry, no books were found for this author.")

        else:
            dispatcher.utter_message(text="I'm sorry, no books were found for this author.")
        
        return events  # Return the list of events, including the SlotSet event


class ActionPopularBooks(Action):
    def name(self):
        return "action_recommend_popular_books"

    def run(self, dispatcher, tracker, domain):
        # Load the JSON file
        with open('books.json') as f:
            data = json.load(f)
            popular_books = data['popular_books']
        
        # Select 3 random books from the list
        selected_books = random.sample(popular_books, 3)
        
        # Create a message with the selected books
        message = "Here are some popular books:\n" + "\n".join([f"{i + 1}. {book['title']}" for i, book in enumerate(selected_books)])
        dispatcher.utter_message(text=message)

        # Send each book cover image
        for book in selected_books:
            dispatcher.utter_message(image=book['cover_link'])  # Send the cover image

        return []