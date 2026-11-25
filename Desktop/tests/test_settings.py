"""Settings round-trips: credentials and preferences serialize and parse back."""
import json
from dataclasses import asdict

from bluey.settings import Credentials, Preferences


def test_preferences_recover_from_corrupt_or_wrongly_typed_values(tmp_path):
    path = tmp_path / 'settings.json'
    path.write_text('{broken')
    assert Preferences.load(path) == Preferences()
    path.write_text(json.dumps({'cursor_size': -100, 'phone_position': 8.0, 'mood': 'invalid', 'glow': 'false'}))
    result = Preferences.load(path)
    assert result.cursor_size == 48
    assert result.phone_position == 1.0
    assert result.mood == 'listening'
    assert result.glow is False


def test_preferences_never_persist_control_consent_or_credentials(tmp_path):
    path = tmp_path / 'settings.json'
    prefs = Preferences(cursor_size=90, personality='Cheeky, please.')
    prefs.save(path)
    assert Preferences.load(path) == prefs
    assert 'computer_control' not in asdict(prefs)
    assert 'api_key' not in path.read_text()


def test_unavailable_keyring_uses_memory_only(monkeypatch):
    import keyring
    def unavailable(*args):
        raise RuntimeError('locked')
    monkeypatch.setattr(keyring, 'get_password', unavailable)
    monkeypatch.setattr(keyring, 'set_password', unavailable)
    credentials = Credentials()
    assert not credentials.set('sk-test-only')
    assert credentials.get() == 'sk-test-only'
    assert not credentials.persisted


def test_session_key_can_be_removed():
    credentials = Credentials(use_keyring=False)
    credentials.set('sk-test-only')
    credentials.clear()
    assert not credentials.get()


def test_save_is_atomic_and_leaves_no_temporary_file(tmp_path):
    # save() writes a sibling .tmp and os.replace()s it into place, so an
    # interrupted write can never leave a half-written settings.json - and
    # after a successful save the temporary file must be gone.
    path = tmp_path / 'settings.json'
    Preferences(cursor_size=96, personality='Calm.').save(path)
    assert path.exists()
    assert not path.with_suffix('.tmp').exists()
    assert json.loads(path.read_text())['cursor_size'] == 96

def test_non_finite_phone_position_falls_back(tmp_path):
    for value in ('NaN','Infinity','-Infinity'):
        path=tmp_path/'settings.json'
        path.write_text('{"phone_position":'+value+'}')
        assert Preferences.load(path).phone_position==0.5

def test_integer_phone_position_is_supported(tmp_path):
    path=tmp_path/'settings.json'
    for value in (0,1):
        path.write_text(json.dumps({'phone_position':value}))
        assert Preferences.load(path).phone_position==float(value)

def test_boolean_is_not_a_phone_position(tmp_path):
    path=tmp_path/'settings.json'
    path.write_text(json.dumps({'phone_position':True,'cursor_size':True}))
    result=Preferences.load(path)
    assert result.phone_position==0.5
    assert result.cursor_size==72

def test_preferences_ignore_non_object_json(tmp_path):
    path=tmp_path/'settings.json'
    for value in ('null','[]','42','"text"'):
        path.write_text(value)
        assert Preferences.load(path)==Preferences()

def test_personality_is_bounded_on_load(tmp_path):
    path=tmp_path/'settings.json'
    path.write_text(json.dumps({'personality':'x'*9000}))
    assert len(Preferences.load(path).personality)==8000

def test_missing_preferences_keep_defaults(tmp_path):
    assert Preferences.load(tmp_path/'missing.json')==Preferences()

def test_save_creates_nested_config_directory(tmp_path):
    path=tmp_path/'nested'/'profile'/'settings.json'
    Preferences(glow=True).save(path)
    assert Preferences.load(path).glow is True

def test_credentials_reject_whitespace_and_oversized_values():
    import pytest
    credentials=Credentials(use_keyring=False)
    for value in ('','  ','has space','has\nnewline','x'*1025):
        with pytest.raises(ValueError):
            credentials.set(value)
        assert credentials.get()=='' 

