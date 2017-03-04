from rest_framework import serializers

from six import iteritems


class FriendlyChoiceField(serializers.ChoiceField):
    '''Serializer ChoiceField that uses the string representation
    of the choices rather then the int values. Supports creation
    with either choice string or via choice int. It's friendlier.'''
    def __init__(self, choices, **kwargs):
        self.choice_dict = dict(choices)
        kwargs['choices'] = choices
        super(FriendlyChoiceField, self).__init__(**kwargs)

    def to_representation(self, obj):
        # uppercase is more authoritative
        return self.choice_dict[obj].upper()

    def to_internal_value(self, data):
        try:
            # first let's see if we can match to a key
            return self.choice_dict[data]
        except KeyError:
            # if that fails, then let's try to match a value
            # note that this will match the first entry
            # if there multiple keys with the same value
            for key, val in iteritems(self.choice_dict):
                if data.upper() == val.upper():
                    return key
            # if nothing matched then we need to fail
            self.fail('invalid_choice', input=data)
