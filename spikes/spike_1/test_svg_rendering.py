import pytest
import os
import tempfile
from pathlib import Path
from svg_renderer import SVGPreprocessor, DevopsSVGMobject
from manim import SVGMobject

@pytest.fixture
def sample_valid_svg(tmp_path):
    """Creates a basic raw SVG file with no nasty css/defs."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" fill="#F2F3F3"/>
<path d="M50 25L75 75H25L50 25Z" fill="#FF9900"/>
</svg>'''
    filepath = tmp_path / "valid.svg"
    filepath.write_text(svg_content)
    return filepath

@pytest.fixture
def sample_dirty_svg(tmp_path):
    """Creates a dirty SVG with embedded styles and defs that break Manim."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .cls-1{fill:#FF9900;}
      .cls-2{fill:#F2F3F3;}
    </style>
  </defs>
  <rect class="cls-2" width="100" height="100"/>
  <path class="cls-1" d="M50 25L75 75H25L50 25Z"/>
</svg>'''
    filepath = tmp_path / "dirty.svg"
    filepath.write_text(svg_content)
    return filepath


class TestSVGPreprocessor:
    def test_validate_input_svg_exists(self, sample_valid_svg):
        """Test validation passes for existing regular SVG."""
        preprocessor = SVGPreprocessor()
        assert preprocessor.validate_input_svg(sample_valid_svg) is True

    def test_validate_input_svg_missing(self):
        """Test validation fails if file doesn't exist."""
        preprocessor = SVGPreprocessor()
        assert preprocessor.validate_input_svg(Path("does_not_exist.svg")) is False

    def test_sanitize_svg_for_manim_cleans_dirty_css(self, sample_dirty_svg):
        """
        The core business logic test: 
        Ensure that when a dirty SVG with <style> tags is parsed, 
        it outputs a sanitized SVG where the 'class' attributes 
        are stripped and 'fill' is pushed directly into the <path> object.
        """
        preprocessor = SVGPreprocessor()
        clean_path = preprocessor.sanitize_svg_for_manim(sample_dirty_svg)
        
        assert clean_path.exists()
        
        cleaned_content = clean_path.read_text()
        
        # Ensure the styling was extracted and placed natively
        assert 'fill="#FF9900"' in cleaned_content
        assert 'fill="#F2F3F3"' in cleaned_content
        
        # Ensure the nasty tags are gone
        assert "<style>" not in cleaned_content
        assert "<defs>" not in cleaned_content
        assert "class=" not in cleaned_content


class TestDevopsSVGMobject:
    def test_init_sets_correct_paths(self, sample_dirty_svg):
        """Test the Devops wrapper successfully routes through the preprocessor."""
        devops_svg = DevopsSVGMobject(sample_dirty_svg)
        
        assert devops_svg.original_filepath == sample_dirty_svg
        assert devops_svg.sanitized_filepath is not None
        assert devops_svg.sanitized_filepath.exists()
        
    def test_render_creates_valid_manim_mobject(self, sample_dirty_svg):
        """
        Test that the final output from render() is 
        an actual Manim SVGMobject that won't crash the engine.
        """
        devops_svg = DevopsSVGMobject(sample_dirty_svg)
        result = devops_svg.render()
        
        # assert it successfully instantiated a manim Mobject
        assert isinstance(result, SVGMobject)

