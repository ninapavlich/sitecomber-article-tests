from ..utils import remove_emails, remove_hashes, remove_phonenumbers, \
    remove_urls, get_misspelled_words, simplify_word
from ..dictionary import core_dictionary

"""
Outstanding mis idenified words:
- moms
- paycheck
- hashtag
- sleepover
- bandanas
- restroom
- sanitizer
- handwash
- descrimination
"""


def test():

    email_input = u"Email test: abc user@xxx.com 123 any@www foo @ bar 78@ppp @5555 aa@111 testing @MyFancyHandle"
    email_expected_output = u"Email test: abc  123  foo  bar    testing  "
    email_actual_output = remove_emails(email_input)
    if email_expected_output != email_actual_output:
        raise Exception("Email removing function returned unexpected output. \nExpected '%s' \nReceieved '%s' " % (email_expected_output, email_actual_output))

    hash_input = u"Hash tag test: this sentence has #fancyhashtag and #MyTag and #mytag# #111Tag"
    hash_expected_output = u"Hash tag test: this sentence has   and   and  #  "
    hash_actual_output = remove_hashes(hash_input)
    if hash_expected_output != hash_actual_output:
        raise Exception("Hash removing function returned unexpected output. \nExpected '%s' \nReceieved '%s' " % (hash_expected_output, hash_actual_output))
    else:
        print("Hash removing logic successful")

    # TODO: 1-800-ALPHNUM  1.222.333.1234 | 1-223-123-1232 | 12223334444 1-(123)-123-1234 | 123 123 1234
    phone_input = u"Phone number test: 1-800-abc-defg and 123-456-7890 and (123)456-7890 and +1-816-555-1212 and 1234567890"
    phone_expected_output = u"Phone number test: -abc-defg and  and   and   and "
    phone_actual_output = remove_phonenumbers(phone_input)
    if phone_expected_output != phone_actual_output:
        raise Exception("Phone number removing function returned unexpected output. \nExpected '%s' \nReceieved '%s' " % (phone_expected_output, phone_actual_output))
    else:
        print("Phone number removing logic successful")

    url_input = u"""
Missing space between this sentence.Another the next one.
URL Test: http://www.example1.com example2.com https://example3.com
Words separated by slashes: and/or happy/sad/etc
Filename Test: .PNG or .JPG format, myfile.pdf or.other filename.doc
URL: ftp://ftp.is.co.za/rfc/rfc1808.txt test text
URL: http://www.ietf.org/rfc/rfc2396.txt test text
URL: mailto:John.Doe@example.com test text
URL: telnet://192.0.2.16:80/ test text
URN (not URL): urn:oasis:names:specification:docbook:dtd:xml:4.1.2 test text
URN (not URL): tel:+1-816-555-1212 tel:1234567890 (?)
IP: 192.0.2.16
URL with query: http://regexlib.com/REDetails.aspx?regexp_id=x#Details
"""
    url_expected_output = u"""
Missing space between this sentence.Another the next one.
URL Test:      
Words separated by slashes: and/or happy/sad/etc
Filename Test: .PNG or .JPG format,   or.other  
URL:   test text
URL:   test text
URL:    test text
URL:   test text
URN (not URL): urn:oasis:names:specification:docbook:dtd:xml:4.1.2 test text
URN (not URL):     (?)
IP:  
URL with query:  
"""
    url_actual_output = remove_urls(url_input)
    if url_expected_output != url_actual_output:
        raise Exception("URL removing function returned unexpected output. \nExpected '%s' \nReceieved '%s' " % (url_expected_output, url_actual_output))
    else:
        print("URL removing logic successful")

    # emove_emails, remove_hashes, remove_phonenumbers, \
    # remove_urls, remove_acronyms,

    words_to_simplify = ['mustardy', 'misstated', 'rashy', 'rashiness',
                         'toddlerhood', 'clinginess', 'seatmates',
                         'grandparenting', 'moisterizers', 'recertified',
                         'cringeworthy', 'reoccurred', 'misappropriating',
                         'handwashing', 'declutter', 'unshowered',
                         'underappreciated', 'reconfigured', 'cataloging']
    expected_output = ['mustard', 'misstate', 'rash', 'rash', 'toddler',
                       'cling', 'seat', 'grandparent', 'moist', 'recertify',
                       'cringe', 'reoccur', 'misappropriate', 'handwash',
                       'clutter', 'shower', 'appreciate',
                       'configure', 'catalog']
    output = []
    for word in words_to_simplify:
        output.append(simplify_word(word, core_dictionary, True))

    if output != expected_output:
        raise Exception("Words incorrectly simplified from:\n%s to:\n%s expected:\n%s" % (words_to_simplify, output, expected_output))

    test_text = u"""
This is an example with proper nouns Dr. Marelle Jazdin, a doctor. Marelle Jazdin is a doctor. Jazdin thinks you should be mindful.
Acronym test: ABCD, A.B.C.D, and even A.B.C.Ds.
Fancy typography test: This is a sentence with fancy curly quotes,” it’s great to have fancy typography like ‘single quotes’ ´back ticks various dashes –-—⁃ ellipses … and fancy bullets •∙

Email test: abc user@xxx.com 123 any@www foo @ bar 78@ppp @5555 aa@111 testing @MyFancyHandle

Hash tag test: this sentence has #fancyhashtag and #MyTag and #mytag# #111Tag

Phone number test: 1-800-222-3456 and 123-456-7890 and +1-816-555-1212 (123)456-7890 1.222.333.1234 | 1-223-123-1232 | 12223334444

URL Test: http://www.example1.com example2.com https://example3.com
Words separated by slashes: and/or happy/sad/etc
Filename Test: .PNG or .JPG format, myfile.pdf filename.doc
URL: ftp://ftp.is.co.za/rfc/rfc1808.txt test text
URL: http://www.ietf.org/rfc/rfc2396.txt test text
URL: mailto:John.Doe@example.com test text
URL: telnet://192.0.2.16:80/ test text
URN (not URL): urn:oasis:names:specification:docbook:dtd:xml:4.1.2 test text
URN (not URL): tel:+1-816-555-1212 (?)
IP: 192.0.2.16
URL with query: http://regexlib.com/REDetails.aspx?regexp_id=x#Details

Compound words test: grandparenting, toddlerhood, seatmates, mustardy, hallucinated, moisterizers, misstated, rashy, clinginess,
sanitizers handwashing recertified bandanas restrooms desensitized weepier scrunchies misappropriating iphones gummy candy yearslong medicating flatline telecommute
emailed transvaginal commoditize counterintuitively pickiest well‐to‐do breast‐feeding nonbinding veganism baby's underappreciated trademarked
hypercompetitive reconfigured dumbest adjustability unshowered prepped women's declutter surefootedness cataloging e-commerce cannibalized keychains
"""
    print("Getting misspelled words - round 1...")
    misspelled_words = get_misspelled_words(test_text, "en", core_dictionary, False)
    if len(misspelled_words) > 0:
        raise Exception("Words incorrectly flagged. Should have found 0 misspellings, but instead found: %s" % (misspelled_words))

    print("Getting misspelled words - round 2...")
    test_text_with_errors = u"""asdl238() 29UDUDJS asdflkjd"""
    misspelled_words = get_misspelled_words(test_text_with_errors, "en", core_dictionary, False)
    if len(misspelled_words) == 0:
        raise Exception("Words incorrectly flagged. Should have found at least one misspelling from %s" % (test_text_with_errors))

    print("Done!")
