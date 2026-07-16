from services.analyzer import analyze_code, calculate_score


def test_empty_code():

    feedback = analyze_code(
        "",
        "",
        "CS136"
    )

    assert feedback[0]["type"] == "error"



def test_print_warning():

    feedback = analyze_code(
        "print('hello')",
        "",
        "CS136"
    )

    found_warning = False

    for item in feedback:
        if item["type"] == "warning":
            found_warning = True


    assert found_warning == True



def test_score_range():

    feedback = []

    score = calculate_score(
        "def hello():\n    pass",
        feedback
    )

    assert 0 <= score <= 100