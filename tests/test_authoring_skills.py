"""Contrats légers des deux skills de rédaction ; aucune connexion distante requise."""

import json
import re
import unittest
from pathlib import Path

from install import discover_skills


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("rustkins-docs", "rustkins-adr")


class AuthoringSkillsTests(unittest.TestCase):
    def test_installer_discovers_both_skills(self):
        available = {skill.name for skill in discover_skills()}
        self.assertTrue(set(SKILLS).issubset(available))

    def test_metadata_requirements_and_local_links(self):
        for name in SKILLS:
            with self.subTest(name=name):
                folder = ROOT / "skills" / name
                source = (folder / "SKILL.md").read_text(encoding="utf-8")
                lines = source.splitlines()
                self.assertEqual(lines[0], "---")
                self.assertEqual(lines[1], f"name: {name}")
                self.assertTrue(lines[2].startswith("description: "))
                self.assertIn("---", lines[3:])
                self.assertIn("references/", source)
                self.assertIn("python scripts/validate_docs.py", source)
                self.assertIn("RustkinsDocs", source)
                self.assertIn("PR", source)
                requirements = json.loads((folder / "requirements.json").read_text(encoding="utf-8"))
                self.assertEqual(requirements, {"commands": ["git", "gh"]})

        paths = [
            ROOT / "skills" / "rustkins-docs" / "SKILL.md",
            ROOT / "skills" / "rustkins-adr" / "SKILL.md",
            ROOT / "skills" / "rustkins-docs" / "references" / "document-workflow.md",
            ROOT / "skills" / "rustkins-adr" / "references" / "adr-workflow.md",
            ROOT / "docs" / "skills" / "rustkins-docs.md",
            ROOT / "docs" / "skills" / "rustkins-adr.md",
        ]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                source = path.read_text(encoding="utf-8")
                for href in re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", source):
                    if "://" in href or href.startswith("#"):
                        continue
                    relative = href.split("#", 1)[0]
                    if relative:
                        self.assertTrue(
                            (path.parent / relative).resolve().is_file(),
                            f"Lien local introuvable dans {path.relative_to(ROOT)} : {href}",
                        )

    def test_document_and_adr_workflow_boundaries(self):
        documents = (ROOT / "skills" / "rustkins-docs" / "SKILL.md").read_text(encoding="utf-8")
        decisions = (ROOT / "skills" / "rustkins-adr" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("runbook.schema.json", documents)
        self.assertIn("related_docs", documents)
        for required in ("status: proposed", "approved_by: []", "supersedes", "superseded"):
            self.assertIn(required, decisions)
        self.assertIn("rustkins-team", decisions)
        self.assertIn("rustkins-knowledge", documents)
        self.assertIn("rustkins-knowledge", decisions)


if __name__ == "__main__":
    unittest.main()
