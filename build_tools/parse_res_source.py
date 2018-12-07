from __future__ import print_function

import sys

class Root(object):
    def __init__(self, end_text):
        self.start_text = 0
        self.children = []
        self.end_text = end_text
        self.block_type = '<root>'

    def __repr__(self):
        return 'Root(%r)' % (self.end_text)

    def __str__(self):
        return '<root>'

    def main_node(self):
        for x in self.children:
            if isinstance(x, Block):
                return x
        return None

class Block(object):
    def __init__(self, name, block_type, start_block_name, end_text=None):
        self.name = name
        self.block_type = block_type
        self.start_block_name = start_block_name
        self.start_text = start_block_name
        self.children = []
        self.end_text = end_text

    def __repr__(self):
        return 'Block(%r,%r,%r,%r)' % (
            self.name, self.block_type, self.start_block_name, self.end_text)

    def __str__(self):
        return '%s:%s' % (self.name, self.block_type)

    def get_block_children(self):
        return [x for x in self.children if isinstance(x, Block)]

    def is_text_whitespace_only(self, source):
        for text in [x for x in self.children if isinstance(x, Text)]:
            if not source[text.start_text:text.end_text].isspace():
                return False
        return True

EMPTY_TUPLE = tuple([])
class Text(object):
    def __init__(self, start_text, end_text):
        self.start_text = start_text
        self.children = EMPTY_TUPLE
        self.end_text = end_text

    def __repr__(self):
        return 'Text(%r,%r)' % (
            self.start_text, self.end_text)

    def __str__(self):
        return '<text>'


def _print_stack(stack):
    stack_str = ' -> '.join([str(x) for x in stack])
    print(stack_str)

def _print_tree(block, indentation=0, repr_mode=False):
    if repr_mode:
        s = repr(block)
    else:
        s = str(block)
    print('%s%s' % (indentation*'  ', s))
    for child in block.children:
        _print_tree(child, indentation + 1, repr_mode)

STATE_NAMES = (
    'in_root_or_block',
    'in_string',
    'in_number',
    'in_block_name',
    'in_block_type',
    'in_single_line_comment',
    'in_multi_line_comment',
)

WHITESPACE = '\t\r\n '

