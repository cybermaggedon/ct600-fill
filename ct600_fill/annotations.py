
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime
import io
import json

# An annotation, writes a string on a particular page at position x, y
class WriteString:
    def __init__(self, page, x, y):
        self.page = page
        self.x = x
        self.y = y
    def do(self, can, s):
        s = str(s)
        can.drawString(self.x * mm, self.y * mm, s)

# An annotation, writes a string on a particular page at position x, y
class WriteNumber:
    def __init__(self, page, x, y):
        self.page = page
        self.x = x
        self.y = y
    def do(self, can, s):
        s = str(s)
        can.drawString(self.x * mm, self.y * mm, s)

# An annotation, writes a boolean value on a particular page at position x, y.
# The boolean value is represented as a letter X (true) or blank for false.
class WriteBool:
    def __init__(self, page, x, y):
        self.page = page
        self.x = x
        self.y = y
    def do(self, can, s):
        if s:
            can.drawString(self.x * mm, self.y * mm, "X")

# An annotation, writes a string on a particular page, at x, y position.
# This is for where a value is written, one character per box.  The pitch
# parameter defines space between boxes.
class SpaceString:
    def __init__(self, page, x, y, pitch):
        self.page = page
        self.x = x
        self.y = y
        self.pitch = pitch
    def do(self, can, s):
        s = str(s)
        for i in range(0, len(s)):
            can.drawString((self.x + self.pitch * i) * mm, self.y * mm, s[i])

# Writes a whole currency value.  Same as WriteString, but commas are removed
# from the number, and the number is rounded to whole currency.
class WritePounds:
    def __init__(self, page, x, y):
        self.page = page
        self.d = WriteString(page, x, y)
    def do(self, can, s):
        s = int(float(s))
        fmt = "%d"
        s = fmt % s
        self.d.do(can, s)

# Writes a currency value.  Same as WriteString, but commas are removed
# from the number.
class WriteMoney:
    def __init__(self, page, x, y):
        self.page = page
        self.d = WriteString(page, x, y)
    def do(self, can, s):
        s = float(s)
        fmt = "%.2f"
        s = fmt % s
        self.d.do(can, s)

# A cross between SpaceString and WritePounds.  Writes a whole currency
# value one digit per box.  The digits paramter defines the number of
# digits, the number is written right-justified.
class SpacePounds:
    def __init__(self, page, x, y, pitch, digits):
        self.page = page
        self.x = x
        self.y = y
        self.pitch = pitch
        self.digits = digits
        self.d = SpaceString(page, x, y, pitch)
    def do(self, can, s):
        s = int(float(s))
        fmt = "%" + str(self.digits) + "d"
        s = fmt % s
        self.d.do(can, s)

# A cross between SpaceString and WritePounds.  Writes a whole currency
# value one digit per box.  The digits paramter defines the number of
# digits, the number is written right-justified.
class SpaceZeroPadNumber:
    def __init__(self, page, x, y, pitch, digits):
        self.page = page
        self.x = x
        self.y = y
        self.pitch = pitch
        self.digits = digits
        self.d = SpaceString(page, x, y, pitch)
    def do(self, can, s):
        s = int(s)
        fmt = "%0" + str(self.digits) + "d"
        s = fmt % s
        self.d.do(can, s)

# Like SpacePounds but includes a pence value.  x,y defines pounds position,
# x2,y2 defines pence position.
class SpaceMoney:
    def __init__(self, page, x, y, x2, y2, pitch, digits):
        self.page = page
        self.digits = digits
        self.d = SpaceString(page, x, y, pitch)
        self.d2 = SpaceString(page, x2, y2, pitch)
    def do(self, can, s):

        pounds = int(float(s))
        fmt = "%" + str(self.digits) + "d"
        pounds = fmt % pounds
        self.d.do(can, pounds)

        pence = float(s) - int(float(s))
        pence = round(100 * pence + 0.5)
        
        pence = "%02d" % pence
        self.d2.do(can, pence)

# Like SpaceString but for dates in dd mm yyyy format.  x,y defines date
# position, x2,y2 defines month position, x3,y3 defines year position.
class WriteSpaceDate:
    def __init__(self, page, x, y, x2, y2, x3, y3, pitch):
        self.page = page

        self.d = SpaceString(page, x, y, pitch)
        self.m = SpaceString(page, x2, y2, pitch)
        self.y = SpaceString(page, x3, y3, pitch)

    def do(self, can, s):
        s = str(s)
        d = datetime.datetime.strptime(s, "%Y-%m-%d").date()
        self.d.do(can, "%02d" % d.day)
        self.m.do(can, "%02d" % d.month)
        self.y.do(can, "%04d" % d.year)

# Like SpaceString but for sort codes in 123465 format.  x,y defines first
# 2 digits position, x2,y2 defines second position, x3,y3 defines third
class WriteSpaceSortCode:
    def __init__(self, page, x, y, x2, y2, x3, y3, pitch):
        self.page = page

        self.d = SpaceString(page, x, y, pitch)
        self.m = SpaceString(page, x2, y2, pitch)
        self.y = SpaceString(page, x3, y3, pitch)

    def do(self, can, s):
        s = str(s)
        self.d.do(can, "%2s" % s[0:2])
        self.m.do(can, "%2s" % s[2:4])
        self.y.do(can, "%2s" % s[4:6])

operators = {
    "WriteString": WriteString,
    "WriteNumber": WriteNumber,
    "SpaceString": SpaceString,
    "WriteSpaceDate": WriteSpaceDate,
    "WriteSpaceSortCode": WriteSpaceSortCode,
    "WriteBool": WriteBool,
    "SpacePounds": SpacePounds,
    "WritePounds": WritePounds,
    "WriteMoney": WriteMoney,
    "SpaceMoney": SpaceMoney,
    "SpaceZeroPadNumber": SpaceZeroPadNumber,
}

# Should only use trusted input!
def get_spec(file):

    spec = json.load(open(file))
    m = {}

    for items in spec:
        tp = items[1]

        tp = operators[items[1]]

        if items[0] not in m:
            m[items[0]] = []
        
        m[items[0]].append(tp(*items[2:]))

    return m

# Feed in a set of iXBRL-to-value mappings, get the set of annotations back.
def create_annotations(values, spec):

    pages = {}

    for k, v in values["ct600"].items():

        if k in spec:

            anns = spec[k]

            for ann in anns:

                page = ann.page
                if page not in pages:
                    pages[page] = []

                pages[page].append((ann, v))

    return pages

# Takes a set of annotations and a page number, returns a file-like
# structure which is a 1-page PDF of annotations for that page.
def get_page(annotations, page):

    font="Courier-Bold"
    font_size=12

    buffer = io.BytesIO()
    can = canvas.Canvas(buffer, pagesize=A4)
    can.setFont(font, font_size)

    for elt, val in annotations[page]:

        if val is not None:
            elt.do(can, val)

    can.save()
    buffer.seek(0)

    return buffer

