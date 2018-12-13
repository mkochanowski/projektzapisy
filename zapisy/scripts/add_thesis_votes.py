import random
from apps.theses.models import (
    Thesis, ThesisVoteBinding, ThesesBoardMember
)


def run():
    ThesisVoteBinding.objects.all().delete()

    board_members = ThesesBoardMember.objects.all()
    board_members_cnt = board_members.count()
    for thesis in Thesis.objects.all():
        num_votes = random.randint(board_members_cnt // 2, board_members_cnt)
        votes = [
            ThesisVoteBinding(thesis=thesis, voter=board_members[i].member, value=random.randint(1, 2))
            for i in range(num_votes)
        ]
        ThesisVoteBinding.objects.bulk_create(votes)
