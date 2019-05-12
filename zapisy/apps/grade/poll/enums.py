from choicesenum import ChoicesEnum


class PollType(ChoicesEnum):
    LECTURE = 1, "ankieta dla wykładu"
    EXERCISE = 2, "ankieta dla ćwiczeń"
    LABS = 3, "ankieta dla pracowni"
    # For some reason, 4 is skipped
    EXERCISE_LABS = 5, "ankieta dla ćwiczenio-pracowni"
    SEMINARY = 6, "ankieta dla seminarium"
    LECTORATE = 7, "ankieta dla lektoratu"
    PHYSICAL_EDUCATION = 8, "ankieta dla zajęć wf"
    REPETITORY = 9, "ankieta dla repetytorium"
    PROJECT = 10, "ankieta dla projektu"
    EXAM = 1000, "ankieta dla egzaminu"
    GENERAL = 1001, "ankieta ogólna"


class SchemaPersonalEvaluationAnswers(ChoicesEnum):
    DEFINITELY_BETTER = "definitely_better", "zdecydowanie lepsze"
    BETTER = "better", "trochę lepsze"
    NEUTRAL = "neutral", "mniej więcej takie same"
    WORSE = "worse", "trochę gorsze"
    DEFINITELY_WORSE = "definitely_worse", "zdecydowanie gorsze"


class SchemaTimeLongAnswers(ChoicesEnum):
    A_FEW_HOURS = "a_few_hours", "kilka godzin"
    A_DAY = "a_day", "około 1 dnia"
    A_FEW_DAYS = "a_few_days", "kilka dni (około 3)"
    ALMOST_A_WEEK = "almost_a_week", "prawie cały tydzień"


class SchemaTimeShortAnswers(ChoicesEnum):
    LESS_THAN_ONE_HOUR = "less_than_one_hour", "mniej niż 1 godzinę"
    ABOUT_TWO_HOURS = "about_two_hours", "około 2 godzin"
    ABOUT_FIVE_HOURS = "about_five_hours", "jedno popołudnie (około 5 godzin)"
    ABOUT_TEN_HOURS = "about_ten_hours", "dwa popołudnia (około 10 godzin)"
    MORE_THAN_TWO_DAYS = "more_than_two_days", "więcej niż dwa dni"


class SchemaGenericAnswers(ChoicesEnum):
    STRONGLY_AGREE = "strongly_agree", "zdecydowanie tak"
    AGREE = "agree", "raczej tak"
    NEUTRAL = "neutral", "trudno powiedzieć"
    DISAGREE = "disagree", "raczej nie"
    STRONGLY_DISAGREE = "strongly_disagree", "zdecydowanie nie"
