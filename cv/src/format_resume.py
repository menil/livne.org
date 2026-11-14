#!/usr/bin/env python3
"""Normalize a resume YAML file to the canonical format while preserving YAML anchors.

Usage:
    python -m src.format_resume [PATH]           # rewrite in place
    python -m src.format_resume [PATH] --check   # fail if not canonical
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

import yaml
from yaml.composer import ComposerError
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

RESUME_PATH = Path(__file__).resolve().parent.parent / "resources" / "cv.yaml"


class _AnchorPreservingLoader(SafeLoader):  # type: ignore[misc]
    """YAML SafeLoader that retains original anchor names on composed nodes."""

    def compose_node(self, parent: Node | None, index: Node | int | None) -> Node | None:
        """Compose a YAML node while storing its user-defined anchor name."""
        if self.check_event(yaml.AliasEvent):
            event = self.get_event()
            anchor = event.anchor
            if anchor not in self.anchors:
                raise ComposerError(
                    None,
                    None,
                    f"found undefined alias {anchor!r}",
                    event.start_mark,
                )
            return cast("Node", self.anchors[anchor])
        event = self.peek_event()
        anchor = event.anchor
        node = cast("Node | None", super().compose_node(parent, index))
        if node is not None and anchor is not None:
            setattr(node, "_anchor_name", anchor)
        return node


class _AnchorPreservingDumper(SafeDumper):  # type: ignore[misc]
    """YAML SafeDumper that emits original anchor names when present."""

    def generate_anchor(self, node: Node) -> str:
        """Return the original anchor name if recorded, otherwise generate one."""
        anchor_name = getattr(node, "_anchor_name", None)
        if isinstance(anchor_name, str):
            return anchor_name
        return cast("str", super().generate_anchor(node))


def _normalize_styles(node: Node, visited: set[int] | None = None) -> None:
    """Reset scalar quoting and collection flow styles to PyYAML canonical defaults."""
    if visited is None:
        visited = set()
    node_id = id(node)
    if node_id in visited:
        return
    visited.add(node_id)

    if isinstance(node, ScalarNode):
        node.style = None
        if "\n" in node.value:
            node.value = node.value.rstrip("\n")
    elif isinstance(node, SequenceNode):
        node.flow_style = False
        for item in node.value:
            _normalize_styles(item, visited)
    elif isinstance(node, MappingNode):
        node.flow_style = False
        for key_node, val_node in node.value:
            _normalize_styles(key_node, visited)
            _normalize_styles(val_node, visited)


def render_canonical_yaml(yaml_content: str) -> str:
    """Parse and serialize YAML content into canonical format, preserving anchors."""
    node = yaml.compose(yaml_content, Loader=_AnchorPreservingLoader)
    if node is None:
        return ""
    _normalize_styles(node)
    result: str = yaml.serialize(
        node,
        Dumper=_AnchorPreservingDumper,
        allow_unicode=True,
    )
    return result


def resume_yaml_is_canonical(path: str | Path) -> bool:
    """Return True if the resume YAML file at ``path`` is in canonical form."""
    file_path = Path(path)
    current = file_path.read_text(encoding="utf-8")
    return current == render_canonical_yaml(current)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for formatting or checking a resume YAML file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=RESUME_PATH,
        type=Path,
        help="Resume YAML file to normalize (default: resources/cv.yaml).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify canonical formatting without writing (exit 1 if not canonical).",
    )
    args = parser.parse_args(argv)

    resume_path: Path = args.path
    current = resume_path.read_text(encoding="utf-8")
    canonical = render_canonical_yaml(current)

    if args.check:
        if current != canonical:
            print(
                f"{resume_path} is not in canonical format; "
                "run `just format-resume` and commit the result."
            )
            return 1
        print(f"{resume_path} is in canonical format.")
        return 0

    if current != canonical:
        resume_path.write_text(canonical, encoding="utf-8")
        print(f"Normalized {resume_path}.")
    else:
        print(f"{resume_path} already canonical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
