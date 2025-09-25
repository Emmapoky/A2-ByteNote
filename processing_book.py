from data_structures import ArrayR
from data_structures.linked_stack import LinkedStack
from processing_line import Transaction

class ProcessingBook:
    LEGAL_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, level: int = 0):
        """
        :complexity: Best case is O(1) and worst case is O(1).
        We allocate a fixed 36-slot ArrayR for pages and initialise counters; the work
        does not depend on how many transactions will be stored later.
        """
        self._level = level  
        self.pages = ArrayR(len(ProcessingBook.LEGAL_CHARACTERS))
        i = 0
        while i < len(self.pages):
            self.pages[i] = None  
            i += 1
        self._size = 0
        self._errors = 0
    
    def page_index(self, character):
        """
        You may find this method helpful. It takes a character and returns the index of the relevant page.
        Time complexity of this method is O(1), because it always only checks 36 characters.

        :complexity: Best case is O(1) and worst case is O(1).
        We index within a fixed alphabet of 36 characters (a–z then 0–9).
        """
        return ProcessingBook.LEGAL_CHARACTERS.index(character)
    
    def get_error_count(self):
        """
        Returns the number of errors encountered while storing transactions.

        :complexity: Best case is O(1) and worst case is O(1).
        Returns the number of attempted updates that provided a different amount for an
        already-stored transaction; the stored amount is never changed.
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
        :complexity: Best case is O(1) where the destination page at this level is
        empty, so we place a leaf directly.

        Worst case is O(D), where D is the number of signature characters needed to
        disambiguate collisions (D larger or equal to L, the signature length). 
        We can descend through at most D nested books, doing O(1) work per level. 
        If the key already exists, we either do nothing (same amount) or increment 
        the error counter (different amount) without changing the stored value.
        """
        self._insert(tr, amount)

    def __getitem__(self, tr: Transaction):
        """
        :complexity: Best case is O(1) when the required entry is a leaf at this level.

        Worst case is O(D), where D is the depth to the unique leaf (D <= L). We follow
        at most one page per level until the leaf is reached; each level costs O(1).
        Raises KeyError if the transaction is not stored.
        """
        sig = tr.signature
        if sig is None:
            raise KeyError("Unsigned transaction")
        return self._get(sig)

    def __delitem__(self, tr: Transaction):
        """
        :complexity: Best case is O(1) when the page at this level contains exactly the
        leaf to delete.

        Worst case is O(D), where D is the depth to that leaf (D <= L). We go down (descend) 
        to the leaf and, on the way back up, perform at most one O(1) collapse check per level
        (empties and singletons) to keep the structure minimal. 

        Additionally, if the transaction is not stored it raises KeyError.
        """
        sig = tr.signature
        if sig is None:
            raise KeyError("Unsigned transaction")
        if not self._delete(sig):
            raise KeyError("Transaction not found")

    @staticmethod
    def _leaf(tr: Transaction, amount):
        pair = ArrayR(2)
        pair[0] = tr
        pair[1] = amount
        return pair
    
    def _insert(self, tr: Transaction, amount) -> bool:
        """
        :complexity: Best case is O(1) when the destination page at the current level
        is empty and we place a leaf.

        Worst case is O(D), where D is the number of signature characters required to
        separate colliding keys (D is less or equal to L). We create/delegate through 
        at most D nested books, performing only O(1) work per level.
        """
        sig = tr.signature
        idx = self.page_index(sig[self._level])
        slot = self.pages[idx]

        if slot is None:
            self.pages[idx] = ProcessingBook._leaf(tr, amount)
            self._size += 1
            return True

        if isinstance(slot, ProcessingBook):
            added = slot._insert_at_next(tr, amount)
            if added:
                self._size += 1  
            return added

        leaf_tr, leaf_amt = slot[0], slot[1]
        if leaf_tr.signature == sig:
            if leaf_amt != amount:
                self._errors += 1
            return False

        child = ProcessingBook(self._level + 1)
        child._insert_at_next(leaf_tr, leaf_amt)
        child._insert_at_next(tr, amount)
        self.pages[idx] = child
        self._size += 1
        return True
    
    def _insert_at_next(self, tr: Transaction, amount) -> bool:
        return self._insert(tr, amount)

    def _get(self, sig: str):

        idx = self.page_index(sig[self._level])
        slot = self.pages[idx]
        if slot is None:
            raise KeyError(sig)
        if isinstance(slot, ProcessingBook):
            return slot._get(sig)
        if slot[0].signature == sig:
            return slot[1]
        raise KeyError(sig)
    
    def _delete(self, sig: str) -> bool:
        """
       :complexity: Best case is O(1) when the target is a leaf in the current page.

        Worst case is O(D), where D is less or equal to L is the depth to that leaf. 
        We descend to the leaf and then possibly collapse an empty or singleton child 
        on the way back up, doing at most one O(1) check per level.
        """
        idx = self.page_index(sig[self._level])
        slot = self.pages[idx]
        if slot is None:
            return False 

        if isinstance(slot, ProcessingBook):
            removed = slot._delete(sig)
            if not removed:
                return False
            self._size -= 1
            if len(slot) == 0:
                self.pages[idx] = None
            elif len(slot) == 1:
                lone_tr, lone_amt = slot._extract_single_leaf()
                self.pages[idx] = ProcessingBook._leaf(lone_tr, lone_amt)
            return True

        if slot[0].signature != sig:
            return False
        self.pages[idx] = None
        self._size -= 1
        return True
    
    def _extract_single_leaf(self):
        """
        :complexity: Best case is O(1) if the single element is directly stored at this
        level.

        Worst case is O(H), where H is the current nesting height (H is less or equal to L). 
        We scan up to 36 fixed pages per level to find the unique non-empty slot, 
        then recurse once.
        """
        i = 0
        while i < len(self.pages):
            slot = self.pages[i]
            if slot is None:
                i += 1
                continue
            if isinstance(slot, ProcessingBook):
                return slot._extract_single_leaf()
            return slot[0], slot[1]
        raise KeyError("Empty subtree during extract")
    
    def __iter__(self):
        """
        :complexity: Best case is O(1) and worst case is O(1) to create the iterator.
        
        Traversal cost is paid lazily by successive next() calls. Items are yielded in
        page order (a..z then 0..9), depth-first across nested books.
        """
        stack = LinkedStack()
        frame = ArrayR(2)
        frame[0] = self
        frame[1] = -1
        stack.push(frame)

        class _Iterator:
            def __init__(self, st):
                self._stack = st

            def __iter__(self):
                return self

            def __next__(self):
                while len(self._stack) > 0:
                    fr = self._stack.pop()
                    b = fr[0]      
                    p = fr[1] + 1 

                    while p < len(b.pages) and b.pages[p] is None:
                        p += 1

                    if p >= len(b.pages):
                        continue

                    fr2 = ArrayR(2)
                    fr2[0] = b
                    fr2[1] = p
                    self._stack.push(fr2)

                    slot = b.pages[p]
                    if isinstance(slot, ProcessingBook):
                        child = ArrayR(2)
                        child[0] = slot
                        child[1] = -1
                        self._stack.push(child)
                        continue

                    return (slot[0], slot[1])

                raise StopIteration

        return _Iterator(stack)

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
