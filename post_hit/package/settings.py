RESOURCE_METHODS = ['GET', 'POST']
DOMAIN = {
    'user': {
        'schema': {
            'firstname': {
                'type': 'string'
            },
            'lastname': {
                'type': 'string'
            },
            'username': {
                'type': 'string',
                 'unique': True
            },
            'password': {
                'type': 'string'
            },
            'phone': {
                'type': 'string'
            }
        }
    },
    'region': {
        'schema': {
            'start':{
                'type': 'integer'
                },
            'end': {
                'type': 'integer'
                }
            }
        }
}
