#!/usr/bin/env python3
import sys
import random

def main():

	filename = sys.argv[1]
	
	with open(filename, 'r', encoding='utf-8') as f:
		for line in f:
			if random.random() < 0.01:
				print(line, end='')

if __name__ == "__main__":
	main()

