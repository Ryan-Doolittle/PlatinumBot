def divider_title(title="", width=50, symbol="-"):
    if len(title) > width:
        print(title[:width])

    left_pad = (width - len(title)) // 2
    right_pad = width - len(title) - left_pad

    print(symbol * left_pad + title + symbol * right_pad)