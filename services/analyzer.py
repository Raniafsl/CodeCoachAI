def calculate_score(code, feedback):

    score = 100

    for item in feedback:

        if item["type"] == "error":
            score -= 25

        elif item["type"] == "warning":
            score -= 10


    if "#" not in code:
        score -= 5


    if len(code.split("\n")) > 40:
        score -= 5


    bad_names = ["x", "y", "z"]

    for name in bad_names:

        if f" {name} " in code:
            score -= 3


    if "def " in code:
        score += 3


    score = max(0, min(score, 100))

    return score

def analyze_code(code, problem, course):

    feedback = []


    if code.strip() == "":

        feedback.append({
            "type": "error",
            "title": "No Code Found",
            "message": "Paste some code so CodeCoach can analyze it."
        })


    # recursion check

    if "def " in code:

        function_names = []


        for line in code.split("\n"):

            line = line.strip()

            if line.startswith("def "):

                name = line.split("(")[0].replace("def ", "")

                function_names.append(name)



        for name in function_names:

            body = "\n".join(
                line for line in code.split("\n")
                if not line.strip().startswith("def " + name)
            )


            if name + "(" in body:

                if "if" not in body:

                    feedback.append({
                        "type": "error",
                        "title": "Possible Missing Base Case",
                        "message": "Recursive function may not stop."
                    })



    if "while True" in code:

        feedback.append({
            "type": "error",
            "title": "Infinite Loop Risk",
            "message": "Make sure your loop has an exit condition."
        })



    if "print(" in code:

        feedback.append({
            "type": "warning",
            "title": "Debug Statement Found",
            "message": "Remove print statements before submitting."
        })



    if code.count("for ") >= 2:

        feedback.append({
            "type": "warning",
            "title": "Efficiency Issue",
            "message": "Possible nested loops detected."
        })



    if "TODO" in code:

        feedback.append({
            "type": "warning",
            "title": "Incomplete Code",
            "message": "TODO comments remain."
        })



    if len(feedback) == 0:

        feedback.append({
            "type": "success",
            "title": "Looks Good!",
            "message": "No obvious issues detected."
        })


    return feedback