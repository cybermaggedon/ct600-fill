import io
import json

import pytest

from ct600_fill.annotations import (
    get_spec,
    create_annotations,
    get_page,
    WriteString,
    WriteBool,
    SpaceString,
    SpacePounds,
    WriteSpaceDate,
)


@pytest.fixture
def mini_spec(tmp_path):
    spec_data = [
        [1, "WriteString", 0, 76, 210.2],
        [2, "SpaceString", 0, 148, 201.7, 5.47],
        [5, "WriteBool", 0, 72.5, 157.7],
        [30, "WriteSpaceDate", 0, 23.5, 110.2, 37, 110.2, 50.5, 110.2, 5.47],
        [145, "SpacePounds", 1, 79, 93.0, 5.5, 18],
        [90, "WriteString", 1, 25, 244.5],
    ]
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(spec_data))
    return str(spec_file)


@pytest.fixture
def sample_values():
    return {
        "ct600": {
            1: "Test Company Ltd",
            2: "12345678",
            5: True,
            30: "2020-06-15",
            145: 11218.0,
            90: "Dog ate the accounts",
        }
    }


class TestSpecToAnnotationsPipeline:
    def test_get_spec_output_feeds_into_create_annotations(self, mini_spec, sample_values):
        spec = get_spec(mini_spec)
        annotations = create_annotations(sample_values, spec)

        assert isinstance(annotations, dict)
        assert 0 in annotations
        assert 1 in annotations

    def test_create_annotations_produces_valid_page_dict(self, mini_spec, sample_values):
        spec = get_spec(mini_spec)
        annotations = create_annotations(sample_values, spec)

        for page_num, page_annotations in annotations.items():
            assert isinstance(page_num, int)
            assert isinstance(page_annotations, list)
            for ann, val in page_annotations:
                assert hasattr(ann, "do")
                assert hasattr(ann, "page")
                assert ann.page == page_num

    def test_annotations_preserve_values(self, mini_spec, sample_values):
        spec = get_spec(mini_spec)
        annotations = create_annotations(sample_values, spec)

        values_found = [val for page_anns in annotations.values() for _, val in page_anns]
        assert "Test Company Ltd" in values_found
        assert True in values_found
        assert 11218.0 in values_found


class TestAnnotationsToPagePipeline:
    def test_get_page_produces_non_empty_pdf(self, mini_spec, sample_values):
        spec = get_spec(mini_spec)
        annotations = create_annotations(sample_values, spec)

        buffer = get_page(annotations, 0)

        assert isinstance(buffer, io.BytesIO)
        content = buffer.read()
        assert len(content) > 0
        assert content[:5] == b"%PDF-"

    def test_get_page_works_for_each_page(self, mini_spec, sample_values):
        spec = get_spec(mini_spec)
        annotations = create_annotations(sample_values, spec)

        for page_num in annotations:
            buffer = get_page(annotations, page_num)
            content = buffer.read()
            assert len(content) > 0
            assert content[:5] == b"%PDF-"

    def test_full_pipeline_spec_to_pdf(self, mini_spec, sample_values):
        spec = get_spec(mini_spec)
        annotations = create_annotations(sample_values, spec)

        buffers = {}
        for page_num in annotations:
            buffers[page_num] = get_page(annotations, page_num)

        assert len(buffers) == 2
        for page_num, buf in buffers.items():
            assert buf.read()[:5] == b"%PDF-"
