# coding=utf-8
from decimal import Decimal, ROUND_HALF_UP
from pypinyin import pinyin, lazy_pinyin
import pypinyin

def format_decimal(value):
    """
    Format a decimal with two decimal point with rounding mode ROUND_HALF_UP
    :param value the decimal to format
    """
    return Decimal(
        Decimal(value).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def decimal_to_percent(value, decimal_place=2):
    """
    Format a decimal to percentage with two decimal
    :param value: the value to be formatted
    :param decimal_place default decimal place, default to 2
    :return: a string in percentage format, 20.50% etc
    """
    format_str = '{:.' + str(2) + '%}'
    return format_str.format(value)


def get_name(last_name, first_name):
    """
    Get name from last name and first name, if the name is in alpha, 
    then use whitespace as the connect between them.
    :param last_name: Last name 
    :param first_name:  First name
    :return: last name + connect + first name, 
    """
    connect = ''
    if str(last_name).isalpha() and str(first_name).isalpha():
        connect = ' '
    return last_name + connect + first_name


def get_pinyin_first_letters(chinese_characters):
    """
    Get fist letters of pin yin of chinese characters, if there's any 多音字
    All combinations will be returned, for example for "调向"
    Result of dx|tx will be returned.
    :param chinese_characters: Chinese characters to get pinyin. 
    :return: first letters of pin yin of the letters
    """
    pys = _get_pinyin_all([], chinese_characters)
    result = ''
    for py in pys:
        for p in py:
            result += p
        result += "|"
    result = result.rstrip('|') # <- Remove last "|"
    return result

def _get_pinyin_all(existing_combinations, characters):
    """
    Get all combinations of pinyin of some chinese characters as list, in a 
    recurrence way, since format of result from pinyin is [['a'], ['b']]
    So a combination of two level loop is needed to get all the pinyin. 
    :param existing_combinations:  Existing combinations, for already calculated characters. 
    :param characters: Characters to get combination of pinyin 
    :return:  A flat list of all combinations of pinyin for 多音字
    """
    first_character, other_characters = characters[0:1], characters[1:]
    if len(first_character) > 0:
        py = pinyin(first_character, style=pypinyin.FIRST_LETTER, heteronym=True)
        new_existing = []
        for p in py:
            for a in p:
                if len(existing_combinations) > 0:
                    for e in existing_combinations:
                        ne = e[:]
                        ne.append(a)
                        new_existing.append(ne)
                else:
                    ne = existing_combinations[:]
                    ne.append(a)
                    new_existing.append(ne)
        return _get_pinyin_all(new_existing, other_characters)
    return existing_combinations




