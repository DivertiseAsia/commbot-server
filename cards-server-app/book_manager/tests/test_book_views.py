# """
# Book Manager's Book Views
# """

from rest_framework.reverse import reverse

from config.helpers import BaseTestCase
from ..models import Author, Book


class TestBookViews(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.book_rabbit_and_turtle = self.create_object({"title": "Rabbit and Turtle"})
        self.book_rapunzel = self.create_object({"title": "Rapunzel"})
        self.book_cinderella = self.create_object({"title": "Cinderella"})

        self.author_aesop = self.create_author({"name": "Aesop"})
        self.author_brothers_grimm = self.create_author({"name": "Brothers Grimm"})

        self.author_aesop.books.add(self.book_rabbit_and_turtle)
        self.author_brothers_grimm.books.add(self.book_rapunzel, self.book_cinderella)

    @staticmethod
    def create_object(details):
        return Book.objects.create(**details)

    @staticmethod
    def create_author(details):
        return Author.objects.create(**details)

    @staticmethod
    def get_url_reverse(view_path, version=1):
        return reverse(f"v{version}:books-{view_path}")

    def given_page_query_param(self, page):
        self.given_query_params({"page": page})

    def assertResponsePagination(self):
        self.assertIn("count", self.response_json)
        self.assertIn("next", self.response_json)
        self.assertIn("previous", self.response_json)
        self.assertIn("results", self.response_json)

    def assertResponseResultKeys(self, result_json):
        self.assertIn("id", result_json)
        self.assertIn("title", result_json)
        self.assertIn("authors", result_json)
        self.assertIn("created_at", result_json)

    def assertTitleOrdering(self, response_json, expected_book):
        self.assertEqual(expected_book.title, response_json["title"])

    def test_get_book_list_with_page_negative_one_would_return_results_without_pagination(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(-1)

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertNotIn("count", self.response_json)
        self.assertNotIn("next", self.response_json)
        self.assertNotIn("previous", self.response_json)
        self.assertNotIn("results", self.response_json)
        self.assertResponseResultKeys(self.response_json[0])
        print(">> test_get_book_list_with_page_negative_one_would_return_results_without_pagination: OK <<")

    def test_get_book_list_without_page_query_param(self):
        self.given_url(self.get_url_reverse("list"))

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertResponsePagination()
        self.assertResponseResultKeys(self.response_json["results"][0])
        print(">> test_get_book_list_without_page_query_param: OK <<")

    def test_get_book_list_with_valid_page(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(1)

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertResponsePagination()
        self.assertResponseResultKeys(self.response_json["results"][0])
        print(">> test_get_book_list_with_valid_page: OK <<")

    def test_get_book_list_with_invalid_page_0(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(0)

        self.when_user_gets_json()

        self.assertResponseNotFound()
        print(">> test_get_book_list_with_invalid_page_0: OK <<")

    def test_get_book_list_with_invalid_page(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(10000)

        self.when_user_gets_json()

        self.assertResponseNotFound()
        self.assertEqual(self.response_json["detail"], "Invalid page.")
        print(">> test_get_book_list_with_invalid_page: OK <<")

    def test_get_book_list_of_bros_grimm_with_page_1(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(1)
        self.query_params.update({"authors__name__icontains": "grimm"})

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertResponsePagination()
        results_json = self.response_json["results"]
        self.assertResponseResultKeys(results_json[0])
        for result in results_json:
            self.assertIn(self.author_brothers_grimm.name, result["authors"])
        print(">> test_get_book_list_of_bros_grimm_with_page_1: OK <<")

    def test_get_book_list_of_title_ra_with_page_1(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(1)
        self.query_params.update({"title__icontains": "Ra"})

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertResponsePagination()
        response_titles = [result["title"] for result in self.response_json["results"]]

        self.assertIn(self.book_rabbit_and_turtle.title, response_titles)
        self.assertIn(self.book_rapunzel.title, response_titles)
        self.assertNotIn(self.book_cinderella.title, response_titles)
        print(">> test_get_book_list_of_title_ra_with_page_1: OK <<")

    def test_get_book_list_ordering_title_asc_with_page_1(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(1)
        self.query_params.update({"ordering": "title"})

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertResponsePagination()
        response_results = self.response_json["results"]

        self.assertTitleOrdering(response_results[0], self.book_cinderella)
        self.assertTitleOrdering(response_results[1], self.book_rabbit_and_turtle)
        self.assertTitleOrdering(response_results[2], self.book_rapunzel)
        print(">> test_get_book_list_ordering_asc_with_page_1: OK <<")

    def test_get_book_list_ordering_title_desc_with_page_1(self):
        self.given_url(self.get_url_reverse("list"))
        self.given_page_query_param(1)
        self.query_params.update({"ordering": "-title"})

        self.when_user_gets_json()

        self.assertResponseSuccess()
        self.assertResponsePagination()
        response_results = self.response_json["results"]

        self.assertTitleOrdering(response_results[0], self.book_rapunzel)
        self.assertTitleOrdering(response_results[1], self.book_rabbit_and_turtle)
        self.assertTitleOrdering(response_results[2], self.book_cinderella)
        print(">> test_get_book_list_ordering_title_desc_with_page_1: OK <<")
