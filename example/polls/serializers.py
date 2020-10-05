from rest_framework import serializers


class QuestionListSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    pub_date = serializers.DateField(label='date published')

    class Meta:
        fields = ('question_text', 'pub_date')


class ChoiceSerializer(serializers.Serializer):
    choice_text = serializers.CharField()
    votes = serializers.IntegerField(default=0)

    class Meta:
        fields = ('choice_text', 'votes')


class QuestionSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    pub_date = serializers.DateField(label='date published')
    choices = ChoiceSerializer(many=True)

    class Meta:
        fields = ('question_text', 'pub_date', 'choices')
