# Offline documentation checker

Validate small documentation repositories before publication. Python 3.10+; standard library only; no network requests or document execution.

From a clone of this repository:

```sh
python tools/check_docs.py --root .
python -m unittest discover -s tests -v
```

Reuse in another repository by copying `check_docs.py` and keeping the accompanying [MIT license](LICENSE):

```sh
python /path/to/check_docs.py --root /path/to/your-repository
```

## Checks

- UTF-8 Markdown, SVG and JSON files, recursively.
- Local Markdown links, reference definitions and HTML image sources: targets must exist inside the repository. URL-encoded paths, fragments and query strings are handled.
- Unclosed fenced code blocks; fenced and inline examples are excluded from link checking.
- SVG XML syntax and selected unsupported content: scripts, event attributes, foreign objects, document/entity declarations and external references.
- JSON syntax.

Exit status is `0` on success and `1` on validation errors. Errors name the source document. `.git`, virtual environments, `node_modules` and `__pycache__` are excluded; directory symlinks are not followed.

## Limits

This is a lightweight publishing check, not a complete Markdown parser or SVG sanitizer. Complex Markdown syntax can require manual inspection. Remote URL availability, fragment target names, JSON Schema contracts, application behavior and secrets are not checked. Only common Markdown links and HTML image `src` attributes are inspected; other HTML references are outside scope. Review untrusted artwork before use.

## License

[MIT](LICENSE) covers this new generic checker and its unit tests. Product documentation, artwork, trademarks and business implementations are outside that license.
