from armenian_budget.sources.downloader import (
    _archive_existing_revision,
    _configured_file_name,
    _sha256_file,
)


def test_archive_existing_revision_preserves_prior_file(tmp_path):
    archive = tmp_path / "report.rar"
    archive.write_bytes(b"old-report")
    checksum = _sha256_file(archive)

    archived_path = _archive_existing_revision(archive, checksum)

    assert not archive.exists()
    assert archived_path.parent == tmp_path / ".revisions"
    assert archived_path.name.endswith(f".{checksum[:12]}.rar")
    assert archived_path.read_bytes() == b"old-report"


def test_configured_file_name_uses_basename_only():
    assert _configured_file_name("../report.rar") == "report.rar"
