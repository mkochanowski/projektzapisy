import random
from apps.theses.models import Thesis, ThesisVoteBinding, ThesisVote
from apps.theses.users import get_theses_board


def run():
    ThesisVoteBinding.objects.all().delete()

    cnt = 0
    board_members = get_theses_board()
    board_members_cnt = len(board_members)
    for thesis in Thesis.objects.all():
        num_votes = random.randint(board_members_cnt // 2, board_members_cnt)
        votes = [
            (board_members[i], ThesisVote(random.randint(2, 3)))
            for i in range(num_votes)
        ]
        thesis.process_new_votes(votes)
        cnt += len(votes)

    print(f'Created {cnt} instances in total')
