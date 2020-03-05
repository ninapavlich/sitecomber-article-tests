import re
from bs4 import BeautifulSoup

"""
Moz's Recommendations:

Required Tags:
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Page Title. Maximum length 60-70 characters</title>
<meta name="description" content="Page description. No longer than 155
characters.">
<meta name="viewport" content="width=device-width, initial-scale=1">

"""

def has_meta_tags(page, settings):

    soup = BeautifulSoup(page.last_text_content)
    meta_tags_correct = False
    messages = []
    data = {}

    contentTypeTag = soup.find('meta', attrs={'http-equiv': 'Content-Type'}) \
        or soup.find('meta', attrs={'http-equiv': 'content-type'})
    contentType = None if not contentTypeTag else contentTypeTag["content"]
    if not contentType:
        messages.append(u"Page is missing the recommended Content-Type meta tag.")

    titleTag = soup.find('title')
    title = None if not titleTag else titleTag.text
    if not title:
        messages.append(u"Page is missing the title tag.")

    descriptionTag = soup.find('meta', attrs={'name': 'description'})
    description = None if not descriptionTag else descriptionTag["content"]
    if not description:
        messages.append(u"Page is missing the description meta tag.")

    viewportTag = soup.find('meta', attrs={'name': 'viewport'})
    viewport = None if not viewportTag else viewportTag["content"]
    if not viewport:
        messages.append(u"Page is missing the recommended viewport meta tag.")

    if contentType and title and description and viewport:
        status = "success"
        meta_tags_correct = True
        messages.append(u"Page contains properly structured article.")

        if len(title) > 70:
            messages.append(u"WARNING: Title length should be 60-70 characters, currently it is %s." % (len(title)))
            status = "warning"

        if len(description) > 155:
            messages.append(u"WARNING: Description length should be no more than 155 characters, currently it is %s." % (len(description)))
            status = "warning"


        data = {
            'tags': {
                'contentType': contentType,
                'title': title,
                'description': description,
                'viewport': viewport,

            }
        }
    else:
        status = "error"

    message = u" ".join(messages)
    return meta_tags_correct, status, message, data




"""
Social Media Tags:

<!-- Schema.org markup for Google+ -->
<meta itemprop="name" content="The Name or Title Here">
<meta itemprop="description" content="This is the page description">
<meta itemprop="image" content="http://www.example.com/image.jpg">

<!-- Twitter Card data -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@publisher_handle">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="Page description less than 200 characters">
<meta name="twitter:creator" content="@author_handle">
<!-- Twitter summary card with large image must be at least 280x150px -->
<meta name="twitter:image:src" content="http://www.example.com/image.jpg">

<!-- Open Graph data -->
<meta property="og:title" content="Title Here" />
<meta property="og:type" content="article" />
<meta property="og:url" content="http://www.example.com/" />
<meta property="og:image" content="http://example.com/image.jpg" />
<meta property="og:description" content="Description Here" />
<meta property="og:site_name" content="Site Name, i.e. Moz" />
<meta property="article:published_time" content="2013-09-17T05:59:00+01:00" />
<meta property="article:modified_time" content="2013-09-16T19:08:47+01:00" />
<meta property="article:section" content="Article Section" />
<meta property="article:tag" content="Article Tag" />
<meta property="fb:admins" content="Facebook numberic ID" />

"""

def has_socialmedia_tags(page, settings):

    soup = BeautifulSoup(page.last_text_content)
    social_tags_correct = True
    status = "success"
    messages = []
    data = {}

    minimum_tags = [{'name': 'description'}, {'name': 'twitter:card'},
     {'property': 'og:title'}, {'property': 'og:type'}, {'property': 'og:url'},
     {'property': 'og:image'}, {'property': 'og:description'}]


    for tagAttrs in minimum_tags:
        foundTag = soup.find('meta', attrs=tagAttrs)
        foundTagContent = None if not foundTag else foundTag["content"]
        if not foundTagContent:
            social_tags_correct = False
            status = "error"
            tagKey = next(iter(tagAttrs))
            tagAttrFormatted = "%s__%s"%(tagKey, tagAttrs[tagKey])
            messages.append(u"Recommended social meta tag %s was not found." % (tagAttrFormatted))
    if social_tags_correct:
        messages.append(u"All recommended social meta tags were found.")

    all_tags = [{'name': 'description'},
        {'itemprop': 'name'}, {'itemprop': 'description'},
        {'itemprop': 'image'}, {'name': 'twitter:card'},
        {'name': 'twitter:site'}, {'name': 'twitter:title'},
        {'name': 'twitter:description'}, {'name': 'twitter:creator'},
        {'name': 'twitter:image:src'}, {'property': 'og:title'},
        {'property': 'og:type'}, {'property': 'og:url'},
        {'property': 'og:image'}, {'property': 'og:description'},
        {'property': 'og:site_name'}, {'property': 'article:published_time'},
        {'property': 'article:modified_time'}, {'property': 'article:section'},
        {'property': 'article:tag'}, {'property': 'fb:admins'}]

    for tagAttrs in all_tags:
        tagKey = next(iter(tagAttrs))
        tagAttrFormatted = "%s__%s"%(tagKey, tagAttrs[tagKey])
        foundTag = soup.find('meta', attrs=tagAttrs)
        foundTagContent = None if not foundTag else foundTag["content"]
        data[tagAttrFormatted] = foundTagContent

    message = u" ".join(messages)
    return social_tags_correct, status, message, data
