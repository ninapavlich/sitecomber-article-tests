from newspaper import Article


def is_reader_view_enabled(html, settings):

    language = 'en' if 'lang' not in settings else settings['lang']
    print("testing reader view in language: %s" % (language))
    # TODO -- validate language available
    article = Article(language=language)
    article.download(html)
    article.parse()

    print("TEXT:")
    print(article.text)

    print("top_image:")
    print(article.top_image)

    print("authors:")
    print(article.authors)

    print("title:")
    print(article.title)

    print("images:")
    print(article.images)

    # TODO
    return True


def contains_placeholder_text(html, settings):
    # TODO
    return False
