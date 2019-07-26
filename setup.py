from setuptools import setup, find_packages
# this is a test
setup(name='sitecomber-article-tests',
      description='Article related tests for Sitecomber',
      version='0.0.29',
      url='https://github.com/ninapavlich/sitecomber-article-tests',
      author='Nina Pavlich',
      author_email='nina@ninalp.com',
      license='MIT',
      packages=find_packages(),
      package_data={'sitecomber_article_tests': ['*.py', '*.html', '*.css', '*.js', '*.jpg', '*.png']},
      include_package_data=True,
      install_requires=['newspaper3k', 'readtime', 'pyspellchecker', 'textsearch', 'contractions'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved',
          'Operating System :: OS Independent',
          'Programming Language :: Python'
      ]
      )
