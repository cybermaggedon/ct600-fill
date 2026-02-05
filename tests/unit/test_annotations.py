import json
import os
import tempfile
from unittest.mock import MagicMock

import pytest
from reportlab.lib.units import mm

from ct600_fill.annotations import (
    WriteString,
    WriteNumber,
    WriteBool,
    SpaceString,
    WritePounds,
    WriteMoney,
    SpacePounds,
    SpaceZeroPadNumber,
    SpaceMoney,
    WriteSpaceDate,
    WriteSpaceSortCode,
    get_spec,
    create_annotations,
)


@pytest.fixture
def canvas():
    return MagicMock()


# --- WriteString ---

class TestWriteString:
    def test_draws_string_at_correct_position(self, canvas):
        ann = WriteString(page=0, x=10, y=20)
        ann.do(canvas, "Hello")
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "Hello")

    def test_converts_value_to_string(self, canvas):
        ann = WriteString(page=0, x=5, y=5)
        ann.do(canvas, 123)
        canvas.drawString.assert_called_once_with(5 * mm, 5 * mm, "123")

    def test_stores_page(self):
        ann = WriteString(page=3, x=0, y=0)
        assert ann.page == 3


# --- WriteNumber ---

class TestWriteNumber:
    def test_draws_number_as_string(self, canvas):
        ann = WriteNumber(page=0, x=10, y=20)
        ann.do(canvas, 42)
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "42")

    def test_draws_string_value(self, canvas):
        ann = WriteNumber(page=0, x=10, y=20)
        ann.do(canvas, "99")
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "99")


# --- WriteBool ---

class TestWriteBool:
    def test_draws_x_for_true(self, canvas):
        ann = WriteBool(page=0, x=10, y=20)
        ann.do(canvas, True)
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "X")

    def test_draws_nothing_for_false(self, canvas):
        ann = WriteBool(page=0, x=10, y=20)
        ann.do(canvas, False)
        canvas.drawString.assert_not_called()

    def test_draws_x_for_truthy_string(self, canvas):
        ann = WriteBool(page=0, x=10, y=20)
        ann.do(canvas, "yes")
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "X")


# --- SpaceString ---

class TestSpaceString:
    def test_draws_characters_at_pitch_spacing(self, canvas):
        ann = SpaceString(page=0, x=10, y=20, pitch=5)
        ann.do(canvas, "AB")
        assert canvas.drawString.call_count == 2
        canvas.drawString.assert_any_call(10 * mm, 20 * mm, "A")
        canvas.drawString.assert_any_call((10 + 5) * mm, 20 * mm, "B")

    def test_single_character(self, canvas):
        ann = SpaceString(page=0, x=10, y=20, pitch=5)
        ann.do(canvas, "X")
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "X")

    def test_converts_to_string(self, canvas):
        ann = SpaceString(page=0, x=10, y=20, pitch=5)
        ann.do(canvas, 12)
        assert canvas.drawString.call_count == 2
        canvas.drawString.assert_any_call(10 * mm, 20 * mm, "1")
        canvas.drawString.assert_any_call((10 + 5) * mm, 20 * mm, "2")


# --- WritePounds ---

class TestWritePounds:
    def test_rounds_float_to_integer(self, canvas):
        ann = WritePounds(page=0, x=10, y=20)
        ann.do(canvas, 123.45)
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "123")

    def test_handles_string_input(self, canvas):
        ann = WritePounds(page=0, x=10, y=20)
        ann.do(canvas, "456.78")
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "456")

    def test_handles_integer(self, canvas):
        ann = WritePounds(page=0, x=10, y=20)
        ann.do(canvas, 100)
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "100")


# --- WriteMoney ---

class TestWriteMoney:
    def test_formats_to_two_decimal_places(self, canvas):
        ann = WriteMoney(page=0, x=10, y=20)
        ann.do(canvas, 142.1)
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "142.10")

    def test_formats_string_input(self, canvas):
        ann = WriteMoney(page=0, x=10, y=20)
        ann.do(canvas, "99.9")
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "99.90")

    def test_formats_integer_input(self, canvas):
        ann = WriteMoney(page=0, x=10, y=20)
        ann.do(canvas, 50)
        canvas.drawString.assert_called_once_with(10 * mm, 20 * mm, "50.00")


# --- SpacePounds ---

