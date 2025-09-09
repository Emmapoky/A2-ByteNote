from data_structures import ArrayR

from processing_line import Transaction


class ProcessingBook:
    LEGAL_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789" # isa fixed alphabet that defines the 36 page slots at EVRY level 

    # def __init__(self):
    #     self.pages = ArrayR(len(ProcessingBook.LEGAL_CHARACTERS))
    def __init__(self, level: int = 0):
        """
        :complexity: Best/Worst = O(1).

        This structure acts like a trie over base-36 characters of a transaction's
        signature. Each node holds 36 pages that are either:
          -> None (empty page)
          -> a leaf (ArrayR(2) with [Transaction, amount])
          -> orr another ProcessingBook (sub-trie) for deeper clarification
        """
        self._level = level  # which char of the signature is used at this node

        # Allocate EXACTLY 36 slots
        self.pages = ArrayR(len(ProcessingBook.LEGAL_CHARACTERS))
        i = 0
        while i < len(self.pages):
            self.pages[i] = None  # start with all pages empty
            i += 1

        # so _size counts how many leaf entries exist in this subtree
        self._size = 0

        # -> _errors counts conflicting re-sets where the amount differs for an EXISTING key
        self._errors = 0
    
    def page_index(self, character):
        """
        You may find this method helpful. It takes a character and returns the index of the relevant page.
        Time complexity of this method is O(1), because it always only checks 36 characters.
        """
        return ProcessingBook.LEGAL_CHARACTERS.index(character)
    
    def get_error_count(self):
        """
        Returns the number of errors encountered while storing transactions.
        """
        pass
    
    def __len__(self):
        pass
    
    def sample(self, required_size):
        """
        1054 Only - 1008/2085 welcome to attempt if you're up for a challenge, but no marks are allocated.
        Analyse your time complexity of this method.
        """
        pass


if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.

    # Let's create a few transactions
    tr1 = Transaction(123, "sender", "receiver")
    tr1.signature = "abc123"

    tr2 = Transaction(124, "sender", "receiver")
    tr2.signature = "0bbzzz"

    tr3 = Transaction(125, "sender", "receiver")
    tr3.signature = "abcxyz"

    # Let's create a new book to store these transactions
    book = ProcessingBook()

    book[tr1] = 10
    print(book[tr1])  # Prints 10

    book[tr2] = 20
    print(book[tr2])  # Prints 20

    book[tr3] = 30    # Ends up creating 3 other nested books
    print(book[tr3])  # Prints 30
    print(book[tr2])  # Prints 20

    book[tr2] = 40
    print(book[tr2])  # Prints 20 (because it shouldn't update the amount)

    del book[tr1]     # Delete the first transaction. This also means the nested books will be collapsed. We'll test that in a bit.
    try:
        print(book[tr1])  # Raises KeyError
    except KeyError as e:
        print("Raised KeyError as expected:", e)

    print(book[tr2])  # Prints 20
    print(book[tr3])  # Prints 30

    # We deleted T1 a few lines above, which collapsed the nested books.
    # Let's make sure that actually happened. We should be able to find tr3 sitting
    # in Page A of the book:
    print(book.pages[book.page_index('a')])  # This should print whatever details we stored of T3 and only T3
