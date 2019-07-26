from ..utils.article import get_placeholder_words


def test():

    print("Test placeholder flagging...")
    placeholder_words = ['lorem', 'ipsum', 'tk', 'todo']
    input_text = u"This is an example sentance with lorem Notsum Lorem and TODO and now klorem bipsum batkite"
    expected_placeholder_words = ['lorem', 'Lorem', 'TODO']
    actual_placeholder_words = get_placeholder_words(input_text, placeholder_words)

    if expected_placeholder_words != actual_placeholder_words:
        raise Exception("Placeholder word finder got unexpected output. \nExpected '%s' \nReceieved '%s' " % (expected_placeholder_words, actual_placeholder_words))

    print("Done testing placeholder functions!")