def test_provider_detection_trims_surrounding_whitespace():
    from bluey.settings import provider_for_key
    assert provider_for_key('  gsk_fixture  ')=='groq'
    assert provider_for_key('sk_fixture')=='openai' 

def test_cursor_size_clamps_both_ends(tmp_path):
    path=tmp_path/'settings.json'
    for value,expected in ((-99,48),(99999,120)):
        path.write_text(json.dumps({'cursor_size':value}))
        assert Preferences.load(path).cursor_size==expected

def test_failed_replace_preserves_old_preferences_and_cleans_temporary(tmp_path, monkeypatch):
    import pytest
    import bluey.settings as settings
    path = tmp_path / "settings.json"
    Preferences(personality="original").save(path)
    def fail(*args):
        raise OSError("simulated disk failure")
    monkeypatch.setattr(settings.os, "replace", fail)
    with pytest.raises(OSError):
        Preferences(personality="new").save(path)
    assert Preferences.load(path).personality == "original"
    assert list(tmp_path.iterdir()) == [path]


def test_concurrent_preference_saves_are_complete_and_leave_no_debris(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = tmp_path / "settings.json"
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda i: Preferences(personality=f"writer-{i}").save(path), range(40)))
    assert Preferences.load(path).personality.startswith("writer-")
    assert set(json.loads(path.read_text())) == set(asdict(Preferences()))
    assert list(tmp_path.iterdir()) == [path]


def test_invalid_float_save_leaves_existing_settings_intact(tmp_path):
    import pytest
    path = tmp_path / "settings.json"
    Preferences().save(path)
    with pytest.raises(ValueError):
        Preferences(phone_position=float("nan")).save(path)
    assert Preferences.load(path) == Preferences()
    assert list(tmp_path.iterdir()) == [path]


def test_credentials_reject_header_unsafe_bytes_without_replacing_session():
    import pytest
    credentials = Credentials(use_keyring=False)
    credentials.set("sk-existing")
    for value in ("sk-null\x00byte", "sk-del\x7f", "sk-é", "sk-zero\u200bwidth"):
        with pytest.raises(ValueError):
            credentials.set(value)
        assert credentials.get() == "sk-existing"


def test_clamp_helpers_hold_both_limits():
    from bluey.settings import clamp_cursor_size, clamp_phone_position
    assert clamp_cursor_size(10) == 48
    assert clamp_cursor_size(500) == 120
    assert clamp_cursor_size(72) == 72
    assert clamp_phone_position(-1) == 0.0
    assert clamp_phone_position(3) == 1.0
    assert clamp_phone_position(0.25) == 0.25


def test_with_updates_returns_a_clamped_copy():
    import pytest
    original = Preferences()
    changed = original.with_updates(cursor_size=999, phone_position=-2, mood='bogus', glow=True)
    assert (changed.cursor_size, changed.phone_position, changed.mood, changed.glow) == (120, 0.0, 'listening', True)
    assert original == Preferences()
    with pytest.raises(TypeError):
        original.with_updates(volume=3)


def test_diff_lists_only_changed_fields():
    base = Preferences()
    assert base.diff(Preferences()) == {}
    assert base.diff(base.with_updates(glow=True, mood='happy')) == {'glow': True, 'mood': 'happy'}


def test_preferences_json_round_trip_and_bad_input():
    prefs = Preferences().with_updates(cursor_size=90, personality='Calm', glow=True)
    assert Preferences.from_json(prefs.to_json()) == prefs
    assert Preferences.from_json('not json') == Preferences()
    assert Preferences.from_json('[1, 2]') == Preferences()
    assert Preferences.from_json('{"cursor_size": "big", "glow": true}') == Preferences(glow=True)
    assert 'api_key' not in prefs.to_json()


def test_next_mood_cycles_through_all_moods():
    from bluey.settings import MOODS, next_mood
    assert next_mood('listening') == 'resting'
    assert next_mood(MOODS[-1]) == MOODS[0]
    assert next_mood('???') == MOODS[0]
    seen, mood = [], MOODS[0]
    for _ in MOODS:
        seen.append(mood)
        mood = next_mood(mood)
    assert seen == list(MOODS) and mood == MOODS[0]
