from django.db import models


class SavedTicket(models.Model):
    ticket = models.TextField(verbose_name='bilet')
    poll = models.ForeignKey('Poll', verbose_name='ankieta', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'zapisane bilety'
        verbose_name = 'zapisany bilet'
        app_label = 'poll'
        unique_together = ['ticket', 'poll']

    def __str__(self):
        res = str(self.poll)
        res += ' (' + str(self.ticket) + ')'
        return res
