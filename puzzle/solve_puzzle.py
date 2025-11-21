import hashlib
import multiprocessing
import time
import sys
import os
import string

# --- CONFIGURATION ---
PUZZLE_FILE = "PUZZLE.txt"
# PUZZLE_FILE = "PUZZLE-EASY.txt"

# We assume one of these words appears in the text. "the" is statistically the safest bet.
ANCHORS = ["the", "The", "and", "And", "a", "to", "of", "in", "is", "that"]
# Standard dictionary path on Linux/Unix systems (including Midway)
DICT_PATH = "/usr/share/dict/words"

def load_hashes(filename):
    """Reads the puzzle file and extracts valid SHA256 hashes."""
    valid_hashes = []
    raw_lines = [] 
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Store original order for final print
                raw_lines.append(line.strip())
                
                # Extract hash: look for 64-char hex strings
                # This handles lines like "84e3..."
                parts = line.strip().split()
                for p in parts:
                    if len(p) == 64 and all(c in string.hexdigits for c in p):
                        valid_hashes.append(p)
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        sys.exit(1)
        
    return valid_hashes, raw_lines

def worker_search_key(args):
    """Worker process to search a specific range of numbers."""
    start, end, target_hashes_set = args
    
    # Pre-encode anchors to save time in the tight loop
    anchor_bytes = [w.encode('utf-8') for w in ANCHORS]
    
    # Loop through the assigned range
    for i in range(start, end):
        # Create the 9-digit key format
        key_str = f"{i:09d}"
        key_bytes = key_str.encode('utf-8')
        
        for w_bytes in anchor_bytes:
            # Hash strategy: sha256(key + word)
            # We only check the anchor words first to be fast
            digest = hashlib.sha256(key_bytes + w_bytes).hexdigest()
            
            if digest in target_hashes_set:
                return key_str
    return None

def find_key_parallel(target_hashes):
    """Splits the work across all available CPU cores."""
    target_set = set(target_hashes)
    num_cores = multiprocessing.cpu_count()
    total_keys = 1_000_000_000 # 0 to 999,999,999
    # total_keys = 10000
    
    print(f"[*] Starting search on {num_cores} cores.")
    print(f"[*] Searching space: 000000000 - 999999999")
    # print(f"[*] Searching space: 0000 - 9999")
    
    # Divide work
    chunk_size = total_keys // num_cores
    ranges = []
    for i in range(num_cores):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_cores - 1 else total_keys
        ranges.append((start, end, target_set))
        
    start_time = time.time()
    
    # Run parallel workers
    pool = multiprocessing.Pool(processes=num_cores)
    # imap_unordered allows us to stop as soon as one worker finds the key
    for result in pool.imap_unordered(worker_search_key, ranges):
        if result:
            pool.terminate()
            elapsed = time.time() - start_time
            print(f"[+] KEY FOUND: {result}")
            print(f"[+] Time taken: {elapsed:.2f} seconds")
            return result
            
    return None

def brute_force_typo(key, target_hash, dictionary_words):
    """Finds the typo by trying 1-edit distance on dictionary words."""
    print(f"[*] Attempting to break unknown hash: {target_hash[:10]}...")
    key_bytes = key.encode('utf-8')
    alphabet = string.ascii_letters
    
    # We try to 'break' every word in the dictionary to see if it matches the hash
    # This assumes the typo is a 1-character error (substitution, deletion, insertion)
    for word in dictionary_words:
        if len(word) < 2: continue # Skip single chars usually
        
        edits = set()
        # Deletions
        for i in range(len(word)):
            edits.add(word[:i] + word[i+1:])
        # Transpositions
        for i in range(len(word)-1):
            edits.add(word[:i] + word[i+1] + word[i] + word[i+2:])
        # Substitutions
        for i in range(len(word)):
            for c in alphabet:
                edits.add(word[:i] + c + word[i+1:])
        # Insertions
        for i in range(len(word)+1):
            for c in alphabet:
                edits.add(word[:i] + c + word[i:])
                
        for candidate in edits:
            h = hashlib.sha256(key_bytes + candidate.encode('utf-8')).hexdigest()
            if h == target_hash:
                return candidate, word # Found the typo, and the original word
                
    return None, None

def decrypt_message(key, hashes_list):
    """Decrypts the full message."""
    print("\n[*] Loading dictionary...")
    try:
        with open(DICT_PATH, 'r', errors='ignore') as f:
            words = [line.strip() for line in f]
    except:
        # Fallback if system dict is missing (unlikely on Midway)
        print("[-] System dictionary not found. Using small fallback.")
        words = ANCHORS + ["example", "test", "words"]

    # Add anchors explicitly just in case
    words = list(set(words + ANCHORS))
    
    print("[*] Building Rainbow Table (hashing dictionary with key)...")
    lookup = {}
    key_bytes = key.encode('utf-8')
    
    for w in words:
        h = hashlib.sha256(key_bytes + w.encode('utf-8')).hexdigest()
        lookup[h] = w
        
    print("\n--- DECODED MESSAGE ---")
    decoded_msg = []
    unknown_hashes = []
    
    for h in hashes_list:
        if h in lookup:
            decoded_msg.append(lookup[h])
        else:
            decoded_msg.append("UNKNOWN")
            unknown_hashes.append(h)
            
    print(" ".join(decoded_msg))
    print("-----------------------\n")
    
    if unknown_hashes:
        print(f"[*] Found {len(unknown_hashes)} unknown word(s). Analyzing...")
        # Usually there's just one misspelled word
        unique_unknowns = set(unknown_hashes)
        for uh in unique_unknowns:
            typo, original = brute_force_typo(key, uh, words)
            if typo:
                print(f"\n[!!!] SOLVED:")
                print(f"      Misspelled Word: '{typo}'")
                print(f"      Intended Word:   '{original}'")

if __name__ == "__main__":
    # 1. Load Hashes
    hashes, _ = load_hashes(PUZZLE_FILE)
    if not hashes:
        print("No hashes found.")
        sys.exit(1)
        
    # 2. Find Key
    key = find_key_parallel(hashes)
    
    # 3. Decrypt & Find Typo
    if key:
        decrypt_message(key, hashes)
    else:
        print("[-] Key not found. Ensure ANCHORS contains a word in the text.")