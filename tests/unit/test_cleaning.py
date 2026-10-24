"""Protect count preservation, exclusion accounting and tag provenance."""

from pathlib import Path

import pandas as pd
import pytest

from musicrec.data.cleaning import clean_interactions, clean_tables, read_source_table
from scripts.preprocess import main


def test_cleaning_accounts_for_each_row_without_summing_or_losing_the_tail() -> None:
    source = pd.DataFrame(
        [("1", str(i), "352698" if i == 1 else str(i)) for i in range(1, 6)]
        + [("1", "1", "352698")]
        + [("2", str(i), "10") for i in range(1, 5)]
        + [("2", "5", "inf"), ("3", "999", "1"), ("0", "1", "1")],
        columns=["userID", "artistID", "weight"],
    )
    original = source.copy(deep=True)
    kept, excluded, counts = clean_interactions(source, {str(i) for i in range(1, 6)})
    assert len(kept) == 5
    assert set(kept.user_id) == {"1"}
    assert kept.listening_count.tolist() == [352698, 2, 3, 4, 5]
    assert counts == {
        "input_rows": 13,
        "output_rows": 5,
        "excluded_rows": 8,
        "users_below_minimum": 1,
        "invalid_id": 1,
        "invalid_count": 1,
        "artist_outside_catalog": 1,
        "duplicate_observation": 1,
        "user_below_minimum": 4,
    }
    assert excluded.source_line.is_unique
    assert len(kept) + len(excluded) == len(source)
    pd.testing.assert_frame_equal(source, original)


def test_conflicting_counts_abort_instead_of_being_aggregated() -> None:
    source = pd.DataFrame(
        [("1", "1", "3"), ("1", "1", "4")], columns=["userID", "artistID", "weight"]
    )
    with pytest.raises(ValueError, match="Conflicting counts"):
        clean_interactions(source, {"1"}, min_user_interactions=1)


def test_reader_and_metadata_preserve_unicode_missing_content_and_tag_authors(
    tmp_path: Path,
) -> None:
    tag_path = tmp_path / "tags.dat"
    tag_path.write_bytes("tagID\ttagValue\n1\tespañol\n2\tNA\n".encode("latin-1"))
    artist_path = tmp_path / "artists.dat"
    artist_path.write_text(
        "id\tname\turl\tpictureURL\n1\tBjörk\tu\t\n2\tNA\tu\t\n3\t\tu\t\n", encoding="utf-8"
    )
    artists, tags = read_source_table(artist_path), read_source_table(tag_path)
    assert tags.tagValue.tolist() == ["español", "NA"]
    interactions = pd.DataFrame(
        [("1", "1", "1"), ("1", "2", "2"), ("2", "1", "9")],
        columns=["userID", "artistID", "weight"],
    )
    assignments = pd.DataFrame(
        [("2", "1", "1"), ("1", "999", "2")], columns=["userID", "artistID", "tagID"]
    )
    tables, metrics = clean_tables(interactions, artists, tags, assignments, 2)
    assert tables["artists"].display_name.tolist() == ["Björk", "NA", "Artist 3"]
    assert tables["interactions"].item_id.tolist() == ["1", "2"]
    assert tables["tag_assignments"].userID.tolist() == ["2"]
    assert tables["excluded_tag_assignments"].artistID.tolist() == ["999"]
    assert (
        metrics["tags"]["assignments_by_excluded_users_retained_for_later_protocol_filtering"] == 1
    )
    assert metrics["tags"]["active_artists_without_tags"] == 1
    assert metrics["after"]["catalog_artists"] == 3


def test_cli_refuses_to_overwrite_an_existing_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sentinel = tmp_path / "previous_result.txt"
    sentinel.write_text("keep", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["preprocess", "--output-dir", str(tmp_path)])
    with pytest.raises(ValueError, match="new directory"):
        main()
    assert sentinel.read_text(encoding="utf-8") == "keep"
