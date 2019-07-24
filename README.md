# sitecomber-article-tests
Article content tests for [Sitecomber platform](https://github.com/ninapavlich/sitecomber)


## Installation Instructions

1. pip install sitecomber-article-tests
2. Add 'sitecomber_article_tests.tests' to your INSTALLED_APPS list in your project's settings.py
3. Restart server to see new tests available in site settings


## Supported Tests:

### ReaderViewTest
Returns successful when an article title and text is found using the Newspaper library (https://github.com/codelucas/newspaper/)

You can specify a language other than english in the Site's test settings JSON:
```json
	{
		"lang": "en"
	}
```
See the Newspaper library for a list of supported languages.

NOTE: The article parsing functionality here is used for the tests below. 


### 2. PlaceholderTextTest
Returns successful when no placeholder words are found in the article title or article body.

You can provide custom placeholder words by specifying "placeholder_words" in the Site's test settings JSON:
```json
	{
	  "placeholder_words": [
	    "lorem",
	    "ipsum",
	    "tk",
	    "todo",
	    "tbd"
	  ],
	  "lang": "en"
	}
```
The default list is ["lorem", "ipsum"]

### 3. ArticleReadTimeInfo
Returns approximate read time as "INFO" based on 265WPM estimate

Uses https://pypi.org/project/readtime/

### 4. SpellCheckTest
Returns successful when no spelling errors are found in the article title or article body.

Uses https://github.com/barrust/pyspellchecker for spell-checking

You can provide custom words to the dictionary by specifying "known_words" in the Site's test settings JSON:
```json
	{
	  "known_words": [
	    "lectus",
	    "faucibus",
	    "amet"
	  ],
	  "lang": "en"
	}
```

## Testing Instructions
To use test functions, run the following:

```bash
    virtualenv venv -p python3
    source venv/bin/activate
    pip install -r requirements.txt

    # This will run a general unit test:
    python unit_tests.py

    # This will run an interactive console to test specific words:
    python test_word.py
```