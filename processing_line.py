from data_structures.referential_array import ArrayR
from data_structures.linked_queue import LinkedQueue
from data_structures.linked_stack import LinkedStack

class Transaction:
    def __init__(self, timestamp, from_user, to_user):
        self.timestamp = timestamp
        self.from_user = from_user
        self.to_user = to_user
        self.signature = None

    _SIG_LEN = 36  
    _ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789" 
    _MODULUS = 36 ** _SIG_LEN 
    
    def sign(self):
        """
        :complexity: Best = Worst = O(S + R + L), where S = len(from_user),
        R = len(to_user), and L is the fixed signature length.
        
        This is because, under the assignment assumptions, arithmetic/bit ops 
        are O(1), so nothing else affects the cost.
        """
        h = 0x9E3779B185EBCA87 
        h ^= self.timestamp * 0xC2B2AE3D27D4EB4F 
   
        i = 0 
        u = self.from_user
        while i < len(u):
            h = (h * 1315423911) ^ (ord(u[i]) * 16777619)
            h ^= (h >> 13) 
            i += 1 
        h = (h * 1469598103934665603) ^ ord('|')

        j = 0 
        v = self.to_user
        while j < len(v):
           
            h = (h * 2166136261) ^ (ord(v[j]) * 1099511628211)
            h ^= (h >> 11)
            j += 1

        h = (h * 1469598103934665603) ^ ord('>')

        h ^= (h << 7)
        h ^= (h >> 17)
        h ^= (h << 31)

        if h < 0: 
            h = -h

     
        L = Transaction._SIG_LEN 
        x = h % Transaction._MODULUS
        chars = ArrayR(L) 
        k = L - 1
        while k >= 0:
            chars[k] = Transaction._ALPHABET[x % 36]
            x //= 36
            k -= 1
        s = "" 
        k = 0
        while k < L:
            s += chars[k]
            k += 1
        self.signature = s 

class ProcessingLine:
    def __init__(self, critical_transaction):
        """
        :complexity: Best case is O(1).
        Best case happens because we only store references and construct empty
        provided ADTs (a queue for ≤ critical and a stack for > critical).

        Worst case is O(1).
        It's O(1) because no work scales with the number of transactions; so we 
        just initialise fields and empty structures.
        """
        self._critical = critical_transaction
        self._before = LinkedQueue()
        self._after = LinkedStack()
        self._locked = False
        self._iter_created = False

    def add_transaction(self, transaction):
        """
        :complexity: Best = Worst = O(1).

        This is because we do a single timestamp comparison and one O(1) operation on the
        appropriate ADT (enqueue to the queue or push to the stack). If the line
        is locked, raising RuntimeError is also O(1).
        """
        if self._locked:
            raise RuntimeError("ProcessingLine is locked; cannot add transactions.")
        if transaction.timestamp <= self._critical.timestamp:
            self._before.append(transaction)
        else:
            self._after.push(transaction)

    class _Iterator:
        def __init__(self, line):
            self._line = line
            self._gave_critical = False

        def __iter__(self):
            return self

        def __next__(self):
            """
            :complexity: Best case is O(1).
            Best case happens when the next transaction is already signed and sits
            at the front/top of the respective ADT: so we just need to perform 
            a single O(1) serve (queue) or pop (stack) and return it without signing cost.

            Worst case is O(S + R + L) where S = len(tx.from_user),
            R = len(tx.to_user), and L is the fixed signature length.
            It's O(S + R + L) because if the next transaction is unsigned we first
            perform the same O(1) ADT operation (serve/pop) and then call sign(),
            which scans usernames once and writes exactly L base-36 characters.
            """
            # Emit <= critical in FIFO order
            if len(self._line._before) > 0:
                tx = self._line._before.serve()
                if tx.signature is None:
                    tx.sign()  
                return tx

            # Then the critical, once
            if not self._gave_critical:
                self._gave_critical = True
                tx = self._line._critical
                if tx.signature is None:
                    tx.sign()
                return tx

            # Then > critical in LIFO order
            if len(self._line._after) > 0:
                tx = self._line._after.pop()
                if tx.signature is None:
                    tx.sign()
                return tx

            # Done
            raise StopIteration

    def __iter__(self):
        """
        :complexity: Best case is O(1).
        Best case happens when no iterator exists yet: we set two flags (lock the
        line and mark the iterator as created) and return a lightweight iterator.

        Worst case is O(1).
        It's O(1) because even in the error path we only check a boolean and raise
        RuntimeError so no data-structure traversal occurs.
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