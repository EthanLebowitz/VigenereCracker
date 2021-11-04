# requires scipy for chi square and tqdm for progress bars
from scipy.stats import chisquare
from tqdm import tqdm

cipherText = "VRDMVDVHUEYJBMPTFAEAUPSKPIVPKNVGBLOAKJBADKKYQWXWJUZADZVJFZCGEQIWQSMYZWELYCTXERQFFJELJBBTVJVGBQXMEHBUOVSYDIEKVNIMSJEUNMSKEIUIGGIXJVDZVYOOVAJBEQMLZIOIBQNBBBIGLLFXVQZHTCBHICTMSLYIVORLKBBBCMIYMGKDCNIMGGIEJXELZHUWDZZMBTBWRXZEYMCXZQODUGFIZAQTBQPARGUPOXZLTBYFVNPAETDCUBRAJGFACSXYPNMGLLTMDZZMJAFSCCEAKQJNIMKXFLFUOFKCPVOVGYSAYFSOUBYSTBJMFWJODPKVVFJKSGLMNMKDPIVUEKKMVJWAKUQZYYIUNBRSKMFXKJRNFADZZMNMCKRAFQXLFQPZNKXCWMXSEYOOVAJBEQMLZIOIBQNCUPYMKBBZNUFXJVQLYYJVNATYTWPLYYTXKUVMJNIGLXPVYLYUWMKLVRUNSDVIGIVDKBFMXYCCTPGGIXTASEGFZICCKBFXKJRJSWPWJMJWXSCUOLRWNCMTQAMYZWEGEYUPOXZLTBZWIMPVDGGLPLEUVUTWVMKCPVDZRNTMZSIUUMCSKFFICLYUMNYXKBFEYJUMDWBJVWUTIAJNIMGAEHFZ"
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
englishFrequencies = [.0820, .0150, .0280, .0430, .130, .0220, .0200, .0610, .0700, .0015, .0077, .0400, .0240, .0670, .0750, .0190, .01, .0600, .0630, .0910, .0280, .0098, .0240, .0015, .0200, .0007] # from https://en.wikipedia.org/wiki/Letter_frequency

class CaesarCipherDecoder:
    
    def decode(self, cipherText, shiftNumber):
        plainText = ""
        for character in cipherText:
            if character == "," or character == "." or character == " ":
                plainText = plainText + character
            else:
                cipherIndex = alphabet.index(character)
                plainIndex = (cipherIndex - shiftNumber) % len(alphabet)
                plainCharacter = alphabet[plainIndex]
                plainText = plainText + plainCharacter
        return plainText
        
    def getCharacterFrequencies(self, text):
        frequencies = []
        for character in alphabet:
            frequencies.append(text.count(character))
        return frequencies
        
    def getNormalizedCharacterFrequencies(self, text):
            
            englishTotal = sum(englishFrequencies)
            textFrequencies = self.getCharacterFrequencies(text)
            textTotal = sum(textFrequencies)
            factor = englishTotal/textTotal
            scaledTextFrequencies = [frequency * factor for frequency in textFrequencies]
            return scaledTextFrequencies
        
    def getShiftNumber(self, cipherText):
        
        lowestError = float('inf')
        bestShiftNumber = -1
        for shiftNum in range(26):
            plainText = self.decode(cipherText, shiftNum)
            textFrequencies = self.getNormalizedCharacterFrequencies(plainText)
            chiSquare = chisquare(textFrequencies, f_exp=englishFrequencies, ddof=0, axis=0)
            if chiSquare.statistic < lowestError:
                lowestError = chiSquare.statistic
                bestShiftNumber = shiftNum
                
        return bestShiftNumber
        
    def crack(self, cipherText):
        shiftNum = self.getShiftNumber(cipherText)
        plainText = self.decode(cipherText, shiftNum)
        return plainText
        
#caesarCracker = CaesarCipherDecoder()
#print(caesarCracker.crack(("pm ol ohk hufaopun jvumpkluaphs av zhf, ol dyval pa pu jpwoly, aoha pz, if zv johunpun aol vykly vm aol slaalyz vm aol hswohila, aoha uva h dvyk jvbsk il thkl vba.").upper()))

class ViganereCipherDecoder:

    def __init__(self, cipherText):
        self.caesarCracker = CaesarCipherDecoder()
        self.cipherText = cipherText

    def getNthCharacters(self, startIndex, N, cipherText):
        characters = []
        for index in range(startIndex,len(cipherText),N):
            character = cipherText[index]
            characters.append(character)
        return characters
        
    def getIndexOfCoincidence(self, text):
        frequencies = self.caesarCracker.getNormalizedCharacterFrequencies(text)
        indexOfCoincidence = 0
        for frequencies in frequencies:
            indexOfCoincidence += frequencies ** 2
        return indexOfCoincidence
    
    def getKeywordLength(self, cipherText):
        bestLength = -1
        bestIndexOfCoincidence = 0
        for length in range(1,10): #min length 1, max length 10
            characters = self.getNthCharacters(0, length, cipherText)
            indexOfCoincidence = self.getIndexOfCoincidence(characters)
            if indexOfCoincidence > bestIndexOfCoincidence:
                bestLength = length
                bestIndexOfCoincidence = indexOfCoincidence
        return bestLength
        
    def assemble(self, splitPlainText):
        plainText = ""
        for index in range(len(splitPlainText[0])):
            for text in splitPlainText:
                if index < len(text):
                    plainText = plainText + text[index]
        return plainText
        
    def crack(self):
        cipherText = self.cipherText
        keywordLength = self.getKeywordLength(cipherText)
        splitCipherText = [] #split into caesar ciphers
        for caesarOffset in range(keywordLength):
            characters = self.getNthCharacters(caesarOffset, keywordLength, cipherText)
            splitCipherText.append(characters)
        splitPlainText = []
        for text in splitCipherText:
            splitPlainText.append(self.caesarCracker.crack(text))
        plainText = self.assemble(splitPlainText)
        return plainText
        
class WordSplitter:
    
    def __init__(self, text):
        print("prepping dictionary...")
        wordFile = open("dictionary.txt", "r")
        mixedCaseWords = wordFile.readlines()
        wordFile.close()
        self.words = [word.rstrip().upper() for word in tqdm(mixedCaseWords)]
        for word in tqdm(self.words):
            if not self.isWordValid(word):
                self.words.remove(word)
        self.words = sorted(self.words, key=len)
        self.words.reverse() # longest words first
        self.text = text
        
                    
    def isWordValid(self, word): # does it contain no special characters
        for character in word:
            if character not in alphabet:
                return False
        return True
        
    def findNextWord(self, text):
        for word in self.words:
            if text[:len(word)] == word:
                return word
        
    def splitText(self):
        text = self.text
        splitText = ""
        split = False
        print("splitting text...")
        while not split:
            nextWord = self.findNextWord(text)
            splitText = splitText + nextWord + " "
            text = text[len(nextWord):]
            if len(text)==0:
                split = True
        return splitText
        
cracker = ViganereCipherDecoder(cipherText)
plainText = cracker.crack()
print(plainText)
splitter = WordSplitter(plainText)
splitText = splitter.splitText()
print(splitText)
