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
