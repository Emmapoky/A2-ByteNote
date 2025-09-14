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

        :complexity: Best/Worst = O(1).

        maps a signature character to a page index using the fixed LEGAL_CHARACTERS order.
        """
        return ProcessingBook.LEGAL_CHARACTERS.index(character)
    
    def get_error_count(self):
        """
        Returns the number of errors encountered while storing transactions.

        :complexity: Best/Worst = O(1).

        In short, an error is counted when attempting to re-set a transaction that is already present
        with a different amount; the stored amount is not changed in that case.
        """
        return self._errors
    
    def __len__(self):
        """
        :complexity: Best case is O(1) and worst case is O(1).
        We maintain a subtree counter (_size) on every insert/delete, so returning it is
        constant time.
        """
        return self._size
    
    def __setitem__(self, tr: Transaction, amount):
        """
        :complexity: Best = O(1) if the destination page is empty at this level.
        Worst = O(D) where D is the number of additional characters needed to clearify
        colliding signatures (D ≤ L, the signature length).

        Behavior:
        - Insert a new leaf if the page is empty.
        - If the page already has a leaf with the same signature:
            - If amount is the same, do nothing.
            - If amount differs, increment _errors and keep the original amount.
        - If the page has a different leaf (signature collision), promote to a sub-book and
          insert both items at the next level.
        """
        self._insert(tr, amount)

    def __getitem__(self, tr: Transaction):
        """
        :complexity: Best = O(1) when the needed leaf is at this level.
        Worst = O(D) where D is the depth to the unique leaf along the trie path.

        Raises KeyError if the key is unsigned or not present in the structure.
        """
        sig = tr.signature
        if sig is None:
            raise KeyError("Unsigned transaction")
        return self._get(sig)

    def __delitem__(self, tr: Transaction):
        """
        :complexity: Best = O(1) when the leaf is at this level.
        Worst = O(D) where D is the depth to the leaf.

        Deletes the item if present and performs node cleanup on the way back up:
        - If a child sub-book becomes empty, replace the page with None
        - If a child sub-book becomes a singleton, collapse it into a leaf
        also raises KeyError if the key is unsigned or not found
        """
        sig = tr.signature
        if sig is None:
            raise KeyError("Unsigned transaction")
        if not self._delete(sig):
            raise KeyError("Transaction not found")

    @staticmethod
    def _leaf(tr: Transaction, amount):
        """
        Create a leaf node as ArrayR(2) = [Transaction, amount].
        Using ArrayR rather than Python tuples/lists aligns with the ADT constraints.
        """
        pair = ArrayR(2)
        pair[0] = tr
        pair[1] = amount
        return pair
    
    def _insert(self, tr: Transaction, amount) -> bool:
        """
        :complexity: Best = O(1) if this level's page is empty.
        Worst = O(D) (D ≤ L) as we create/descend into sub-books to disambiguate.

        Control flow:
        1) Empty page: place a leaf, ++ size, return True.
        2) Sub-book: delegate to child; if added there, increment size here.
        3) existing leaf:
           -> If the signature matches and amount differs: increment _errors, return False
           -> If the signature differs: allocate a sub-book at next level and re-insert both
        """
        sig = tr.signature
        idx = self.page_index(sig[self._level])
        slot = self.pages[idx]

        # case 1: empty page, place a leaf
        if slot is None:
            self.pages[idx] = ProcessingBook._leaf(tr, amount)
            self._size += 1
            return True

        # case 2: page already holds a sub-book, insert recursively at next level
        if isinstance(slot, ProcessingBook):
            added = slot._insert_at_next(tr, amount)
            if added:
                self._size += 1  # Bubble up size increase
            return added

        # case 3: page holds a leaf
        leaf_tr, leaf_amt = slot[0], slot[1]

        # if same signature exists, check amount consistency
        if leaf_tr.signature == sig:
            if leaf_amt != amount:
                # Do not overwrite -> record the conflict
                self._errors += 1
            return False

        # diff signature collided at this level then promote to a sub-book
        child = ProcessingBook(self._level + 1)

        # reinsert both the existing leaf and the new item into the sub-book
        child._insert_at_next(leaf_tr, leaf_amt)
        child._insert_at_next(tr, amount)

        # replace current page with the new sub-book and increase size by 1 (for the new item)
        self.pages[idx] = child
        self._size += 1
        return True
    
    def _insert_at_next(self, tr: Transaction, amount) -> bool:
        """
        a helper to insert at the next level; keeps the code centralized.
        """
        return self._insert(tr, amount)

    def _get(self, sig: str):
        """
        :complexity: Best = O(1) if the page holds the leaf here.
        Worst = O(D) following exactly one page per level until the leaf or a miss.

        On miss:
        - None page then is KeyError
        - Leaf with mismatched signature then KeyError is raise
        """
        idx = self.page_index(sig[self._level])
        slot = self.pages[idx]

        if slot is None:
            # Path does not exist
            raise KeyError(sig)

        if isinstance(slot, ProcessingBook):
            # Keep descending along the determined single page per level
            return slot._get(sig)

        # Found a leaf -> validate it's the correct signature
        if slot[0].signature == sig:
            return slot[1]

        # A different leaf sits here: not found
        raise KeyError(sig)
    
    def _delete(self, sig: str) -> bool:
        """
        :complexity: Best = O(1) if deleting a leaf at this level.
        Worst = O(D) to descend, then O(1) cleanup per level on the way back.

        Cleanup rules:
        - If child length drops to 0, remove the page (set to None)
        - If child length becomes 1, collapse the child into a single leaf to keep structure compact
        """
        idx = self.page_index(sig[self._level])
        slot = self.pages[idx]

        if slot is None:
            return False  # NTH to delete

        if isinstance(slot, ProcessingBook):
            # delegate deletion to child
            removed = slot._delete(sig)
            if not removed:
                return False

            # bubble up size decrement
            self._size -= 1

            # cleanup child after deletion
            if len(slot) == 0:
                # REMOVE empty sub-book
                self.pages[idx] = None
            elif len(slot) == 1:
                # collapse singleton sub-book to a leaf to avoid unnecessary depth
                lone_tr, lone_amt = slot._extract_single_leaf()
                self.pages[idx] = ProcessingBook._leaf(lone_tr, lone_amt)

            return True

        # page holds a leaf; delete only if signature matches
        if slot[0].signature != sig:
            return False

        self.pages[idx] = None
        self._size -= 1
        return True
    
    def _extract_single_leaf(self):
        """
        :complexity: Best = O(1) if the single element is a leaf at this level.
        Worst = O(H) scanning fixed 36 pages per level until finding the unique leaf,
        recursing at most once when the single child is itself a sub-book.
        """
        i = 0
        while i < len(self.pages):
            slot = self.pages[i]
            if slot is None:
                i += 1
                continue

            if isinstance(slot, ProcessingBook):
                # delegate to the only non-empty child
                return slot._extract_single_leaf()

            # found the single leaf directly
            return slot[0], slot[1]

        # should never happen if the caller verified length == 1
        raise KeyError("Empty subtree during extract")
    
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
