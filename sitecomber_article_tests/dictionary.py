from nltk.corpus import words


modern_technical_terminology = [
    "blog",
    "blogger",
    "website",
    "webpage",
    "homepage",
    "inbox",
    "inboxes",
    "hashtag",
    "email",
    "outsource",
    "timeline",
    "airfare",
    "paycheck",
    "timeout",
    "ipad",
    "iphone",
    "ebay",
    "instagram",
    "facebook",
    "twitter",
    "whiteboard",
    "podcast",
    "livestream",
    "smartphone",
    "upload",
    "download",
    "listserv",
    "screensaver",
    "telecommute"
]
modern_social_terminology = [
    "who'd",
    "mom",
    "bandana",
    "transgender",
    "cisgender",
    "transvaginal",
    "descrimination",
    "anxious",
    "handwash",
    "restroom",
    "sanitizer",

    "misappropriate",
    "dystopian",
    "scrunchy",
    "rehab",
    "veggie",
    "prep",
    "indoctrinate"
    "attune",
    "upcycling",
    "sedate",
    "badass",
    "pushback",
    "inundate",
    "overshare",
    "cilantro",
    "reframing",
    "midcentury",
    "flatline"
]

adopted_words = [
    "reiki",
    'mâché',
    'guac',
    'queso',
    'quesadilla',
    'mitzvah',
    'naïve',
    'fiancée'
    'à'

]

dictionary = set(words.words() + modern_technical_terminology + modern_social_terminology + adopted_words)
