# DeepSentinel USENIX Draft

This directory contains a USENIX-formatted version of the DeepSentinel draft.

Files:

- `deepsentinel_usenix_draft.tex`: paper source using the official USENIX
  LaTeX style.
- `deepsentinel_usenix_draft.pdf`: compiled PDF.
- `usenix-2020-09.sty`: official USENIX LaTeX style downloaded from USENIX
  author resources.
- `usenix_template.tex`: official USENIX example template downloaded from
  USENIX author resources.
- `deepsentinel.bib`: bibliography copied from the AAAI draft.

Compile from this directory with:

```bash
latexmk -pdf -interaction=nonstopmode deepsentinel_usenix_draft.tex
```
