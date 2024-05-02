from spire.doc import *
from spire.doc.common import *

# Create a Document object
document = Document()
document.LoadFromFile('Doc.doc')
text = document.GetText()
text = '\n'.join(text.split('\n', 1)[1:])
print(text)