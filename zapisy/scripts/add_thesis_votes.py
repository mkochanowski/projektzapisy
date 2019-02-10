import random
import sys

from faker import Faker

from apps.theses.models import Thesis, ThesisVoteBinding, ThesisVote, VoteToProcess
from apps.theses.users import get_theses_board

fake = Faker()

DEFINITE_VOTES = (ThesisVote.ACCEPTED, ThesisVote.REJECTED)


def run():
    board_members = list(get_theses_board())
    board_members_cnt = len(board_members)
    if not board_members_cnt:
        sys.stderr.write("Warning: no theses board members defined, no votes generated\n")
        sys.exit(1)
    cnt = 0
    ThesisVoteBinding.objects.all().delete()
    for thesis in Thesis.objects.all():
        num_votes = random.randint(0, board_members_cnt)
        members_to_vote = random.sample(board_members, num_votes)
        for member in members_to_vote:
            vote_value = random.choice(DEFINITE_VOTES)
            vote = VoteToProcess(member, vote_value, fake.text() if vote_value == ThesisVote.REJECTED else "")
            thesis.process_new_votes([vote], member, True)
        cnt += len(members_to_vote)

    print(f'Created {cnt} instances in total')