class Parser(object):

    def __init__(self, source):
        self._source = source
        self._tree = None

    def _make_traverse_list(self, the_list, current_node):
        the_list.append(current_node)
        for node in current_node.children:
            self._make_traverse_list(the_list, node)

    def _get_line(self, start):
        end = self._source.find('\n', start)
        if end == -1:
            end = len(self._source)
        return self._source[start:end]

    def get_cleaned_source(self, to_delete_list):
        assert to_delete_list, 'Do not waste time here.'
        source_len = len(self._source)
        keep_char = [True] * source_len
        cleaned_source_list = []
        to_delete = set(to_delete_list)
        for node in to_delete:
            del_len = node.end_text - node.start_text
            keep_char[node.start_text:node.end_text] = [False] * del_len

        # Remove lines that would end up empty too.
        start_line = 0
        source_pos = 0
        only_whitespace = True
        while source_pos < source_len:
            if keep_char[source_pos]:
                if self._source[source_pos] == '\n':
                    if only_whitespace:
                        # Delete line.
                        for i in range(start_line, source_pos + 1):
                            keep_char[i] = False
                    start_line = source_pos + 1
                    only_whitespace = True
                elif self._source[source_pos] not in WHITESPACE:
                    only_whitespace = False
            source_pos += 1

        # Extract the remaining parts of the source.
        start = 0
        while True:
            end = start
            while end < source_len and keep_char[end]:
                end += 1
            if start != end:
                cleaned_source_list.append(self._source[start:end])
            start = end + 1
            while start < source_len and not keep_char[start]:
                start += 1
            if start >= source_len:
                break

        cleaned_source = ''.join(cleaned_source_list)
        return cleaned_source

    def get_tree(self):
        return self._tree

    def parse(self, verbose=False, debug=False):
        """The main parser. It is tempting to break this up in a lot of small
        functions but that made it much, much slower. So big function where
        everything is a local variable it is."""
        should_print_open_close = verbose

        def is_block_name_char(c):
            return c.isalnum() or c in '%_-+"'

        def get_state():
            return STATE_NAMES[current_state]

        def get_source_context():
            return (source[source_pos],
                    source[max(0, source_pos-40):source_pos+20])

        have_asserts = verbose or debug

        # Index to where the current block name starts.
        start_block_name = None

        # Index to where the current string starts.
        start_string = None

        # Index to where the current text starts.
        start_text = 0

        # Having a local variable for the source position makes the
        # parser 15% faster.
        source_pos = 0

        # Having the source variable local makes the parser 10%
        # faster.
        source = self._source
        source_len = len(source)
        root_block = Root(source_len)
        stack = [root_block]

        if source.startswith('\xef\xbb\xbf'):
            # BOM
            source_pos = 3

        # A local STATE makes it 10% faster.
        STATE = {}
        for s in STATE_NAMES:
            STATE[s] = STATE_NAMES.index(s)

        # A local current_state makes the parser 15% faster
        current_state = STATE['in_root_or_block']

        while source_pos < source_len:
            if debug:
                print(source_pos, (source[source_pos], get_state()))
            if current_state == STATE['in_single_line_comment']:
                if source[source_pos] == '\n':
                    current_state = STATE['in_root_or_block']
                    source_pos -= 1
                source_pos += 1
                continue

            if current_state == STATE['in_multi_line_comment']:
                if (source[source_pos] == '*' and
                    source_pos + 1 < source_len and
                    source[source_pos + 1] == '/'):
                    current_state = STATE['in_root_or_block']
                    source_pos += 1
                source_pos += 1
                continue

            if current_state == STATE['in_string']:
                if source[source_pos] == '"':
                    # Strings can be block names. At least the string
                    # "%%ALIAS". So make that exception (or should we
                    # parse strings with the 'in_block_name' parser?)
                    if (source_pos + 1 < source_len and
                        source[source_pos + 1] == '{'):
                        source_pos = start_string - 1
                        current_state = STATE['in_block_name']
                        start_block_name = source_pos + 1
                        if source_pos + 1 != start_text:
                            stack[-1].children.append(
                                Text(start_text, source_pos + 1))
                    else:
                        assert not (source_pos + 1 < source_len and
                                    source[source_pos + 1] == ':'), (
                                        'Not supported')  # See ex10
                        current_state = STATE['in_root_or_block']
                source_pos += 1
                continue

            if current_state == STATE['in_number']:
                if source[source_pos] not in '.0123456789':
                    current_state = STATE['in_root_or_block']
                    if source[source_pos] not in WHITESPACE + ',':
                        # Parse again, maybe it's a block end.
                        source_pos -= 1
                source_pos += 1
                continue

            if current_state == STATE['in_block_name']:
                if (source[source_pos] in '{ ' or
                    source[source_pos] == ':' and
                    start_block_name != start_string):
                    # End of the block name. A colon only ends the block
                    # name if it's outside a quoted string.
                    block_name = source[start_block_name:source_pos]
                    current_state = STATE['in_block_type']
                    if source[source_pos] == '{':
                        start_block_type = source_pos
                        # Read this char again, terminating the block type
                        source_pos -= 1
                    else:
                        start_block_type = source_pos + 1
                else:
                    if (source[source_pos] == '"' and
                        start_block_name == start_string and
                        start_string != source_pos):
                        # No longer in a quoted block name.
                        start_string = None
                    if have_asserts:
                        assert is_block_name_char(source[source_pos]), (
                            get_source_context())
                source_pos += 1
                continue

            if current_state == STATE['in_block_type']:
                if source[source_pos] == '{':
                    # block_name was set when we parsed the ':'
                    block_type = source[start_block_type:source_pos].strip()
                    if have_asserts:
                        assert ' ' not in block_type, block_type
                    if block_type == '':
                        block_type = 'block'
                    if block_name == '':
                        block_name = '<anon>'
                    stack.append(Block(block_name, block_type,
                                       start_block_name))
                    stack[-2].children.append(stack[-1])

                    current_state = STATE['in_root_or_block']
                    start_text = source_pos + 1
                    if should_print_open_close:
                        print('OPEN: ', end='')
                        _print_stack(stack)
                else:
                    # Allow whitespace before block opens. Will be
                    # stripped when the type is stored.
                    if have_asserts:
                        assert (source[source_pos].isalnum() or
                                source[source_pos] in '(_) '), (
                                    get_source_context())
                source_pos += 1
                continue

            if current_state == STATE['in_root_or_block']:
                # Digits are either blocknames or numbers depending on
                # context. Check for number first.
                if (stack[-1].block_type in ('intvector', 'int') and (
                        source[source_pos].isdigit() or
                        source[source_pos] in '-.')):
                    current_state = STATE['in_number']
                    source_pos += 1
                    continue

                # Quotes are either the block name "%%ALIAS", a block
                # name with a colon in it or strings depending on
                # context. Check for string first.
                if source[source_pos] == '"':
                    current_state = STATE['in_string']
                    start_string = source_pos
                    source_pos += 1
                    continue

                if (source[source_pos] in ':{' or
                    is_block_name_char(source[source_pos])):
                    current_state = STATE['in_block_name']
                    start_block_name = source_pos
                    if source_pos != start_text:
                        stack[-1].children.append(
                            Text(start_text, source_pos))
                    if source[source_pos] in ':{':
                        # Parse it again and jump to in_block_type.
                        source_pos -= 1
                    source_pos += 1
                    continue

                if source[source_pos] == '}':
                    if source_pos != start_text:
                        stack[-1].children.append(
                            Text(start_text, source_pos))
                    if should_print_open_close:
                        print('CLOSE: ', end='')
                        _print_stack(stack)
                    stack[-1].end_text = source_pos + 1
                    del stack[-1]
                    start_text = source_pos + 1
                    source_pos += 1
                    continue

                if source[source_pos] == '/':
                    if (source_pos + 1 < source_len and
                        source[source_pos + 1] == '/'):
                        current_state = STATE['in_single_line_comment']
                        source_pos += 1
                    elif (source_pos + 1 < source_len and
                          source[source_pos + 1] == '*'):
                        current_state = STATE['in_multi_line_comment']
                        source_pos += 1
                    else:  # Weird block name?
                        assert False, get_source_context()
                        if source_pos != start_text:
                            stack[-1].children.append(
                                Text(start_text, source_pos))
                        current_state = STATE['in_block_name']
                        start_block_name = source_pos
                    source_pos += 1
                    continue

                if source[source_pos] == '\n':
                    source_pos += 1
                    continue

                if have_asserts:
                    assert (source[source_pos] in WHITESPACE or
                            source[source_pos] == ','), (
                                get_source_context())
                source_pos += 1
                continue

            assert False, list(get_source_context()) + [get_state()]

        if source_pos != start_text:
            stack[-1].children.append(
                Text(start_text, source_pos))

        self._tree = root_block
        #_print_tree(root_block, repr_mode=True)
        if have_asserts:
            self.assert_good_tree(root_block)
        return self._tree

    def assert_good_tree(self, block):
        assert block.end_text is not None, repr(block)
        for child in block.children:
            self.assert_good_tree(child)

def main():
    print('Parsing %d files.' % (len(sys.argv) - 1))
    for file_name in sys.argv[1:]:
        with open(file_name, 'r') as in_file:
            source = in_file.read()

        should_print_tree = True
        if should_print_tree:
            print(file_name)
            print('--------')
        try:
            parser = Parser(source)
            parser.parse()
            if should_print_tree:
                if parser.get_tree():
                    _print_tree(parser.get_tree())
        except AssertionError as exc:
            print(exc)
            raise

if __name__ == '__main__':
    main()

