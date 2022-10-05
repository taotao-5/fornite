def truncate(num, n):  # copied and pasted this one from https://www.delftstack.com/howto/python/python-truncate-float-python/
    temp = str(num)
    for x in range(len(temp)):
        if temp[x] == '.':
            try:
                return float(temp[:x + n + 1])
            except IndexError:
                return float(temp)
    return float(temp)
