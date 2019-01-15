import random
from apps.theses.models import Thesis, ThesisVoteBinding, ThesisVote
from apps.theses.users import get_theses_board


def run():
    ThesisVoteBinding.objects.all().delete()

    cnt = 0
    board_members = list(get_theses_board())
    board_members_cnt = len(board_members)
    for thesis in Thesis.objects.all():
        num_votes = random.randint(board_members_cnt // 2, board_members_cnt)
        members_to_vote = random.sample(board_members, num_votes)
        votes = [
            (voter, ThesisVote(random.randint(2, 3)))
            for voter in members_to_vote
        ]
        thesis.process_new_votes(votes, True)
        cnt += len(votes)

    print(f'Created {cnt} instances in total')
