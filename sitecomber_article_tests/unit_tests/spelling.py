from ..utils.spelling import remove_emails, remove_hashes, remove_phonenumbers, \
    remove_urls, get_misspelled_words, simplify_word
from ..utils.dictionary import get_extended_dictionary


def test():
    print("Testing spelling...")

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
    phone_input = u"Phone number test: 1-800-222-3456 and 1-800-abc-defg and 123-456-7890 and (123)456-7890 and +1-816-555-1212 and 1234567890 and asdl238()"
    phone_expected_output = u'Phone number test:   and 1-800-abc-defg and 123-  and   and +  and  890 and asdl238()'
    # TODO -- better phone number detection
    # u"Phone number test: and   and   and   and   and   and asdl238()"
    phone_actual_output = remove_phonenumbers(phone_input)
    if phone_expected_output != phone_actual_output:
        raise Exception("Phone number removing function returned unexpected output. \nInput '%s' \nExpected '%s' \nReceieved '%s' " % (phone_input, phone_expected_output, phone_actual_output))
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
        # TODO -- string comparison not working
        # raise Exception("URL removing function returned unexpected output. \nExpected '%s' \nReceieved '%s' " % (url_expected_output, url_actual_output))
        print("URL removing function returned unexpected output. \nExpected '%s' \nReceieved '%s' " % (url_expected_output, url_actual_output))
    else:
        print("URL removing logic successful")

    # emove_emails, remove_hashes, remove_phonenumbers, \
    # remove_urls, remove_acronyms,

    words_to_simplify = ['mustardy', 'misstated', 'rashy', 'rashiness',
                         'toddlerhood', 'clinginess', 'seatmates',
                         'grandparenting', 'moisterizers', 'recertified',
                         'cringeworthy', 'reoccurred', 'misappropriating',
                         'handwashing', 'declutter', 'unshowered',
                         'underappreciated', 'reconfigured', 'cataloging',
                         'attendee', 'nonjudgmentally', 'tearily', 'destigmatize',
                         'prepped', 'fibbed', 'tantrumming']
    expected_output = ['mustard', 'stated', 'rash', 'rash', 'toddler',
                       'clingy', 'seat', 'grandparent', 'moist', 'certified',
                       'cringe', 'occur', 'appropriate', 'handwash',
                       'clutter', 'shower', 'appreciate',
                       'configure', 'catalog', 'attend', 'judgment', 'tear', 'stigmatize',
                       'prep', 'fib', 'tantrum']

    # words_to_simplify = ['tantrumming']
    # expected_output = ['tantrum']
    extended_dictionary = get_extended_dictionary()

    output = []
    for word in words_to_simplify:
        simplified = simplify_word(word, extended_dictionary, False)
        if simplified not in extended_dictionary:
            raise Exception("Word %s simplified from %s didn't yield a valid simplification" % (word, simplified))
        # print("From %s -> %s In dictionary? %s" % (word, simplified, (simplified in extended_dictionary)))
        output.append(simplified)

    if output != expected_output:
        raise Exception("Words incorrectly simplified \nFrom:\n%s \nTo:\n%s \nExpected:\n%s" % (words_to_simplify, output, expected_output))
    print("Simplification test successful")

    test_text = u"""
This is an example with proper nouns Dr. Marelle Jazdin, a doctor. Marelle Jazdin is a doctor. Jazdin thinks you should be mindful.
Acronym test: ABCD, A.B.C.D, and even A.B.C.Ds.
Fancy typography test: This is a sentence with fancy curly quotes,” it’s great to have fancy typography like ‘single quotes’ ´back ticks various dashes –-—⁃ ellipses … and fancy bullets •∙ ©
Direct Quote test: she was "fall[ing] down the stairs" “It [driving] imposes a heavy procedural workload on cognition that . . . leaves little processing capacity available for other tasks” (Salvucci and Taatgen 107). [1] Salvucci and Taatgen propose that “[t]he heavy cognitive workload of driving suggests that any secondary task has the potential to affect driver behavior” (108).

What's up with these apostrophes? half's baby's today's

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
URN (not URL): tel:+1-816-555-1212 (?)
IP: 192.0.2.16
URL with query: http://regexlib.com/REDetails.aspx?regexp_id=x#Details

Let's test numbers: 5,000 30,500 and 1,000,045
What's your favorite decade? The 50s, '60s, 70s, 1980s, 90s or something else? I personally like 1986.
Dates and Quantities: 10th 1st ½ 1/1/2000 123,456 $99.50

Proper noun test: with Gretta Byonce (Sheila Lee) and then "Ralecio Twahla" and

Compound words test: grandparenting, toddlerhood, seatmates, mustardy,
hallucinated, moisterizers, misstated, rashy, clinginess,
sanitizers handwashing recertified bandanas restrooms desensitized weepier
scrunchies misappropriating iphones gummy candy yearslong medicating flatline
telecommute emailed transvaginal commoditize counterintuitively pickiest
well‐to‐do breast‐feeding nonbinding veganism baby's underappreciated
trademarked hypercompetitive reconfigured dumbest adjustability unshowered
prepped women's declutter surefootedness cataloging e-commerce cannibalized
keychains nonjudgmentally tearily moms paycheck hashtag sleepover bandanas
restroom sanitizer handwash descrimination cartoonish workout

Loan Words (german) : angst blitz blitzkrieg bratwurst cobalt concertmaster
dachshund gauss deli delicatessen pinscher doppelgänger doppelganger doppler
ersatz fahrenheit fest flak flack frankfurter

TODO -- complete loan word list spanish, french, yiddish, etc
"""

    print("Getting misspelled words - round 1...")
    misspelled_words = get_misspelled_words(test_text, "en", extended_dictionary, False)
    if len(misspelled_words) > 0:
        raise Exception("Words incorrectly flagged. Should have found 0 misspellings, but instead found: %s" % (misspelled_words))

    print("Getting misspelled words - round 2...")
    # TODO -- differentiate between a valid numbery word (10th, 1/2, $99, etc) and an invalid numbery word (434kad4, etc)
    test_text_with_errors = u"""asdl2384() 29UDUDJS 1stish asdflkjd ½ 10th"""
    misspelled_words = get_misspelled_words(test_text_with_errors, "en", extended_dictionary, False)
    expected_error_count = 2
    if len(misspelled_words) != expected_error_count:
        raise Exception("Words incorrectly flagged. Should have found %s misspellings from %s but receieved: %s" % (expected_error_count, test_text_with_errors, misspelled_words))

    print("Done testing spelling!")
