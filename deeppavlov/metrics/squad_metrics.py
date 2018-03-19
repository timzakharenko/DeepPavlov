import re
import string
from collections import Counter

from deeppavlov.core.common.metrics_registry import register_metric


@register_metric('exact_match')
def exact_match(y_true, y_predicted):
    """ Calculates Exact Match score between y_true and y_predicted
        EM score uses the best matching y_true answer:
            if y_pred equal at least to one answer in y_true then EM = 1, else EM = 0

    Args:
        y_true: list of tuples (y_true_text, y_true_start), y_true_text and y_true_start are lists of len num_answers
        y_predicted: list of tuples (y_pred_text, y_pred_start), y_pred_text : str, y_pred_start : int

    Returns:
        exact match score : float
    """
    y_predicted = hotfix(y_predicted)
    EM_total = 0
    for (ground_truth, _), (prediction, _) in zip(y_true, y_predicted):
        EMs = [int(normalize_answer(gt) == normalize_answer(prediction)) for gt in ground_truth]
        EM_total += max(EMs)
    return 100 * EM_total / len(y_true) if len(y_true) > 0 else 0


@register_metric('squad_f1')
def squad_f1(y_true, y_predicted):
    """ Calculates F-1 score between y_true and y_predicted
        F-1 score uses the best matching y_true answer

    Args:
        y_true: list of tuples (y_true_text, y_true_start), y_true_text and y_true_start are lists of len num_answers
        y_predicted: list of tuples (y_pred_text, y_pred_start), y_pred_text : str, y_pred_start : int

    Returns:
        F-1 score : float
    """
    y_predicted = hotfix(y_predicted)
    f1_total = 0.0
    for (ground_truth, _), (prediction, _) in zip(y_true, y_predicted):
        prediction_tokens = normalize_answer(prediction).split()
        f1s = []
        for gt in ground_truth:
            gt_tokens = normalize_answer(gt).split()
            common = Counter(prediction_tokens) & Counter(gt_tokens)
            num_same = sum(common.values())
            if num_same == 0:
                f1s.append(0.0)
                continue
            precision = 1.0 * num_same / len(prediction_tokens)
            recall = 1.0 * num_same / len(gt_tokens)
            f1 = (2 * precision * recall) / (precision + recall)
            f1s.append(f1)
        f1_total += max(f1s)
    return 100 * f1_total / len(y_true) if len(y_true) > 0 else 0


def hotfix(y_predicted):
    """
    hotfix:
    [[arg1, arg1, ...], [arg2, arg2, ...], [arg1, arg1, ...], [arg2, arg2, ...], ...]
    ->
    [(arg1, arg2), (arg1, arg2), ...]
    """
    assert len(y_predicted) % 2 == 0
    a, p = [], []
    for i in range(len(y_predicted) // 2):
        a.extend(y_predicted[i * 2])
        p.extend(y_predicted[i * 2 + 1])

    return list(zip(a, p))


def normalize_answer(s):
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))
