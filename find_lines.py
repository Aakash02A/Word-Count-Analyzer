filename = "c:/Users/loges/Downloads/wordcountanalyzer/templates/index.html"
search_terms = ["stopword-btn", "search-word-btn", "setupVizFilters", "dataStore.words.filter"]

with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        for term in search_terms:
            if term in line:
                print(f"{i+1}: {term} -> {line.strip()}")
