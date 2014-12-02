import sys
import email.parser
import nltk 
from nltk.probability import FreqDist
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from message_decorator import MessageDecorator

class wordCounter:

    def common_word_counts(self, message):
        """
        >>> email_msg = MessageDecorator.from_file('test/test_single.eml')
        >>> wordCounter().common_word_counts(email_msg)
        [('word3', 3), ('word2', 2), ('plain', 1), ('word1', 1), ('My', 1), ('Subject', 1)]
        >>> email_msg = MessageDecorator.from_file('test/test_unicode_warning.eml')
        >>> wordCounter().common_word_counts(email_msg)
        [('holiday', 3), ('We', 2), ('Club', 2), ('party', 2), ('Mighty', 2), ('bars', 1), ('feedback', 1), ('finalized', 1), ('throwing', 1), ('hosted', 1), ('Hey', 1), ('venues', 1), ('one', 1), ('shame', 1), ('planning', 1), ('committee', 1), ('parties', 1), ('event', 1), ('Good', 1), ('would', 1)]
        """
        text = message.text_reply()
        words = self._normal_words(text)
        subject = message.message['Subject']
        if subject is not None:
            words.extend(self._normal_words(subject))
        return self._count(words)

    def _normal_words(self, text):
        """
        >>> wordCounter()._normal_words("When I'm a Duchess,' she said to herself, (not in a very hopeful tone... though) ")
        ['When', 'Duchess', 'said', 'hopeful', 'tone', 'though']
        >>> wordCounter()._normal_words("")
        []
        >>> wordCounter()._normal_words("test joe@gmail.com joe_shmo12+stuff@gmail.com http://minezy.org/app/ https://minezy.org/app/")
        ['test', 'joe@gmail.com', 'joe_shmo12+stuff@gmail.com', 'http://minezy.org/app/', 'https://minezy.org/app/']
        """
        email_regex = r'[A-Za-z0-9\._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}'
        http_url_regex = r'[a-zA-Z]{2,10}\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?'
        word_regex = r'[\s.,:;][\w]+[\s.,:;]'
        blob_regex = r'[\w\+\-=%&^~`#]+'

        tokenizer = RegexpTokenizer(email_regex + '|' + http_url_regex + '|' + word_regex)
        #tokenizer = RegexpTokenizer(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]+|\w+')
        tokens = tokenizer.tokenize(text)
        stop = stopwords.words('english')
        normal = []
        for t in tokens:
            try: 
                t.decode("utf-8")
                if (t not in stop and len(t) > 1 and len(t) < 60):
                    normal.append(t.lower())
            except Exception,e:
                pass 
        return normal

    def _count(self, words):
        """
        >>> wordCounter()._count(['plain', 'word1', 'word2', 'word2', 'word3', 'word3', 'word3'])
        [('word3', 3), ('word2', 2), ('plain', 1), ('word1', 1)]
        >>> wordCounter()._count([])
        []
        """
        fdist1 = FreqDist(words)
        return fdist1.most_common(10)

if __name__ == '__main__':
    import doctest
    doctest.testmod()