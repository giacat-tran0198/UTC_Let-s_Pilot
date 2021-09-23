"""Class definition for Pagination."""

from typing import List


class Pagination:
    DEFAULT_PAGE_SIZE = 10
    DEFAULT_PAGE_NUMBER = 1

    def __init__(self, total: int, pages: int, has_next: bool, has_prev: bool, next_: str, prev: str, data: List):
        self.has_prev = has_prev
        self.has_next = has_next
        self.prev = prev
        self.next = next_
        self.total = total
        self.pages = pages
        self.data = data
