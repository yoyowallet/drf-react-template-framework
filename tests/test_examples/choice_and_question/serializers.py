from rest_framework import serializers


class ChoiceListSerializer(serializers.Serializer):
    choice_text = serializers.CharField()
    votes = serializers.IntegerField(default=0)

    class Meta:
        fields = ('choice_text', 'votes')


class QuestionsSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    pub_date = serializers.DateTimeField(label='date published')

    class Meta:
        fields = ('question_text', 'pub_date')


class ChoiceSerializer(serializers.Serializer):
    choice_text = serializers.CharField()
    votes = serializers.IntegerField(default=0)
    questions = QuestionsSerializer(many=True)

    class Meta:
        fields = ('choice_text', 'votes', 'questions')
