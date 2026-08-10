from redcheck import RedCheck

def test_lexical_fallback_pass():
    checker = RedCheck(provider="none")
    prompt = "How do I configure an SMTP server?"
    response = "To configure an SMTP server, set domain records and open ports."
    
    result = checker.evaluate_relevance(prompt, response)
    
    assert "score" in result
    assert result["status"] == "PASS"
    assert result["method"] == "lexical_fallback"

def test_empty_input_flagged():
    checker = RedCheck()
    result = checker.evaluate_relevance("", "")
    
    assert result["score"] == 0.0
    assert result["status"] == "FLAGGED"
