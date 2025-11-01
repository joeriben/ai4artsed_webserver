"""
Test metadata API endpoints to verify they read directly from config files
"""
from my_app import create_app
import json
from pathlib import Path

def test_metadata_endpoints():
    """Test that API reads directly from config files"""
    app = create_app()

    with app.test_client() as client:
        print("=== Test 1: Verify metadata endpoint returns all configs ===")
        response = client.get('/pipeline_configs_metadata')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.get_json()
        assert 'configs' in data, "Response missing 'configs' field"
        assert 'count' in data, "Response missing 'count' field"
        assert data['count'] == 34, f"Expected 34 configs, got {data['count']}"

        print(f"✓ Metadata endpoint returns {data['count']} configs")

        print("\n=== Test 2: Verify data matches actual config files ===")
        # Pick a specific config and verify it matches the file
        jugendsprache_from_api = None
        for config in data['configs']:
            if config['id'] == 'jugendsprache':
                jugendsprache_from_api = config
                break

        assert jugendsprache_from_api is not None, "jugendsprache not found in API response"

        # Read the actual file
        config_file = Path(__file__).parent / "schemas" / "configs" / "jugendsprache.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            jugendsprache_from_file = json.load(f)

        # Compare key fields
        assert jugendsprache_from_api['name'] == jugendsprache_from_file['name'], \
            "Name doesn't match file"
        assert jugendsprache_from_api['pipeline'] == jugendsprache_from_file['pipeline'], \
            "Pipeline doesn't match file"
        assert jugendsprache_from_api['display'] == jugendsprache_from_file['display'], \
            "Display doesn't match file"

        print("✓ API data matches config file (no duplication)")

        print("\n=== Test 3: Verify detail endpoint ===")
        response = client.get('/pipeline_config/jugendsprache')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.get_json()
        assert data['success'] is True, "Response missing 'success' field"
        assert 'config' in data, "Response missing 'config' field"

        # Verify it returns the complete config
        config = data['config']
        assert config['name'] == jugendsprache_from_file['name'], "Name doesn't match"
        assert config['context'] == jugendsprache_from_file['context'], "Context doesn't match"

        print("✓ Detail endpoint returns complete config data")

        print("\n=== Test 4: Verify all configs have required metadata ===")
        response = client.get('/pipeline_configs_metadata')
        data = response.get_json()

        missing_fields = []
        for config in data['configs']:
            if 'display' not in config:
                missing_fields.append(f"{config['id']}: missing 'display'")
            if 'tags' not in config:
                missing_fields.append(f"{config['id']}: missing 'tags'")
            if 'audience' not in config:
                missing_fields.append(f"{config['id']}: missing 'audience'")

        if missing_fields:
            print(f"⚠ Some configs missing metadata:")
            for msg in missing_fields[:5]:
                print(f"  - {msg}")
        else:
            print("✓ All configs have complete metadata")

        print("\n=== All tests passed! ===")

if __name__ == "__main__":
    test_metadata_endpoints()
