from pathlib import Path
import tempfile
import unittest

from tools.check_docs import check_repository


class DocumentationChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')

    def test_valid_encoded_local_path_with_query_and_fragment(self):
        self.write('README.md', '# Inicio\n[Guía](docs/gu%C3%ADa%20corta.md?v=1#pasos)\n')
        self.write('docs/guía corta.md', '# Pasos\n')
        self.assertEqual(check_repository(self.root), [])

    def test_missing_link_is_reported_without_remote_requests(self):
        self.write('README.md', '# Inicio\n[Ausente](docs/missing.md)\n[Web](https://example.org)\n')
        self.assertTrue(any('missing.md' in error for error in check_repository(self.root)))

    def test_fenced_and_inline_code_examples_are_not_links(self):
        self.write('README.md', '# Inicio\n```markdown\n[Ejemplo](missing.md)\n```\n`[Código](missing.md)`\n')
        self.assertEqual(check_repository(self.root), [])

    def test_four_backtick_fence_keeps_three_backticks_as_example(self):
        self.write('README.md', '# Inicio\n````markdown\n```\n[Ejemplo](missing.md)\n```\n````\n')
        self.assertEqual(check_repository(self.root), [])

    def test_reference_links_and_html_images_are_checked(self):
        self.write('README.md', '# Inicio\n[Guía][guide]\n[guide]: docs/guide.md\n<img src="assets/missing.svg" />\n')
        errors=check_repository(self.root)
        self.assertTrue(any('guide.md' in error for error in errors))
        self.assertTrue(any('missing.svg' in error for error in errors))

    def test_repository_escape_is_rejected(self):
        self.write('README.md', '# Inicio\n[Fuera](../outside.md)\n')
        self.assertTrue(any('outside repository' in error for error in check_repository(self.root)))

    def test_fragment_and_mailto_links_do_not_require_files(self):
        self.write('README.md', '# Inicio\n[Sección](#inicio)\n[Correo](mailto:test@example.org)\n')
        self.assertEqual(check_repository(self.root), [])

    def test_unclosed_fence_is_reported(self):
        self.write('README.md', '# Inicio\n```python\nprint(1)\n')
        self.assertTrue(any('Unclosed code fence' in error for error in check_repository(self.root)))

    def test_valid_self_contained_svg(self):
        self.write('assets/cover.svg', '<svg xmlns="http://www.w3.org/2000/svg"><title>Portada</title><rect width="10" height="10"/></svg>')
        self.assertEqual(check_repository(self.root), [])

    def test_svg_active_content_and_remote_references_are_rejected(self):
        self.write('assets/cover.svg', '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>1</script><image href="https://example.org/image.png"/></svg>')
        errors=check_repository(self.root)
        self.assertTrue(any('Active SVG content' in error for error in errors))
        self.assertTrue(any('External SVG reference' in error for error in errors))

    def test_malformed_svg_and_json_are_reported(self):
        self.write('assets/cover.svg','<svg>')
        self.write('examples/profile.json','{"missing":}')
        errors=check_repository(self.root)
        self.assertTrue(any('Invalid SVG' in error for error in errors))
        self.assertTrue(any('Invalid JSON' in error for error in errors))

    def test_git_internal_files_are_ignored(self):
        self.write('.git/private.json','not JSON')
        self.write('README.md','# Inicio\n')
        self.assertEqual(check_repository(self.root), [])

    def test_nonstandard_json_constants_are_rejected(self):
        for constant in ['NaN', 'Infinity', '-Infinity']:
            with self.subTest(constant=constant):
                self.write('example.json', '{"value":' + constant + '}')
                self.assertTrue(any('Invalid JSON' in error for error in check_repository(self.root)))


if __name__ == '__main__':
    unittest.main()
