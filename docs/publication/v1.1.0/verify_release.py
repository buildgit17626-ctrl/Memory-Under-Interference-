"""Snapshot old GitHub history and verify the approved public release; no publishing."""

import argparse
import hashlib
import json
import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REPO = "buildgit17626-ctrl/Memory-Under-Interference-"
TAG = "v1.1.0"
APPROVED = json.loads((HERE / "approved-assets.json").read_text(encoding="utf-8"))


def api(endpoint: str):
    return json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tag_identity(name: str) -> dict:
    obj = api(f"repos/{REPO}/git/ref/tags/{name}")["object"]
    target = obj
    while target["type"] == "tag":
        target = api(f"repos/{REPO}/git/tags/{target['sha']}")["object"]
    assert target["type"] == "commit"
    return {"object_sha": obj["sha"], "commit_sha": target["sha"]}


def release_identity(name: str) -> dict:
    r = api(f"repos/{REPO}/releases/tags/{name}")
    fields = ("id", "tag_name", "name", "target_commitish", "draft", "prerelease")
    return {
        **{key: r[key] for key in fields},
        "body_sha256": digest(r["body"].encode()),
        "assets": sorted(
            [{key: a.get(key) for key in ("id", "name", "size", "digest")} for a in r["assets"]],
            key=lambda a: a["name"],
        ),
    }


def preflight() -> None:
    hooks = api(f"repos/{REPO}/hooks")
    workflows = api(f"repos/{REPO}/actions/workflows")
    assert not hooks, "Review publication hooks before releasing; Zenodo is not authorized"
    assert workflows["total_count"] == 0, "Review workflows before publication"
    rows = {
        name: {"tag": tag_identity(name), "release": release_identity(name)}
        for name in ("v1.0.0", "v1.0.1")
    }
    data = {"previous_releases": rows, "hooks": hooks, "workflow_count": 0}
    (HERE / "preflight.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Previous releases/tags snapshotted; no hooks or Actions workflows observed")


def verify(commit: str) -> None:
    r = api(f"repos/{REPO}/releases/tags/{TAG}")
    assert not r["draft"] and not r["prerelease"]
    assert r["target_commitish"] == commit
    assert tag_identity(TAG)["commit_sha"] == commit
    assert api(f"repos/{REPO}/releases/latest")["tag_name"] == TAG
    assert api(f"repos/{REPO}/git/ref/heads/main")["object"]["sha"] == commit
    assert APPROVED["doi"] in r["body"]
    assert "reserved" in r["body"].lower()
    assert "Version 1.1" in r["name"]
    for name in ("README.md", "CITATION.cff"):
        url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{name}"
        with urllib.request.urlopen(url, timeout=60) as response:
            content = response.read().decode()
        assert APPROVED["doi"] in content and "/v1.1.0" in content
    expected = {a["name"]: a for a in APPROVED["assets"]}
    assert {a["name"] for a in r["assets"]} == set(expected)
    downloads = ROOT / "tmp/github-v1.1.0-public-downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    rows = []
    for a in r["assets"]:
        e = expected[a["name"]]
        assert a["size"] == e["bytes"]
        assert a["digest"] == "sha256:" + e["sha256"]
        # No token/cookie/Authorization header: these must be actual public downloads.
        req = urllib.request.Request(
            a["browser_download_url"], headers={"User-Agent": "release-check"}
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            assert response.status == 200
            content = response.read()
        assert len(content) == e["bytes"] and digest(content) == e["sha256"]
        local = ROOT / "releases/v1.1" / a["name"]
        committed = subprocess.check_output(
            ["git", "show", commit + ":" + local.relative_to(ROOT).as_posix()]
        )
        assert content == local.read_bytes() == committed
        (downloads / a["name"]).write_bytes(content)
        rows.append({**e, "public_url": a["browser_download_url"], "http_status": 200})
    for line in (downloads / "SHA256SUMS.txt").read_text().splitlines():
        value, name = line.split("  ", 1)
        assert digest((downloads / name).read_bytes()) == value
    inner_count = 0
    for p in downloads.glob("*.zip"):
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            assert not any(n.endswith((".ttf", ".otf")) for n in z.namelist())
            tex = z.read("manuscript/main.tex").decode()
            assert APPROVED["doi"] in tex and "/v1.1.0" in tex
            if "reproducibility" in p.name:
                inner = json.loads(z.read("SHA256SUMS.json"))
                for name, entry in inner.items():
                    content = z.read(name)
                    assert digest(content) == entry["sha256"] and len(content) == entry["bytes"]
                inner_count = len(inner)
                cff = z.read("CITATION.cff").decode()
                assert APPROVED["doi"] in cff and "/v1.1.0" in cff
    old = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))
    for name, before in old["previous_releases"].items():
        assert before == {"tag": tag_identity(name), "release": release_identity(name)}
    report = {
        "release_url": r["html_url"],
        "release_id": r["id"],
        "tag": TAG,
        "publication_commit": commit,
        "approved_artifact_commit": APPROVED["approved_commit"],
        "published_at": r["published_at"],
        "latest": True,
        "doi": APPROVED["doi"],
        "doi_status": "Reserved; Zenodo not published by this work",
        "unauthenticated_public_downloads": rows,
        "inner_manifest_files_verified": inner_count,
        "prior_releases_tags_and_asset_metadata_unchanged": True,
        "new_model_inference": 0,
        "manuscript_revisions": 0,
        "zenodo_publication_performed": False,
    }
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "verify"))
    parser.add_argument("--commit")
    args = parser.parse_args()
    if args.action == "preflight":
        preflight()
    else:
        if not args.commit:
            parser.error("verify requires --commit")
        verify(args.commit)
