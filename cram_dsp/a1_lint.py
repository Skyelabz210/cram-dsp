"""A1 lint: static compliance scan of the CRAM-DF package.

Flags, per file:
  - float literals (ast.Constant with float value)
  - true division `/` (ast.Div) — only `//`, `%`, `>>` are A1-legal
  - float dtype names (float, float32, float64, np.float*, astype(float), hypot, exp)
`baseline_float.py` is quarantined by design and reported separately.
"""

import ast
import os
import sys

FLOAT_NAMES = {"float", "float16", "float32", "float64", "double",
               "hypot", "exp", "linalg", "lstsq"}
QUARANTINE = {"baseline_float.py"}
SELF = {"a1_lint.py"}  # the detector must name its target type


def scan_file(path):
    with open(path, "r", encoding="utf8") as f:
        tree = ast.parse(f.read(), filename=path)
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            issues.append((node.lineno, f"float literal {node.value!r}"))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            issues.append((node.lineno, "true division '/'"))
        if isinstance(node, ast.Name) and node.id in FLOAT_NAMES:
            issues.append((node.lineno, f"float name '{node.id}'"))
        if isinstance(node, ast.Attribute) and node.attr in FLOAT_NAMES:
            issues.append((node.lineno, f"float attribute '.{node.attr}'"))
    return issues


def scan_package(pkg_dir):
    report = {}
    for name in sorted(os.listdir(pkg_dir)):
        if not name.endswith(".py"):
            continue
        issues = scan_file(os.path.join(pkg_dir, name))
        report[name] = {
            "quarantined": name in QUARANTINE,
            "issues": issues,
        }
    return report


def main(pkg_dir):
    report = scan_package(pkg_dir)
    clean = True
    lines = []
    for name, info in report.items():
        tag = "QUARANTINED (classical foil, float by design)" if info["quarantined"] else ""
        if info["quarantined"]:
            lines.append(f"  {name}: {len(info['issues'])} float sites — {tag}")
            continue
        if name in SELF:
            lines.append(f"  {name}: {len(info['issues'])} self-references "
                         f"(the detector names its target) — exempt")
            continue
        if info["issues"]:
            clean = False
            lines.append(f"  {name}: A1 VIOLATIONS:")
            for ln, msg in info["issues"]:
                lines.append(f"    line {ln}: {msg}")
        else:
            lines.append(f"  {name}: A1 CLEAN")
    verdict = "A1 LINT: PASS (all production files clean)" if clean else "A1 LINT: FAIL"
    return verdict, lines


if __name__ == "__main__":
    verdict, lines = main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
    print(verdict)
    print("\n".join(lines))
