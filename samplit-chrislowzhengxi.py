import random
import sys

def samp_lines(filename, prob=0.01):
    # Assume file exists and is readable
    with open(filename, 'r') as file: 
        for line in file:
            if random.random() < prob: 
                # 0 to 1, so 1% chance being retained
                print(line, end='')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python samplit-username.py <filename>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    samp_lines(input_filename)