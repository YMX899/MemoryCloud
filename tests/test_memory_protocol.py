from app.memory_protocol import build_archive, build_manifest, parse_archive


def test_memory_archive_round_trip():
    manifest = build_manifest(
        title="Round Trip Agent",
        summary="A test memory suite",
        version="1.0.0",
        license_name="CC-BY-4.0",
        tags=["agent", "openclaw"],
        persona_type="agent",
        provenance={"source_type": "self_authored"},
        author_handle="tester",
    )
    archive, hydrated_manifest = build_archive(
        manifest=manifest,
        memory_md="# Memory\n\n- durable fact",
        dreams_md="# Dreams\n\n- reflection",
        work_memory=[{"date": "2026-05-28", "content": "# 2026-05-28\n\n- work item"}],
    )

    parsed = parse_archive(archive)

    assert parsed["manifest"]["schema"] == "amp.memory.v1"
    assert parsed["manifest"]["suite"]["schema"] == "amp.memory-suite.v1"
    assert "suite/manifest.json" in parsed["manifest"]["files"]
    assert parsed["manifest"]["files"]["MEMORY.md"]["sha256"] == hydrated_manifest["files"]["MEMORY.md"]["sha256"]
    assert parsed["memory_md"].startswith("# Memory")
    assert parsed["work_memory"][0]["date"] == "2026-05-28"
