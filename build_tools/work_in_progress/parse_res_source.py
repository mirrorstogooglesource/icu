




with open(sys.args[1], "r") as in:
    source = in.read()


stack = []

in_string = False
in_block_name = False
in_single_line_comment = False
in_whitespace = True

i = 0
while i < len(source):
    if in_single_line_comment:
        if source[i] == "\n":
            in_single_comment = False
            in_whitespace = True
        i += 1
        continue

    if in_multi_line_comment:
        if source[i] == "*" and i + 1 < len(source) and source[i + 1] == "/":
            in_multi_line_comment = False
            in_whitespace = True
            i += 1
        i += 1
        continue

    if in_string:
        if source[i] == '"':
            in_string = False
            in_whitespace = True
        i += 1
        continue

    if in_block_name:
        if source[i] == "{":
            block_name = source[start_block_name:i]
            stack.append(block_name)
            in_block_name = False
            in_whitespace = True
            print("OPEN: " stack)
        else:
            assert source[i].isalnum()
        i += 1
        continue

    if in_whitespace:
        if source[i] == "}":
            print("CLOSE: " + stack)
            del stack[-1]
            i += 1
            continue

        if source[i] == '"':
            in_whitespace = False
            in_string = True
            i += 1
            continue

        if source[i] == "/":
            if i + 1 < len(source) and source[i + 1] == "/":
                in_whitespace = False
                in_single_comment = True
                i += 1
            elif i + 1 < len(source) and source[i + 1] == "*":
                in_whitespace = False
                in_multi_line_comment = True
                i += 1
            else:  # Weird block name?
                assert False, source[max(0, i-40]:i+20]
                in_whitespace = False
                in_block_name = True
                start_block_name = i
            i += 1
            continue

        if source[i].isalnum():
            in_whitespace = False
            in_block_name = True
            start_block_name = i
            i += 1
            continue
