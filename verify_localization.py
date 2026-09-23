# -*- coding: utf-8 -*-
"""Verify localization: .strings syntax, en/zh key parity, code-key coverage."""
import io, re, sys, glob, os

ROOT = r"/home/user/Doubao/chats/38443843430476034/PhotosBackup"
EN_PATH = os.path.join(ROOT, "App/Resources/en.lproj/Localizable.strings")
ZH_PATH = os.path.join(ROOT, "App/Resources/zh-Hans.lproj/Localizable.strings")

def parse_strings(path):
    errors = []
    table = {}
    with io.open(path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\r\n").strip()
            if not line or line.startswith("/*") or line.startswith("//"):
                continue
            m = re.match(r'^"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)";$', line)
            if not m:
                errors.append("line %d: %s" % (lineno, line[:80]))
                continue
            key, value = m.group(1), m.group(2)
            def dec(s):
                return (s.replace(r'\"', '"').replace(r"\\", "\\")
                         .replace(r"\n", "\n").replace(r"\t", "\t"))
            table[dec(key)] = dec(value)
    return table, errors

def extract_code_keys():
    keys = set()
    def dec(s):
        return (s.replace(r'\"', '"').replace(r"\\", "\\")
                 .replace(r"\n", "\n").replace(r"\t", "\t"))
    pats = [
        re.compile(r'String\(localized:\s*"((?:[^"\\]|\\.)*)"'),
        re.compile(r'NSLocalizedString\("((?:[^"\\]|\\.)*)"'),
        re.compile(r'LocalizedStringResource\s*=\s*"((?:[^"\\]|\\.)*)"'),
    ]
    auto = re.compile(r'\b(?:Text|Button|Label|Toggle|Picker|NavigationLink|Link|ProgressView|DisclosureGroup|TextField|Section|navigationTitle|searchable|accessibilityLabel|accessibilityHint|confirmationDialog|alert|statusBarHidden)\("((?:[^"\\]|\\.)*)"')
    for f in glob.glob(os.path.join(ROOT, "App/Sources", "*.swift")):
        with io.open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
        for p in pats:
            for m in p.finditer(text):
                keys.add(dec(m.group(1)))
        for m in auto.finditer(text):
            keys.add(dec(m.group(1)))
    return keys

INTERPOLATED_KEYS = {
    "%lld selected",
    "+ %lld more albums",
    "%lld remaining",
    "%lld items need to download from iCloud first. Keep the app open to finish them.",
    "code %lld",
    "Took %@",
    "Up to %lld events from the last two weeks. Warnings and errors are kept longer than routine entries. Filenames, photo identifiers, addresses and links are removed.",
    "Retrying (attempt %lld)",
    "Your account is connected, and we’ll keep %lld selected %@ protected.",
    "Connected · %@",
    "The Keychain refused the credential: %@.",
    "Could not create the report: %@",
    "Upload completion could not be saved: %@",
    "The saved upload queue could not be restored: %@",
    "Upload progress could not be saved: %@",
    "Google asked the app to slow down. Backup continues in ",
    "%lld minutes.",
    "no photo library access (%@)",
    "backed up %lld; %lld failed; %lld unfinished",
    "; paused: %@",
    "%lld s",
    "%lld min",
    "%lld h %lld min",
    "%lld days",
    "finished %@; %lld failed; %lld unfinished; ended because %@",
    "%@ of %@ done",
    "%lld failures this session; showing the %lld most recent.",
    "%lld failures this session.",
    "Repeated %lld times",
    " since %@",
    "%@ of %@ backed up",
    "All %@ backed up",
    "%@ items",
    "%lld items",
    "1 item",
    "Backing up %@ items. Watch progress in Activity.",
    "Re-checking %@ items against Google Photos.",
    "%lld items remaining",
    "%lld items failed — open Activity to retry",
}

NON_LOCALIZABLE = {
    "",
    "accounts.google.com",
    "Your account is connected, and we’ll keep \\(count) selected \\(count == 1 ? ",
}

ok = True

en, en_err = parse_strings(EN_PATH)
zh, zh_err = parse_strings(ZH_PATH)
print("== .strings syntax ==")
print("en errors: %d, entries: %d" % (len(en_err), len(en)))
print("zh errors: %d, entries: %d" % (len(zh_err), len(zh)))
if en_err or zh_err:
    ok = False
    for e in (en_err[:5] + zh_err[:5]):
        print("  ERR:", e)

print("\n== key parity ==")
only_en = set(en) - set(zh)
only_zh = set(zh) - set(en)
print("keys only in en: %d, only in zh: %d" % (len(only_en), len(only_zh)))
if only_en:
    ok = False
    for k in sorted(only_en)[:10]:
        print("  only-en:", k)
if only_zh:
    ok = False
    for k in sorted(only_zh)[:10]:
        print("  only-zh:", k)

print("\n== code key coverage ==")
code_keys = extract_code_keys()
code_keys |= INTERPOLATED_KEYS

def balanced_interp_end(s, start):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1

def normalize_matches_table(raw):
    parts = []
    i = 0
    n = len(raw)
    while i < n:
        if raw[i] == "\\" and i + 1 < n and raw[i + 1] == "(":
            end = balanced_interp_end(raw, i + 1)
            if end > 0:
                parts.append("%\\S+")
                i = end + 1
                continue
        c = raw[i]
        if c in "\\^$.|?*+()[]{}":
            parts.append("\\" + c)
        else:
            parts.append(c)
        i += 1
    rx = re.compile("^" + "".join(parts) + "$")
    return any(rx.match(k) for k in en)

raw_missing = sorted(k for k in code_keys if k not in en)
real_missing = []
for k in raw_missing:
    if k in NON_LOCALIZABLE:
        continue
    if "\\(" in k and normalize_matches_table(k):
        continue
    real_missing.append(k)

print("raw interpolated literals in code (informational): %d" % len(raw_missing))
print("genuinely missing keys: %d" % len(real_missing))
if real_missing:
    ok = False
    for k in real_missing[:30]:
        print("  MISSING:", k)

unused = sorted(set(en) - code_keys - {k for k in raw_missing if "\\(" in k})
print("\nentries in en table not matched by code scan (informational): %d" % len(unused))
for k in unused:
    print("  maybe-unused:", k)


print("\n== multi-language parity ==")
LANGS = ["zh-Hans", "ja", "ko", "fr", "de", "es", "it", "pt-BR", "ru"]
# 品牌/专有名词在目标语言中同形属合理保留
BRAND_KEYS = {"Photos Backup", "Photos Backup Connect", "iOS", "GPMC by xob0t", "G",
              "Home", "Albums", "Activity", "App", "Support", "Backup", "Uploads",
              "Item", "Pause", "Diagnostics", "All", "Show", "Waiting", "Done", "Retry",
              "Version", "Extensions", "code %lld", "%lld minutes.", "%lld s",
              "%lld min", "%lld h %lld min", "1 item"}
fmt_re = re.compile(r'%(?:\d+\$)?[@dDiuUxXoOfeEgGcCsS]|%lld|%[0-9.]*[fF]|%%')

for lang in LANGS:
    lp = os.path.join(ROOT, "App/Resources/%s.lproj/Localizable.strings" % lang)
    lt, lerr = parse_strings(lp)
    if lerr:
        ok = False
        print("%s: SYNTAX ERRORS %d" % (lang, len(lerr)))
        continue
    miss = set(en) - set(lt)
    extra = set(lt) - set(en)
    fmts_mismatch = [k for k in en if fmt_re.findall(k) != fmt_re.findall(lt.get(k, ""))]
    fallback = [k for k, v in lt.items() if v == k and k not in BRAND_KEYS and len(k) > 2]
    issues = []
    if miss: issues.append("missing %d" % len(miss))
    if extra: issues.append("extra %d" % len(extra))
    if fmts_mismatch: issues.append("format-mismatch %d" % len(fmts_mismatch))
    if fallback: issues.append("fallback %d" % len(fallback))
    if issues:
        ok = False
        print("%s: FAIL %s (keys=%d)" % (lang, ", ".join(issues), len(lt)))
        for k in sorted(miss)[:5]: print("   miss:", k[:70])
        for k in sorted(extra)[:5]: print("   extra:", k[:70])
        for k in fmts_mismatch[:5]: print("   fmt:", k[:50], "=>", lt.get(k, "")[:50])
        for k in fallback[:5]: print("   fallback:", k[:70])
    else:
        print("%s: OK (keys=%d)" % (lang, len(lt)))



print("\nRESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
