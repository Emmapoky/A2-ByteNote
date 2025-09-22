from data_structures import ArrayR
from data_structures.hash_table_separate_chaining import HashTableSeparateChaining
from algorithms.insertionsort import insertion_sort
from processing_line import Transaction


class FraudDetection:
    def __init__(self, transactions: ArrayR):
        """
        :complexity: Best case is O(1) and worst case is O(1).
        
        We only store the reference to the provided ArrayR; no work scales with the
        number of transactions here.
        """
        self.transactions = transactions 

    def detect_by_blocks(self):
        """
        :complexity: O(N*L^2*log L), with N transactions and signature length L.
        
        We try every block size S (1..L). Per signature that means sorting B=⌊L/S⌋ blocks
        by insertion sort (~O(B^2·S)=O(L^2/S)); across N items and all S, this sums to O(N·L^2*log L).
        """
        first_sig = None
        for t in self.transactions:
            if first_sig is None:
                first_sig = t.signature
            N += 1
        if N == 0:
            return (1, 1)

        L = len(first_sig)
        best_S = 1
        best_score = 1
        S = 1
        while S <= L:
            groups = HashTableSeparateChaining(97)
            r = L - (L // S) * S
            B = L // S

            for t in self.transactions:
                sig = t.signature
                tail = "" if r == 0 else sig[L - r:L]

                blocks = ArrayR(B)
                i = 0
                while i < B:
                    start = i * S
                    blocks[i] = sig[start:start + S]
                    i += 1

                if B > 1:
                    insertion_sort(blocks)

                key = tail + "|"
                i = 0
                while i < B:
                    key = key + blocks[i] + "|"
                    i += 1

                # Increment group size
                try:
                    c = groups[key]
                    groups[key] = c + 1
                except KeyError:
                    groups[key] = 1

            # Compute suspicion score = product of all group sizes
            score = 1
            items = groups.items()  # ArrayR of (key, value) pairs (as 2-length arrays/tuples)
            i = 0
            while i < len(items):
                kv = items[i]
                score *= kv[1]
                i += 1

            if score > best_score:
                best_score = score
                best_S = S
            S += 1

        return (best_S, best_score)

    def rectify(self, functions: ArrayR):
        """
        :complexity: Per function f with table size T=max(f(tx))+1: best O(N+T), worst O(N+T^2).
        
        We hash all N once to build counts, then scan circular windows to find the worst
        probe chain—quick when windows break early (~T), quadratic in a packed worst case (~T^2).
        Sum per-function costs over all candidates..
        """
        # Count N once
        N = 0
        for _ in self.transactions:
            N += 1

        best_func = None
        best_mpcl = None

        for f in functions:
            vals = ArrayR(N)
            max_v = 0
            i = 0
            for t in self.transactions:
                v = f(t)
                vals[i] = v
                if v > max_v:
                    max_v = v
                i += 1

            T = max_v + 1
            if N > T:
                mpcl = T
            else:
                # Build counts per index
                counts = ArrayR(T)
                i = 0
                while i < T:
                    counts[i] = 0
                    i += 1

                i = 0
                while i < N:
                    idx = vals[i]
                    counts[idx] = counts[idx] + 1
                    i += 1

                mpcl = 0
                j = 0
                while j < T:
                    if counts[j] > 0:
                        cum = 0
                        tlen = 0
                        while tlen < T:
                            idx = (j + tlen) % T
                            cum += counts[idx]
                            if cum >= (tlen + 2):
                                tlen += 1
                                if tlen > mpcl:
                                    mpcl = tlen
                            else:
                                break
                    j += 1

            if (best_mpcl is None) or (mpcl < best_mpcl):
                best_mpcl = mpcl
                best_func = f

        return (best_func, best_mpcl)

if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    def to_array(lst):
        """
        Helper function to create an ArrayR from a list.
        """
        lst = [to_array(item) if isinstance(item, list) else item for item in lst]
        return ArrayR.from_list(lst)

    # Here is something to get you started with testing detect_by_blocks
    print("<------- Testing detect_by_blocks! ------->")
    # Let's create 2 transactions and set their signatures
    tr1 = Transaction(1, "Alice", "Bob")
    tr2 = Transaction(2, "Alice", "Bob")

    # I will intentionally give the signatures that would put them in the same groups
    # if the block size was 1 or 2.
    tr1.signature = "aabbcc"
    tr2.signature = "ccbbaa"

    # Let's create an instance of FraudDetection with these transactions
    fd = FraudDetection([tr1, tr2])

    # Let's test the detect_by_blocks method
    block_size, suspicion_score = fd.detect_by_blocks()

    # We print the result, hopefully we should see either 1 or 2 for block size, and 2 for suspicion score.
    print(f"Block size: {block_size}, Suspicion score: {suspicion_score}")

    # I'm putting this line here so you can find where the testing ends in the terminal, but testing is by no means
    # complete. There are many more scenarios you'll need to test. Follow what we did above.
    print("<--- Testing detect_by_blocks finished! --->\n")

    # ----------------------------------------------------------

    # Here is something to get you started with testing rectify
    print("<------- Testing rectify! ------->")
    # I'm creating 4 simple transactions...
    transactions = [
        Transaction(1, "Alice", "Bob"),
        Transaction(2, "Alice", "Bob"),
        Transaction(3, "Alice", "Bob"),
        Transaction(4, "Alice", "Bob"),
    ]

    # Then I create two functions and to make testing easier, I use the timestamps I
    # gave to transactions to return the value I want for each transaction.
    def function1(transaction):
        return [2, 1, 1, 50][transaction.timestamp - 1]

    def function2(transaction):
        return [1, 2, 3, 4][transaction.timestamp - 1]

    # Now I create an instance of FraudDetection with these transactions
    fd = FraudDetection(to_array(transactions))

    # And I call rectify with the two functions
    result = fd.rectify(to_array([function1, function2]))

    # The expected result is (function2, 0) because function2 will give us a max probe chain of 0.
    # This is the same example given in the specs
    print(result)
    
    # I'll also use an assert statement to make sure the returned function is indeed the correct one.
    # This will be harder to verify by printing, but can be verified easily with an `assert`:
    assert result == (function2, 0), f"Expected (function2, 0), but got {result}"

    print("<--- Testing rectify finished! --->")