from processing_line import Transaction
from data_structures import ArrayR


class FraudDetection:
    def __init__(self, transactions: ArrayR):
        """
        :complexity: Best case is O(1) and worst case is O(1).
        So we only store the reference to the provided ArrayR 
        No work scales with the number of transactions here.
        """
        self.transactions = transactions 

    def detect_by_blocks(self):
        """
        :complexity: O(N·L^2·log L), with N transactions and signature length L.
        We try every block size S (1..L); sorting B=⌊L/S⌋ blocks with insertion sort gives O(L^2/S),
        across all S this sums to O(N·L^2·log L).
        """
        # will be implemented in Part 3.2
        return (1, 1)

    def rectify(self, functions: ArrayR):
        """
        :complexity: Per function f with table size T=max(f(tx))+1: best O(N+T), worst O(N+T^2).
        """
        # will be implemented in Part 3.3
        return (None, 0)

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