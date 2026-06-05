import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "harness_collect.py"


class HarnessCollectCliTest(unittest.TestCase):
    def test_version_exits_zero_without_json_collection(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip()
        self.assertRegex(output, r"^harness_collect\.py \d+\.\d+\.\d+$")
        self.assertFalse(output.startswith("{"), output)
        self.assertNotIn('"collected_at"', output)


if __name__ == "__main__":
    unittest.main()
