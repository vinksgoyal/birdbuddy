from pathlib import Path


def test_repository_layout():
    repo_root = Path(__file__).resolve().parents[1]
    assert (repo_root / "src").is_dir()
