from datetime import date

import factory.fuzzy

from example.polls import models


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Question

    question_text = factory.fuzzy.FuzzyText()
    pub_date = factory.LazyAttribute(lambda v: date.today())


class ChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Choice

    question = factory.SubFactory(QuestionFactory)
    choice_text = factory.fuzzy.FuzzyText()
    votes = factory.Sequence(int)
