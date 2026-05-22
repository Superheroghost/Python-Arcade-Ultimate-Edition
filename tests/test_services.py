import tempfile
import unittest
from pathlib import Path

from arcade_ue.services import ProfileService, SettingsService


class ServiceTests(unittest.TestCase):
    def test_settings_persist_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            service = SettingsService(settings_path=path)
            service.load()
            service.values["volume"] = 0.9
            service.save()

            loaded = SettingsService(settings_path=path)
            loaded.load()
            self.assertEqual(loaded.values["volume"], 0.9)

    def test_profile_records_high_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            profile = ProfileService(profile_path=path)
            profile.load()
            profile.record_score("breakout", 120)
            profile.record_score("breakout", 100)
            self.assertEqual(profile.values["high_scores"]["breakout"], 120)


if __name__ == "__main__":
    unittest.main()
