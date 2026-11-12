#!/usr/bin/env bash
# Put an HTML file on the macOS clipboard as rich text (public.html) + plain text fallback,
# so that pasting into monday.com (or mail, Teams, Docs) keeps bold/italic/lists.
# Usage: clip_html.sh <file.html>
set -euo pipefail
f="${1:?usage: clip_html.sh <file.html>}"
[ -f "$f" ] || { echo "not found: $f" >&2; exit 1; }
abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
txt="$(mktemp)"
textutil -convert txt -format html -stdout "$abs" > "$txt"
osascript -l JavaScript - "$abs" "$txt" <<'JS' >/dev/null
function run(argv) {
  ObjC.import('AppKit');
  const html = $.NSString.stringWithContentsOfFileEncodingError(argv[0], 4, null);
  const txt = $.NSString.stringWithContentsOfFileEncodingError(argv[1], 4, null);
  const pb = $.NSPasteboard.generalPasteboard;
  pb.clearContents;
  pb.setStringForType(html, 'public.html');
  pb.setStringForType(txt, 'public.utf8-plain-text');
  return 'ok';
}
JS
rm -f "$txt"
echo "on clipboard: $(pbpaste | head -1) …"
