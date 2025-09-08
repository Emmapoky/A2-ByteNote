from data_structures.referential_array import ArrayR
from data_structures.linked_queue import LinkedQueue
from data_structures.linked_stack import LinkedStack

class Transaction:
    def __init__(self, timestamp, from_user, to_user):
        # Here we basically store metadata used by ProcessingLine along w/ signature generation
        self.timestamp = timestamp
        self.from_user = from_user
        self.to_user = to_user
        self.signature = None
    # Rmb these are constants for signature GENERATION make more
    _SIG_LEN = 36  # fixed-signature len is 36
    _ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789" #t he alphabet
    _MODULUS = 36 ** _SIG_LEN #base^len 
    
    def sign(self):
        """
        :complexity: Best = Worst = O(S + R + L), where S = len(from_user),
        R = len(to_user), and L is the fixed signature length.
        
        This is because, under the assignment assumptions, arithmetic/bit ops 
        are O(1), so nothing else affects the cost.
        """
        h = 0x9E3779B185EBCA87 # large odd constant reduce collisions - "Golden Rattio Hashing" "Fibonacci Hashing" from DM
        h ^= self.timestamp * 0xC2B2AE3D27D4EB4F # now mix timestamp into teh accumilator  
        # Mix fromuser characters one by o1ne - O(1) each
        i = 0 
        u = self.from_user
        while i < len(u):
            h = (h * 1315423911) ^ (ord(u[i]) * 16777619) # *-then-xor mixing pattern
            h ^= (h >> 13)  # now do right-shift xor to mix + bits into - (low) bits
            i += 1 
        h = (h * 1469598103934665603) ^ ord('|') # now use delimiter to separate the 2 names in the stiring stream

        j = 0  # combine to-user chars with a sim. pattern using diff. constants
        v = self.to_user
        while j < len(v):
            # use diff multiplier sequence to REDUCE structured alignment
            h = (h * 2166136261) ^ (ord(v[j]) * 1099511628211)
            h ^= (h >> 11)
            j += 1
        # lasst delimiter and shifts to smear the state 
        h = (h * 1469598103934665603) ^ ord('>')

        h ^= (h << 7)
        h ^= (h >> 17)
        h ^= (h << 31)

        if h < 0: # make sure it is a non-negative value before modulo, avoids Py - mod issues
            h = -h

        # encode to fixed-width base-36 using ArrayR to lisren to ADT constraints
        L = Transaction._SIG_LEN 
        x = h % Transaction._MODULUS
        chars = ArrayR(L) # temp buffer for characters
        k = L - 1
        while k >= 0:
            chars[k] = Transaction._ALPHABET[x % 36]
            x //= 36
            k -= 1
        s = "" # build final Py string WITHOUT using lists
        k = 0
        while k < L:
            s += chars[k]
            k += 1
        self.signature = s # RMb store the signature for future re-use

class ProcessingLine:
    def __init__(self, critical_transaction):
        """
        :complexity: Best case is O(1).

        Keep 3 REF/STRUCTURES:
        - _critical: the single critical Transaction - output in the middle
        - _before: LinkedQueue for all transactions w timestamp <= critical
        - _after: LinkedStack for all transactions w/ timestamp > critical

        2 flags control mutation:
        1- _locked: set to True once iteration starts (blocks add_transaction)
         2- _iter_created: ensures only 1 iterator may ever be created
        """
        self._critical = critical_transaction
        self._before = LinkedQueue()
        self._after = LinkedStack()
        self._locked = False
        self._iter_created = False

    def add_transaction(self, transaction):
        """
        :complexity: Best = Worst = O(1).

        Adds a transaction to the queue (<= critical) or to the stack (> critical).
        If the line is locked (iteration started), raise sRuntimeError to preserve
        deterministic ordering and immutability during processing.
        """
        if self._locked:
            raise RuntimeError("ProcessingLine is locked; cannot add transactions.")

        # using partition by timestamp relative to the CRITICAL transaction
        if transaction.timestamp <= self._critical.timestamp:
            # FIFO for items before or = to critical
            self._before.append(transaction)
        else:
            # LIFO for items ONLY after critical
            self._after.push(transaction)

    class _Iterator:
        def __init__(self, line):
            # THIS Iterator class holds a ref to the line and a flag to emit the critical once
            self._line = line
            self._gave_critical = False

        def __iter__(self):
            return self

        def __next__(self):
            """
            :complexity: Best case O(1); worst case O(S + R + L) if signing is needed.

            So Emission order is:
            1) All <= critical in FIFO (we serve from queue).
            2) The single critical transaction.
            3) All > critical in LIFO (we pop from stack).

            Each time a transaction is about to be returned, sign it if needed
            (LAZY signing ENSURES O(1) path when already signed).
            """
            # emmit all queued transactions with timestamp <= critical in FIFO order
            if len(self._line._before) > 0:
                tx = self._line._before.serve()
                if tx.signature is None:
                    tx.sign()  # Lazy computation of signature
                return tx

            # emit the critical transaction exactly once
            if not self._gave_critical:
                self._gave_critical = True
                tx = self._line._critical
                if tx.signature is None:
                    tx.sign()
                return tx

            # emit transactions after the critical in LIFO order
            if len(self._line._after) > 0:
                tx = self._line._after.pop()
                if tx.signature is None:
                    tx.sign()
                return tx

            # nth left to emit
            raise StopIteration

    def __iter__(self):
        """
        :complexity: Best/Worst = O(1).

        ENCOURAGES single-iterator semantics: the first call locks the line and
        returns a lightweight iterator; subsequent calls raise RuntimeError.
        Basically, this guarantees immutability during iteration and consistent ordering.
        """
        if self._iter_created:
            raise RuntimeError("An iterator already exists; processing has started.")
        self._iter_created = True
        self._locked = True
        return ProcessingLine._Iterator(self)

if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    # Here's something to get you started...
    transaction1 = Transaction(50, "alice", "bob")
    transaction2 = Transaction(100, "bob", "dave")
    transaction3 = Transaction(120, "dave", "frank")

    line = ProcessingLine(transaction2)
    line.add_transaction(transaction3)
    line.add_transaction(transaction1)

    print("Let's print the transactions... Make sure the signatures aren't empty!")
    line_iterator = iter(line)
    while True:
        try:
            transaction = next(line_iterator)
            print(f"Processed transaction: {transaction.from_user} -> {transaction.to_user}, "
                  f"Time: {transaction.timestamp}\nSignature: {transaction.signature}")
        except StopIteration:
            break