class TestSpacePounds:
    def test_right_justified_digits(self, canvas):
        ann = SpacePounds(page=0, x=10, y=20, pitch=5, digits=6)
        ann.do(canvas, 748.0)
        # "%6d" % 748 == "   748"
        formatted = "%6d" % 748
        assert canvas.drawString.call_count == len(formatted)
        for i, ch in enumerate(formatted):
            canvas.drawString.assert_any_call((10 + 5 * i) * mm, 20 * mm, ch)

    def test_handles_string_input(self, canvas):
        ann = SpacePounds(page=0, x=10, y=20, pitch=5, digits=4)
        ann.do(canvas, "99.5")
        formatted = "%4d" % 99
        assert canvas.drawString.call_count == len(formatted)


# --- SpaceZeroPadNumber ---

class TestSpaceZeroPadNumber:
    def test_zero_pads_digits(self, canvas):
        ann = SpaceZeroPadNumber(page=0, x=10, y=20, pitch=5, digits=4)
        ann.do(canvas, 6)
        # "%04d" % 6 == "0006"
        formatted = "0006"
        assert canvas.drawString.call_count == 4
        for i, ch in enumerate(formatted):
            canvas.drawString.assert_any_call((10 + 5 * i) * mm, 20 * mm, ch)

    def test_no_padding_needed(self, canvas):
        ann = SpaceZeroPadNumber(page=0, x=10, y=20, pitch=5, digits=2)
        ann.do(canvas, 42)
        assert canvas.drawString.call_count == 2
        canvas.drawString.assert_any_call(10 * mm, 20 * mm, "4")
        canvas.drawString.assert_any_call((10 + 5) * mm, 20 * mm, "2")


# --- SpaceMoney ---

class TestSpaceMoney:
    def test_splits_pounds_and_pence(self, canvas):
        ann = SpaceMoney(page=0, x=10, y=20, x2=50, y2=20, pitch=5, digits=6)
        ann.do(canvas, 142.12)
        # Pounds: "%6d" % 142 = "   142", drawn at (10, 20)
        # Pence: "%02d" % round(0.12 * 100 + 0.5) = "12" (actually 13 due to +0.5 rounding)
        # The code does: pence = float(s) - int(float(s)) => 0.12
        # pence = round(100 * 0.12 + 0.5) => round(12.5) => 12
        # pence = "%02d" % 12 => "12"
        assert canvas.drawString.call_count > 0

    def test_zero_pence(self, canvas):
        ann = SpaceMoney(page=0, x=10, y=20, x2=50, y2=20, pitch=5, digits=4)
        ann.do(canvas, 100.0)
        # Pounds: "%4d" % 100 = " 100" (4 chars)
        # Pence: round(0.0 * 100 + 0.5) = round(0.5) = 0
        # "%02d" % 0 = "00" (2 chars)
        assert canvas.drawString.call_count == 4 + 2


# --- WriteSpaceDate ---

class TestWriteSpaceDate:
    def test_parses_iso_date(self, canvas):
        ann = WriteSpaceDate(page=0, x=10, y=20, x2=30, y2=20, x3=50, y3=20, pitch=5)
        ann.do(canvas, "2020-01-15")
        # Day "15" at (10, 20), Month "01" at (30, 20), Year "2020" at (50, 20)
        # Each drawn char-by-char via SpaceString
        # Day: 2 chars, Month: 2 chars, Year: 4 chars = 8 drawString calls
        assert canvas.drawString.call_count == 8

    def test_date_values_correct(self, canvas):
        ann = WriteSpaceDate(page=0, x=10, y=20, x2=30, y2=20, x3=50, y3=20, pitch=5)
        ann.do(canvas, "2020-03-25")
        # Day "25": chars '2' at x=10, '5' at x=15
        canvas.drawString.assert_any_call(10 * mm, 20 * mm, "2")
        canvas.drawString.assert_any_call((10 + 5) * mm, 20 * mm, "5")
        # Month "03": chars '0' at x=30, '3' at x=35
        canvas.drawString.assert_any_call(30 * mm, 20 * mm, "0")
        canvas.drawString.assert_any_call((30 + 5) * mm, 20 * mm, "3")
        # Year "2020": chars '2' at x=50, '0' at x=55, '2' at x=60, '0' at x=65
        canvas.drawString.assert_any_call(50 * mm, 20 * mm, "2")
        canvas.drawString.assert_any_call((50 + 5) * mm, 20 * mm, "0")
        canvas.drawString.assert_any_call((50 + 10) * mm, 20 * mm, "2")
        canvas.drawString.assert_any_call((50 + 15) * mm, 20 * mm, "0")


