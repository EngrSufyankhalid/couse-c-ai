"""Offline regression checks; run with python -m unittest discover -s tests."""
import importlib.util
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mission02", ROOT / "mission-02/04_fst_noisy_simulator_starter.py")
MISSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MISSION)


class DialogueTests(unittest.TestCase):
    def setUp(self):
        self.fst = MISSION.FSTDialogueManager()
        for text in ("Hello", "Proxima Centauri", "Warp 7", "CLEARANCE-ALPHA-9"):
            self.fst.process_utterance(text)

    def test_confirmation_requires_explicit_consent(self):
        for text in ("not YES", "yesterday", "YES NO", "", "yes, but wait"):
            self.fst.process_utterance(text)
            self.assertEqual(self.fst.state, "CONFIRMATION")
        self.fst.process_utterance(" yes ")
        self.assertEqual(self.fst.state, "TERMINAL")

    def test_cancel_and_restart_clear_slots(self):
        self.fst.process_utterance("NO")
        self.assertEqual(self.fst.state, "FALLBACK")
        self.fst.process_utterance("RESTART")
        self.assertEqual(self.fst.state, "GREETING")
        self.assertEqual(self.fst.slot_memory, {})

    def test_invalid_slots_can_be_retried(self):
        self.fst.process_utterance("RESTART")
        self.fst.process_utterance("  ")
        self.assertEqual(self.fst.state, "GREETING")
        self.fst.process_utterance("Mars")
        for speed in ("Warp 0", "Warp 99", "fast"):
            self.fst.process_utterance(speed)
            self.assertNotIn("speed", self.fst.slot_memory)
        self.fst.process_utterance("Warp 3")
        self.fst.process_utterance("anything")
        self.assertNotIn("clearance", self.fst.slot_memory)
        self.fst.process_utterance("CLEARANCE-BETA-2")
        self.assertEqual(self.fst.state, "CONFIRMATION")


class ChannelTests(unittest.TestCase):
    def test_substitution_and_bandwidth(self):
        for length in range(1, 12):
            source = [f"word{i}" for i in range(length)]
            for seed in range(10):
                channel = MISSION.NoisyChannelSimulator("test", seed=seed)
                output = channel.apply_channel_constraints(" ".join(source)).split()
                self.assertEqual(len(output), min(length, 7))
                self.assertEqual(sum(a != b for a, b in zip(source, output)), 1)
                self.assertTrue(any(w in channel.NOISE_VOCAB for w in output))

    def test_seed_reproducibility_and_empty_input(self):
        state = random.getstate()
        a = MISSION.NoisyChannelSimulator("test", seed=42)
        b = MISSION.NoisyChannelSimulator("test", seed=42)
        self.assertEqual(a.apply_channel_constraints("one two three"),
                         b.apply_channel_constraints("one two three"))
        self.assertEqual(a.apply_channel_constraints("  "), "")
        self.assertEqual(random.getstate(), state)


class CliTests(unittest.TestCase):
    def test_invalid_options_fail_before_execution(self):
        for args in (("--rounds", "0"), ("--max-turns", "-1"),
                     ("--max-refinements", "-1"), ("--debate-providers", "invalid"),
                     ("--debate-providers", "mock,mock")):
            result = subprocess.run(
                [sys.executable, str(ROOT / "mission-01/04_dialogic_engine.py"), *args],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
