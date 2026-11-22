from agent.tools import search_documents


def documents(result):
    return [m["document"] for m in result["matches"]]


def test_english_question_finds_the_card_dispute_procedure():
    result = search_documents("How many days does a customer have to dispute a card payment?")
    assert documents(result)[0] == "card-dispute-procedure.md"
    assert "60 days" in result["matches"][0]["snippet"]


def test_french_question_matches_without_accents_or_plurals():
    result = search_documents("combien de temps conserver un releve de compte")
    assert documents(result)[0] == "politique-conservation-donnees.md"
    assert "10 ans" in result["matches"][0]["snippet"]


def test_snippet_skips_the_fictional_disclaimer_and_titles():
    result = search_documents("dispute card")
    snippet = result["matches"][0]["snippet"]
    assert not snippet.startswith((">", "#"))


def test_a_figure_in_a_later_list_item_is_not_cut_off():
    match = search_documents("What is the scheme deadline for a chargeback?")["matches"][0]
    assert match["document"] == "card-dispute-procedure.md"
    assert match["snippet"].startswith("3.")
    assert "120 days" in match["snippet"]


def test_a_table_row_comes_back_with_its_header():
    match = search_documents("enregistrements téléphoniques")["matches"][0]
    assert "6 mois" in match["snippet"]
    assert match["snippet"].startswith("| Catégorie | Durée |")
    assert "10 ans" not in match["snippet"]


def test_documents_rank_by_their_best_passage(monkeypatch, tmp_path):
    # Both documents mention all three words; only one says it in a single passage.
    (tmp_path / "a-scattered.md").write_text(
        "# A\n\nLaptop rules.\n\nTravel rules.\n\nLost items.\n"
    )
    (tmp_path / "b-focused.md").write_text("# B\n\nReport a lost laptop while on travel.\n")
    monkeypatch.setenv("BANQUE_DOCS_DIR", str(tmp_path))
    assert documents(search_documents("lost laptop travel"))[0] == "b-focused.md"


def test_title_only_match_falls_back_to_the_first_body_paragraph(monkeypatch, tmp_path):
    (tmp_path / "expenses.md").write_text(
        "> Fictional.\n\n# Expenses policy\n\n## Scope\n\nApplies to all staff.\n\nKeep receipts.\n"
    )
    monkeypatch.setenv("BANQUE_DOCS_DIR", str(tmp_path))
    match = search_documents("expenses")["matches"][0]
    assert match["document"] == "expenses.md"
    assert match["snippet"] == "Applies to all staff."


def test_no_match_returns_an_empty_list():
    assert search_documents("cryptocurrency staking rewards")["matches"] == []


def test_filler_only_question_matches_nothing():
    assert search_documents("what is the")["matches"] == []


def test_docs_dir_override(monkeypatch, tmp_path):
    (tmp_path / "travel-policy.md").write_text("# Travel\n\nTrains under 4 hours.\n")
    monkeypatch.setenv("BANQUE_DOCS_DIR", str(tmp_path))
    assert documents(search_documents("train travel")) == ["travel-policy.md"]


def test_missing_docs_dir_returns_no_matches(monkeypatch, tmp_path):
    monkeypatch.setenv("BANQUE_DOCS_DIR", str(tmp_path / "absent"))
    assert search_documents("card dispute")["matches"] == []
