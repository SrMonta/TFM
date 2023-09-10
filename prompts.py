from config import N_QUESTIONS_JOIN

prompts = {
    "question": {
        "true/false": f"Utilizando el siguiente texto genera {N_QUESTIONS_JOIN} preguntas de tipo test de verdadero y falso.",
        "single": f"Utilizando el siguiente texto genera {N_QUESTIONS_JOIN} preguntas tipo test con 4 opciones donde solo una de ellas es correcta.",
        "multiple": f"Utilizando el siguiente texto genera {N_QUESTIONS_JOIN} preguntas de tipo test. Las preguntas pueden tener máximo 4 opciones. Debe haber al menos 2 opciones correctas y una incorrecta."
        },
    "answers": {
        "true": " Después de cada pregunta indica la respuesta correcta.",
        "false": ""
        },
    "format": {
            "json": "Devuelve las preguntas como un objeto JSON con 'pregunta', 'opciones' y 'respuesta_correcta'."
        }
    }