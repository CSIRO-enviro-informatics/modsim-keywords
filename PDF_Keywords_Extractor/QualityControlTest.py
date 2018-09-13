import unittest
from PDF_Keywords_Extractor import QualityControl


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.qc = QualityControl.KeywordQualityControl()

    def test_spellingCheck(self):
        #- checks for spelling correct number of wrongly spelt words
        words = ["correct", "monkey", "dragon", "banana", "ApplE", "cHickEn", "Mouse", "donKey", "asdngn", "dthird"]
        self.assertEqual(self.qc.spellingCheck(words), 2)
        #-checks for all correct
        words = ["Test", "car", "walk", "paper", "Steam","BanaNa"]
        self.assertEqual(self.qc.spellingCheck(words), 0)

    def test_check(self):
        #- checks to see if keywords are correctly checked (false is good)

        #-One keyword
        keywords = "manager"
        self.assertEqual(self.qc.check(keywords),False)

        #-small number of keywords
        keywords = "sheep, car."
        self.assertEqual(self.qc.check(keywords),False)

        #-large number of keywords
        keywords = "sheep, car, asdsadas, new ways to search, this is just a test one two three"
        self.assertEqual(self.qc.check(keywords), False)

        #-No keywords, just a big sentences
        keywords = "Any valid Python identifier may be used for a fieldname except for names starting with an underscore. Valid identifiers consist of letters, digits, and underscores but do not start with a digit or underscore and cannot be a keyword such as class, for, return, global, pass, print, or raise."
        self.assertEqual(self.qc.check(keywords), True)

if __name__ == '__main__':
    unittest.main()
