import sys
import email.parser
from bs4 import BeautifulSoup
from email_reply_parser import EmailReplyParser

class MessageDecorator:
    message=None
    word_counts=[]

    def __init__(self, message=None):
        self.message = message

    @classmethod
    def from_file(cls, fielname):
    	message = email.parser.Parser().parse(open(fielname), headersonly=False)
    	return MessageDecorator(message)

    def text_reply(self):
        """
        >>> email_msg = MessageDecorator.from_file('test/test_single.eml')
        >>> email_msg.text_reply()
        'plain word1, word2, word2, word3, word3, word3'
        """
        text = self.text()
        return EmailReplyParser.parse_reply(text)

    def text(self):
        """
        >>> email_msg = MessageDecorator.from_file('test/test_single.eml')
        >>> email_msg.text()
        'plain word1, word2, word2, word3, word3, word3'
        >>>
        >>> email_msg = MessageDecorator.from_file('test/test_multi.eml')
        >>> email_msg.text()
        'plain word1, word2, word2, word3, word3, word3'
        >>>
        >>> email_msg = MessageDecorator.from_file('test/test_html.eml')
        >>> email_msg.text()
        u'\\n\\n\\nhtml word1, word2, word2, word3, word3, word3\\n\\n\\n'
        >>>
        >>> email_msg = MessageDecorator(email.message.Message())
        >>> email_msg.text()
        ''
        """
        return self._text(self.message)

    def _text(self, message):
        if message.is_multipart():
	        # Recurse into the first message in multi-part
            return self._text(message.get_payload()[0])
        else:
            if message['Content-Type'] is None:
                return ""
            if 'text/html' in message['Content-Type']:
                return BeautifulSoup(message.get_payload(decode=True)).get_text()
            elif 'text/plain' in message['Content-Type']:
                return message.get_payload(decode=True)

        return ""

if __name__ == '__main__':
    import doctest
    doctest.testmod()