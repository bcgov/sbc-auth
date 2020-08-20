import os
import sys
from xml.sax.saxutils import escape

from junitparser import Attr, Element, JUnitXml


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
    )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s


class SkippedElement(Element):
    _tag = 'skipped'
    message = Attr()


class FailureElement(Element):
    _tag = 'failure'
    message = Attr()


def analysis():
    skipped = SkippedElement()
    failure = FailureElement()

    newxml = JUnitXml()
    for filename in os.listdir('./test_results'):
        # Only get xml files
        if not filename.endswith('.xml'):
            continue
        fullname = os.path.join('./test_results', filename)
        xml = JUnitXml.fromfile(fullname)
        newxml += xml

    output = []

    for suite in newxml:
        # handle suites
        for testcase in suite:
            testcase.append(failure)
            testcase.child(FailureElement)
            for fail in testcase.iterchildren(FailureElement):
                detail = {"test suite": testcase.classname,
                          "test case": testcase.name,
                          "failure message": html_decode(fail.message)}
                output.append(detail)

    return output


if __name__ == '__main__':
    result: list = analysis()
    if len(result) > 0:
        print(result)
        sys.exit(1)

    sys.exit()
