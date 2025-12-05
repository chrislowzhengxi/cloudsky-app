import hashlib
import sys

# --- CONFIGURATION ---
KEY = "049677629"
PUZZLE_FILE = "PUZZLE.txt"
# ---------------------

def edits2(word, alphabet):
    """Generates all strings that are 2 edits away from the word."""
    # 1. Generate all 1-edit strings
    edits1 = set()
    for k in range(len(word)):
        edits1.add(word[:k] + word[k+1:])  # Delete
        if k < len(word) - 1:
            edits1.add(word[:k] + word[k+1] + word[k] + word[k+2:]) # Transpose
        for c in alphabet:
            edits1.add(word[:k] + c + word[k+1:]) # Replace
    for k in range(len(word)+1):
        for c in alphabet:
            edits1.add(word[:k] + c + word[k:]) # Insert
    
    # 2. Generate all 2-edit strings (1-edit of a 1-edit string)
    edits2 = set()
    for e1 in edits1:
        # Re-run all 1-edit operations on the 1-edit result (e1)
        for k in range(len(e1)):
            edits2.add(e1[:k] + e1[k+1:])
            if k < len(e1) - 1:
                edits2.add(e1[:k] + e1[k+1] + e1[k] + e1[k+2:])
            for c in alphabet:
                edits2.add(e1[:k] + c + e1[k+1:])
        for k in range(len(e1)+1):
            for c in alphabet:
                edits2.add(e1[:k] + c + e1[k:])
                
    return edits2

def solve():
    print("[*] Starting 2-Edit Deep Solver for 'tyrant'...")
    
    # Load Hashes
    hashes = []
    try:
        with open(PUZZLE_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split()
                for p in parts:
                    if len(p) == 64:
                        hashes.append(p)
    except FileNotFoundError:
        print(f"[-] {PUZZLE_FILE} not found.")
        return

    key_bytes = KEY.encode('utf-8')
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # 1. Generate 2-edit typos for "tyrant"
    target = "tyrant"
    print(f"[*] Generating all 1-edit and 2-edit typos for '{target}'...")
    typo_candidates = edits2(target, alphabet)
    
    # Add 1-edit typos (just in case the hash corresponds to a clean 1-edit base word)
    # The edits1 generation is included within the edits2 function
    
    # 2. Check the hashes
    punctuation = [".", ",", "?", "!", ";", ":", '"', "'", "’", "“", "”", "-", ")", "]", "}"]
    
    found_typo = None
    
    for target_hash in hashes:
        if found_typo: break
        
        # Check against all typo candidates
        for cand in typo_candidates:
            # Check 1: Raw typo
            if hashlib.sha256(key_bytes + cand.encode('utf-8')).hexdigest() == target_hash:
                found_typo = f"[[TYPO: {cand} (2 edits from {target})]]"
                break
            
            # Check 2: Typo + Suffix Punctuation (e.g. tirantt.)
            for p in punctuation:
                cand_p = cand + p
                if hashlib.sha256(key_bytes + cand_p.encode('utf-8')).hexdigest() == target_hash:
                    found_typo = f"[[TYPO: {cand_p} (2 edits from {target}{p})]]"
                    break
            
            if found_typo: break
        
        # We assume the last remaining blank is the misspelled word
        # The tyrant hash is located near the end of the text.
        
        # This is very aggressive. We assume the problem is a deep typo.
    
    print("\n" + "="*60)
    if found_typo:
        print(f"[!!!] THE MISSPELLED WORD IS LIKELY: {found_typo}")
        print("Once you run the full decode, this string should appear in place of '___'.")
    else:
        print("[*] Failed to find a 2-edit typo for 'tyrant'.")
        print("The misspelled word might be 1-edit of a word we didn't check.")
    print("="*60)

if __name__ == "__main__":
    solve()