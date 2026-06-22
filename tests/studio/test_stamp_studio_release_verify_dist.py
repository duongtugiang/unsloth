#!/usr/bin/env python3
"""Tests for scripts/stamp_studio_release.py verify-dist behavior."""

from __future__ import annotations

import io
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import stamp_studio_release as stamp  # noqa: E402

_TEST_PACKAGE_BASENAME = "unsloth-0.0.0"


def _build_info(version: str) -> str:
    return (
        "# SPDX-License-Identifier: AGPL-3.0-only\n"
        "STUDIO_RELEASE_VERSION = "
        f"{version!r}\n"
    )


def _write_wheel(path: Path, version: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(stamp.BUILD_INFO_SUFFIX, _build_info(version))


def _write_sdist(path: Path, version: str) -> None:
    with tarfile.open(path, "w:gz") as archive:
        payload = _build_info(version).encode("utf-8")
        member = tarfile.TarInfo(name = f"{_TEST_PACKAGE_BASENAME}/{stamp.BUILD_INFO_SUFFIX}")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))


def test_verify_dist_passes_without_expected_when_stamp_is_valid_and_consistent():
    with tempfile.TemporaryDirectory() as directory:
        dist_dir = Path(directory)
        _write_wheel(dist_dir / f"{_TEST_PACKAGE_BASENAME}-py3-none-any.whl", "v0.1.40-beta")
        _write_sdist(dist_dir / f"{_TEST_PACKAGE_BASENAME}.tar.gz", "v0.1.40-beta")

        assert stamp.verify_dist(None, dist_dir) == 0


def test_verify_dist_keeps_expected_mismatch_check():
    with tempfile.TemporaryDirectory() as directory:
        dist_dir = Path(directory)
        _write_wheel(dist_dir / f"{_TEST_PACKAGE_BASENAME}-py3-none-any.whl", "v0.1.40-beta")
        _write_sdist(dist_dir / f"{_TEST_PACKAGE_BASENAME}.tar.gz", "v0.1.40-beta")

        assert stamp.verify_dist("v0.1.471-beta", dist_dir) == 2


def test_verify_dist_requires_consistent_stamp_across_artifacts():
    with tempfile.TemporaryDirectory() as directory:
        dist_dir = Path(directory)
        _write_wheel(dist_dir / f"{_TEST_PACKAGE_BASENAME}-py3-none-any.whl", "v0.1.40-beta")
        _write_sdist(dist_dir / f"{_TEST_PACKAGE_BASENAME}.tar.gz", "v0.1.41-beta")

        assert stamp.verify_dist(None, dist_dir) == 2
