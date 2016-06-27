with open("data/ensembl/Homo_sapiens.GRCh37.75.gtf") as f:
    last_check = ("0","0")
    next(f)
    for line in f:
        if line.startswith("#"):
            continue
        words = line.split()
        if not (int(last_check[0]) <= int(words[0]) and int(last_check[1]) <= int(words[3])):
            print(last_check)
            print ((words[0], words[3]))
            print("NOT SORTED")
        last_check = (words[0], words[3])
