"""
    News Forms
"""

from django.forms import ModelForm
from offer.news.models import News

class NewsForm(ModelForm):
    """
        Form for news
    """
    class Meta:
        model  = News
        fields = ('title', 'body')
