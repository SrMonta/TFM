question_function = {
    'name': 'questions',
    'description': 'Get questions data',
    'parameters': {
        'type': 'object',
        'properties': {
            'preguntas': {
                'type': 'object',
                'properties': {
                    'pregunta': {
                        'type': 'string'
                    },
                    'opciones': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    },
                    'respuesta_correcta': {
                        'type': 'string'
                    }
                }
            }
        },
        'required': ['preguntas']
    }
}