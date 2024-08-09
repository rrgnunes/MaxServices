def split_string(string, max_length, price_top = False):
    words = string.split()
    lines = []
    current_line = ""

    if price_top:
        title = '*** ' + words[-1].strip() + ' ***' 
        lines.append(title.center(max_length))
        # lines.append('*** ' + words[-1].strip() + ' ***')
        words = words[:-1]

    for word in words:
        if len(current_line) + len(word) <= max_length:
            current_line += word + " "
        else:
            lines.append(current_line.strip().ljust(max_length))
            current_line = word + " "

    if not price_top:
        lines.append('*** ' + current_line.strip() + ' ***')
    else:
        lines.append(current_line.strip())

    return ' ' + ''.join(lines)