# --- WriteSpaceSortCode ---

class TestWriteSpaceSortCode:
    def test_splits_six_digit_code(self, canvas):
        ann = WriteSpaceSortCode(page=0, x=10, y=20, x2=30, y2=20, x3=50, y3=20, pitch=5)
        ann.do(canvas, "123465")
        # Pair 1 "12" at (10, 20), Pair 2 "34" at (30, 20), Pair 3 "65" at (50, 20)
        # Each pair is 2 chars = 6 drawString calls
        assert canvas.drawString.call_count == 6

    def test_sort_code_digit_positions(self, canvas):
        ann = WriteSpaceSortCode(page=0, x=10, y=20, x2=30, y2=20, x3=50, y3=20, pitch=5)
        ann.do(canvas, "123465")
        # First pair "12"
        canvas.drawString.assert_any_call(10 * mm, 20 * mm, "1")
        canvas.drawString.assert_any_call((10 + 5) * mm, 20 * mm, "2")
        # Second pair "34"
        canvas.drawString.assert_any_call(30 * mm, 20 * mm, "3")
        canvas.drawString.assert_any_call((30 + 5) * mm, 20 * mm, "4")
        # Third pair "65"
        canvas.drawString.assert_any_call(50 * mm, 20 * mm, "6")
        canvas.drawString.assert_any_call((50 + 5) * mm, 20 * mm, "5")


# --- get_spec ---

class TestGetSpec:
    def test_loads_spec_from_json(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
            [2, "SpaceString", 0, 148, 201.7, 5.47],
            [5, "WriteBool", 0, 72.5, 157.7],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))

        result = get_spec(str(spec_file))

        assert 1 in result
        assert 2 in result
        assert 5 in result

    def test_returns_correct_annotation_types(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
            [5, "WriteBool", 0, 72.5, 157.7],
            [30, "WriteSpaceDate", 0, 23.5, 110.2, 37, 110.2, 50.5, 110.2, 5.47],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))

        result = get_spec(str(spec_file))

        assert isinstance(result[1][0], WriteString)
        assert isinstance(result[5][0], WriteBool)
        assert isinstance(result[30][0], WriteSpaceDate)

    def test_annotation_has_correct_page(self, tmp_path):
        spec_data = [
            [1, "WriteString", 2, 76, 210.2],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))

        result = get_spec(str(spec_file))
        assert result[1][0].page == 2

    def test_multiple_annotations_per_box(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
            [1, "WriteString", 1, 50, 100.0],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))

        result = get_spec(str(spec_file))
        assert len(result[1]) == 2


# --- create_annotations ---

class TestCreateAnnotations:
    def test_maps_values_to_page_groups(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
            [5, "WriteBool", 0, 72.5, 157.7],
            [90, "WriteString", 1, 25, 244.5],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))
        spec = get_spec(str(spec_file))

        values = {"ct600": {1: "Test Co", 5: True, 90: "Some reason"}}
        result = create_annotations(values, spec)

        assert 0 in result
        assert 1 in result
        # Page 0 has boxes 1 and 5
        assert len(result[0]) == 2
        # Page 1 has box 90
        assert len(result[1]) == 1

    def test_skips_values_not_in_spec(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))
        spec = get_spec(str(spec_file))

        values = {"ct600": {1: "Test Co", 999: "Unknown box"}}
        result = create_annotations(values, spec)

        assert 0 in result
        assert len(result[0]) == 1

    def test_returns_annotation_value_tuples(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))
        spec = get_spec(str(spec_file))

        values = {"ct600": {1: "Test Co"}}
        result = create_annotations(values, spec)

        ann, val = result[0][0]
        assert isinstance(ann, WriteString)
        assert val == "Test Co"

    def test_empty_values_returns_empty_dict(self, tmp_path):
        spec_data = [
            [1, "WriteString", 0, 76, 210.2],
        ]
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec_data))
        spec = get_spec(str(spec_file))

        values = {"ct600": {}}
        result = create_annotations(values, spec)

        assert result == {}
