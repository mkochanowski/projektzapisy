import random
import sys
from apps.theses.models import Thesis, ThesisVoteBinding, ThesisVote
from apps.theses.users import get_theses_board

DEFINITE_VOTES = (ThesisVote.ACCEPTED, ThesisVote.REJECTED)


def run():
    board_members = list(get_theses_board())
    board_members_cnt = len(board_members)
    if not board_members_cnt:
        sys.stderr.print("Warning: no theses board members defined, no votes generated")
        sys.exit(1)
    cnt = 0
    ThesisVoteBinding.objects.all().delete()
    for thesis in Thesis.objects.all():
        num_votes = random.randint(0, board_members_cnt)
        members_to_vote = random.sample(board_members, num_votes)
        votes = [
            (voter, random.choice(DEFINITE_VOTES))
            for voter in members_to_vote
        ]
        thesis.process_new_votes(votes, True)
        cnt += len(votes)

    print(f'Created {cnt} instances in total')
