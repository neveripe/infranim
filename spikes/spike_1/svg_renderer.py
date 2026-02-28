import os
import re
import tempfile
import uuid
from pathlib import Path
from manim import SVGMobject

class SVGPreprocessor:
    """
    A minimal preprocessor to strip problematic CSS <style> tags 
    from complex SVGs and inline the fills/strokes so Manim's XML parser 
    doesn't crash.
    """
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "manim_devops_spikes"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def validate_input_svg(self, filepath: Path) -> bool:
        """Validates that the file exists and is actually an SVG."""
        return filepath.exists() and filepath.suffix.lower() == '.svg'

    def sanitize_svg_for_manim(self, filepath: Path) -> Path:
        """
        Reads the SVG, extracts <style> class definitions,
        inlines those definitions directly into the <path>/<rect> elements,
        and removes the <defs>/<style> blocks entirely.
        """
        if not self.validate_input_svg(filepath):
            raise FileNotFoundError(f"SVG not found at {filepath}")

        content = filepath.read_text()

        # 1. Extract CSS class styles: e.g. .cls-1{fill:#FF9900;}
        # Returns a dict: {'cls-1': 'fill="#FF9900"', 'cls-2': 'fill="#F2F3F3"'}
        style_pattern = re.compile(r'\.(\w[a-zA-Z0-9_\-]*)\s*\{\s*([^{}]*)\s*\}')
        styles = {}
        for match in style_pattern.finditer(content):
            class_name = match.group(1)
            raw_rules = match.group(2)
            
            # Convert CSS rules like `fill:#FF9900;` to XML attributes `fill="#FF9900"`
            attr_string = []
            for rule in raw_rules.split(';'):
                if ':' in rule:
                    key, val = rule.split(':', 1)
                    attr_string.append(f'{key.strip()}="{val.strip()}"')
            
            styles[class_name] = " ".join(attr_string)

        # 2. Inline the styles by replacing `class="cls-1"` with `fill="#FF9900"`
        for class_name, attr_string in styles.items():
            class_pattern = re.compile(fr'class=[\'"]{class_name}[\'"]')
            content = class_pattern.sub(attr_string, content)

        # 3. Strip out entirely the nasty <style> and <defs> blocks that crash Manim
        content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<defs>.*?</defs>', '', content, flags=re.DOTALL)

        # Write sanitized content to temp file safely
        safe_filename = f"sanitized_{uuid.uuid4().hex[:8]}.svg"
        clean_path = self.temp_dir / safe_filename
        clean_path.write_text(content)
        
        return clean_path


class DevopsSVGMobject:
    """
    A wrapper standardizing the ingestion of SVGs for Manim rendering.
    """
    def __init__(self, filepath: Path):
        self.original_filepath = filepath
        self.preprocessor = SVGPreprocessor()
        
        # We sanitize instantly upon creation
        self.sanitized_filepath = self.preprocessor.sanitize_svg_for_manim(self.original_filepath)
        self.manim_mobject = None

    def render(self) -> SVGMobject:
        """Loads the sanitized SVG into Manim's pipeline."""
        self.manim_mobject = SVGMobject(str(self.sanitized_filepath))
        return self.manim_mobject
