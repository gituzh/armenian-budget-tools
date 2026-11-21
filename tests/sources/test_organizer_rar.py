import subprocess
from pathlib import Path

import pytest

from armenian_budget.sources import organizer


@pytest.fixture
def dirs(tmp_path):
    input_dir = tmp_path / "original"
    output_dir = tmp_path / "extracted"
    (input_dir / "2023" / "Q123").mkdir(parents=True)
    (input_dir / "2023" / "Q123" / "report.rar").write_bytes(b"Rar!")
    return input_dir, output_dir, output_dir / "2023" / "Q123" / "report"


def install_tools(monkeypatch, available, outcomes=None):
    """Fake `shutil.which` and `subprocess.run`.

    `outcomes` maps a tool name to True (extract a file and exit 0) or False
    (write a partial file and exit non-zero). Returns the list of tools run.
    """
    outcomes = outcomes or {}
    paths = {name: f"/fake/bin/{name}" for name in available}
    calls = []

    def fake_which(name):
        return paths.get(name)

    def fake_run(cmd, **kwargs):
        tool = Path(cmd[0]).name
        calls.append(tool)
        target = Path(next(a for a in cmd if a.endswith("report")).removeprefix("-o"))
        if outcomes.get(tool, True):
            (target / f"{tool}.xls").write_text("ok")
            return subprocess.CompletedProcess(cmd, 0, stdout=b"")
        (target / "partial.xls").write_text("partial")
        raise subprocess.CalledProcessError(2, cmd, output=b"Unpacking failed")

    monkeypatch.setattr(organizer.shutil, "which", fake_which)
    monkeypatch.setattr(organizer.subprocess, "run", fake_run)
    return calls


def test_prefers_7zz_over_other_tools(monkeypatch, dirs):
    input_dir, output_dir, target = dirs
    calls = install_tools(monkeypatch, ["unar", "unrar", "7z", "7zz"])

    assert organizer.extract_rar_files(input_dir, output_dir) == [target]
    assert calls == ["7zz"]


def test_tries_tools_in_order_until_one_succeeds(monkeypatch, dirs):
    input_dir, output_dir, target = dirs
    calls = install_tools(
        monkeypatch,
        ["unar", "unrar", "7z", "7zz"],
        {"7zz": False, "7z": False, "unrar": False},
    )

    assert organizer.extract_rar_files(input_dir, output_dir) == [target]
    assert calls == ["7zz", "7z", "unrar", "unar"]


def test_fallback_clears_partial_output_of_failed_tool(monkeypatch, dirs):
    input_dir, output_dir, target = dirs
    install_tools(monkeypatch, ["7zz", "unar"], {"7zz": False})

    organizer.extract_rar_files(input_dir, output_dir)

    assert sorted(p.name for p in target.iterdir()) == ["unar.xls"]


def test_all_tools_failing_leaves_no_target_dir(monkeypatch, dirs, caplog):
    input_dir, output_dir, target = dirs
    install_tools(monkeypatch, ["7zz", "unar"], {"7zz": False, "unar": False})

    assert organizer.extract_rar_files(input_dir, output_dir) == []
    assert not target.exists()
    assert "Unpacking failed" in caplog.text


def test_failed_archive_is_retried_on_next_run(monkeypatch, dirs):
    input_dir, output_dir, target = dirs
    install_tools(monkeypatch, ["unar"], {"unar": False})
    organizer.extract_rar_files(input_dir, output_dir)

    calls = install_tools(monkeypatch, ["unar"])

    assert organizer.extract_rar_files(input_dir, output_dir) == [target]
    assert calls == ["unar"]


def test_skips_non_empty_target_dir(monkeypatch, dirs):
    input_dir, output_dir, target = dirs
    target.mkdir(parents=True)
    (target / "existing.xls").write_text("keep")
    calls = install_tools(monkeypatch, ["7zz"])

    assert organizer.extract_rar_files(input_dir, output_dir) == []
    assert calls == []
    assert (target / "existing.xls").read_text() == "keep"


def test_no_tool_found_skips_extraction(monkeypatch, dirs, caplog):
    input_dir, output_dir, target = dirs
    calls = install_tools(monkeypatch, [])

    assert organizer.extract_rar_files(input_dir, output_dir) == []
    assert calls == []
    assert not target.exists()
    assert "No RAR extractor found" in caplog.text
