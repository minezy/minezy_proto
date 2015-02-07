import sys
import email.parser
import nltk 
import re
from nltk.probability import FreqDist
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from message_decorator import MessageDecorator

class wordCounter:
    word_types = None
    subject_only = None
    words_per_message = None
    debug = None
    tokenizer = None
    word_type_regexs = None
    stop_words = stopwords.words('english')


    def __init__(self, word_types=None, subject_only=False, words_per_message=10, debug=False):
        self.subject_only = subject_only
        self.words_per_message = words_per_message
        self.debug = debug
        self.tokenizer = RegexpTokenizer(self._tokenizer_regex())
        self._init_word_types(word_types)

    def _init_word_types(self, word_types):
        if word_types is None:
            self.word_types = wordCounter.word_types()
        else: 
            self.word_types = word_types

        self.word_type_regexs = {}
        for word_type in wordCounter.word_types():
            self.word_type_regexs[word_type] = re.compile(self._type_regex(word_type))

    def common_word_counts(self, message):
        """
        >>> email_msg = MessageDecorator.from_file('test/test_single.eml')
        >>> wordCounter().common_word_counts(email_msg)
        [('word3', 3), ('word2', 2), ('plain', 1), ('word1', 1), ('my', 1), ('subject', 1)]
        >>> wordCounter(word_types=['emails']).common_word_counts(email_msg)
        []
        >>> email_msg = MessageDecorator.from_file('test/test_unicode_warning.eml')
        >>> wordCounter().common_word_counts(email_msg)
        [('holiday', 3), ('mighty', 2), ('party', 2), ('we', 2), ('club', 2), ('bars', 1), ('feedback', 1), ('finalized', 1), ('throwing', 1), ('hosted', 1)]
        """
        words = []
        if (self.subject_only is False):
            text = message.text_reply()
            words = self._normal_words(text)
        subject = message.message['Subject']
        if subject is not None:
            words.extend(self._normal_words(subject))
        return self._count(words)

    @classmethod
    def word_types(cls):
        return ['urls', 'emails', 'words', 'blobs']

    def _type_regex(self, word_type):
        if word_type == 'emails':
            return r'[A-Za-z0-9\._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}'
        elif word_type == 'urls':
            return r'[a-zA-Z]{2,10}\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?'
        elif word_type == 'words':
            #return r'(?![^\s.,:;=])[\w]+(?=[$\s.,:;=])' 
            return r'\A(?=\w)\D+\Z'
        elif word_type == 'blobs':
            return r'[\w\+\-=%&^~`#]+';
        else:
            raise "Unrecognized word type " + str(word_type)

    def _tokenizer_regex(self):
        return self._type_regex('urls') + '|' +self._type_regex('emails') + '|' + self._type_regex('blobs')

    def _word_type(self, word):
        """
        >>> wordCounter()._word_type("joe@gmail.com")
        'emails'
        >>> wordCounter()._word_type("http://minezy.org/app/")
        'urls'
        >>> wordCounter()._word_type("test")
        'words'
        >>> wordCounter()._word_type("word_word-word")
        'words'
        >>> wordCounter()._word_type("1234")
        'blobs'
        >>> wordCounter()._word_type("word$1234")
        'blobs'
        >>> wordCounter()._word_type("test1234")
        'blobs'
        >>> wordCounter()._word_type("wor&400d@")
        'blobs'
        >>> wordCounter()._word_type("test&")
        'blobs'
        """        
        for word_type in wordCounter.word_types():
            if self.word_type_regexs[word_type].match(word):
                return word_type
        return None

    def _is_normal_word(self, word):
        """
        >>> wordCounter()._is_normal_word("joe@gmail.com")
        True
        >>> wordCounter()._is_normal_word("test")
        True
        >>> wordCounter()._is_normal_word("Francisco\xe2")
        False
        >>> wordCounter()._is_normal_word("d")
        False
        >>> wordCounter()._is_normal_word("dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        False
        """        
        try: 
            word.decode("utf-8")
            if word in self.stop_words: 
                return False
            if len(word) == 1 or len(word) > 60:
                return False
            if self._word_type(word) not in self.word_types:
                return False
        except Exception,e:
            return False

        return True

    def _normal_words(self, text):
        """
        >>> wordCounter()._normal_words("When I'm a Duchess,' she said to herself, (not in a very hopeful tone... though) ")
        ['when', 'duchess', 'said', 'hopeful', 'tone', 'though']
        >>> wordCounter()._normal_words("")
        []
        >>> wordCounter()._normal_words("test joe@gmail.com joe_shmo12+stuff@gmail.com http://minezy.org/app/ https://minezy.org/app/")
        ['test', 'joe@gmail.com', 'joe_shmo12+stuff@gmail.com', 'http://minezy.org/app/', 'https://minezy.org/app/']
        """
        tokens = self.tokenizer.tokenize(text)
        stop = stopwords.words('english')
        normal = []
        for t in tokens:
            if self._is_normal_word(t):
                normal.append(t.lower())
        return normal

    def _count(self, words):
        """
        >>> wordCounter()._count(['plain', 'word1', 'word2', 'word2', 'word3', 'word3', 'word3'])
        [('word3', 3), ('word2', 2), ('plain', 1), ('word1', 1)]
        >>> wordCounter()._count([])
        []
        >>> wordCounter(words_per_message=-1)._count(['plain', 'word1', 'word2', 'word2', 'word3', 'word3', 'word3'])
        [('word3', 3), ('word2', 2), ('plain', 1), ('word1', 1)]
        """
        fdist1 = FreqDist(words)
        if (self.words_per_message > 0):
            return fdist1.most_common(self.words_per_message)
        else:
            return fdist1.most_common()

if __name__ == '__main__':
    import doctest
    doctest.testmod()