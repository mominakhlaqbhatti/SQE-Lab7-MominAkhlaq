from itertools import combinations, product
from allpairspy import AllPairs

parameters = [
    ["Title", "Author", "ISBN"],          # P1 Query type
    ["None", "Available", "Genre"],       # P2 Filter
    ["Relevance", "A-Z", "Date"],         # P3 Sort order
    ["10", "20", "50"],                   # P4 Page size
]

cases = [list(case) for case in AllPairs(parameters)]
print(f"Generated {len(cases)} test cases")
for number, case in enumerate(cases, start=1):
    print(f"PW{number}: {case}")

total_pairs = 0
missing = []
for i, j in combinations(range(len(parameters)), 2):
    covered = {(case[i], case[j]) for case in cases}
    required = set(product(parameters[i], parameters[j]))
    total_pairs += len(required)
    missing += [(i + 1, j + 1, pair) for pair in required - covered]

print(f"Pairs required: {total_pairs}, missing: {len(missing)}")

full = 1
for values in parameters:
    full *= len(values)
print(f"Full combinations: {full}, pairwise: {len(cases)}, reduction: {full / len(cases):.0f}x")
