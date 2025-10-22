**FIT1008 A2a : Tasks 1–3 README (ONLY FOR REVIEWER TO READ)**
Hello, this document is confidential and intended only for the assessment and the unit staff for FIT1008 

**Overview**
- This project implements a transaction processing line (Task 1), a page‑trie processing book (Task 2), and fraud analysis utilities (Task 3) using only the provided ADTs and within the scaffold constraints.​
- My code avoids restricted Python features and keeps logic inside the allowed files with optional small tests under if name == "main".​
- Each task is aligned to the unit’s data structures and complexity wants.​

**Files and roles**
> processing_line.py - Transaction signing and ordered iteration around a critical pivot (Task 1).​
> processing_book.py - Base‑36 page trie for storing (Transaction, amount) with collision disambiguation (Task 2).​
> fraud_detection.py — Block‑based grouping and hash rectification over transactions (Task 3).​

**Constraints and design choices**
> I USED: ArrayR, LinkedQueue, LinkedStack, HashTableSeparateChaining, and insertion_sort 
> ALL from the scaffold; avoids lists/dicts/sets/yield/built‑in sort in solution paths.​
> ALL interfaces and behaviors follow the scaffold EXACTLY to ensure compatibility with unit tests.​

**SUMMARY OF EACH TASK**

**Task 1: Processing Line**
> Transaction.sign mixes timestamp and usernames, it then emits a fixed 36‑char base‑36 signature using ArrayR only.​
> add_transaction partitions by timestamp into a queue (≤ critical) or stack (> critical) and locks once iteration begins.​
> Iteration order is FIFO before, then the single critical, then LIFO after; signatures are computed lazily on first emission.​

**Task 2: Processing Book**
> A 36‑page trie keyed by signature characters: page holds None, a leaf [Transaction, amount], or a nested ProcessingBook.​
> setitem inserts a leaf, promotes to a sub‑book on collision, and records an error if a different amount is re‑set for the same signature.​
> getitem/delitem/iter follow exactly one path per level, collapse empty/singleton children after deletes, and traverse with an explicit stack.​

**Task 3 — Fraud Detection**
> detect_by_blocks tries block sizes 1..L, sorts per‑signature blocks, groups by tail+sorted‑blocks key, and returns the block size with the highest suspicion score.​
> rectify evaluates candidate hash functions, counts indices up to T=max(f(tx))+1, it scans circular windows to find max probe chain length, and picks the function with minimal chain.​
> Both methods operate over an ArrayR of transactions and use only provided ADTs/algorithms.​

**COMPLEXITIES**
Task 1: sign is O(S+R+L); adding is O(1); iterator step is best O(1), worst O(S+R+L).
Task 2: inserts/lookups/deletes are best O(1), worst O(D) where D<=L; single‑leaf extract is best O(1), worst O(H)
Task 3: detect_by_blocks is O(N*L^2*logL); rectify per function is best O(N+T), worst O(N+T^2).
