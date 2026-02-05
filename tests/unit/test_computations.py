import xml.etree.ElementTree as ET

import pytest

from ct600_fill.computations import get_computations


IXBRL_TEMPLATE = """\
<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
      xmlns:xbrli="http://www.xbrl.org/2003/instance">
  <body>
    <div>
      <xbrli:hidden>
        <xbrli:context id="ctx1">
          <xbrli:entity>
            <xbrli:identifier scheme="http://www.companieshouse.gov.uk/">12345678</xbrli:identifier>
          </xbrli:entity>
        </xbrli:context>
      </xbrli:hidden>
      {elements}
    </div>
  </body>
</html>
"""


class TestGetComputations:
    def test_extracts_non_numeric_values(self):
        elements = '<ix:nonNumeric name="ct:CompanyName">Example Ltd</ix:nonNumeric>'
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=elements))
        result = get_computations(doc)
        assert result["ct:CompanyName"] == "Example Ltd"

    def test_extracts_non_fraction_values(self):
        elements = '<ix:nonFraction name="ct:TurnoverRevenue">50000</ix:nonFraction>'
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=elements))
        result = get_computations(doc)
        assert result["ct:TurnoverRevenue"] == "50000"

    def test_extracts_company_number(self):
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=""))
        result = get_computations(doc)
        assert result["uk-core:UKCompaniesHouseRegisteredNumber"] == "12345678"

    def test_skips_empty_non_numeric(self):
        elements = '<ix:nonNumeric name="ct:Empty"></ix:nonNumeric>'
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=elements))
        result = get_computations(doc)
        assert "ct:Empty" not in result

    def test_skips_empty_non_fraction(self):
        elements = '<ix:nonFraction name="ct:EmptyNum"></ix:nonFraction>'
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=elements))
        result = get_computations(doc)
        assert "ct:EmptyNum" not in result

    def test_multiple_values(self):
        elements = """
        <ix:nonNumeric name="ct:CompanyName">Test Co</ix:nonNumeric>
        <ix:nonFraction name="ct:Revenue">1000</ix:nonFraction>
        <ix:nonFraction name="ct:Costs">500</ix:nonFraction>
        """
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=elements))
        result = get_computations(doc)
        assert result["ct:CompanyName"] == "Test Co"
        assert result["ct:Revenue"] == "1000"
        assert result["ct:Costs"] == "500"
        assert result["uk-core:UKCompaniesHouseRegisteredNumber"] == "12345678"

    def test_non_fraction_overwrites_non_numeric_with_same_name(self):
        elements = """
        <ix:nonNumeric name="ct:Value">text</ix:nonNumeric>
        <ix:nonFraction name="ct:Value">42</ix:nonFraction>
        """
        doc = ET.fromstring(IXBRL_TEMPLATE.format(elements=elements))
        result = get_computations(doc)
        assert result["ct:Value"] == "42"
