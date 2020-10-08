# -*- coding: utf-8 -*-
import string


def fix_u(m):
    replacements = (("u:", "ü"),
                    ("v", "ü"),
                    ("U:", "Ü"),
                    ("V", "Ü"))
    for pair in replacements:
        m = m.replace(*pair)
    return m


def accent_placement(m):
    assert len(m) > 0
    retval = None
    if "a" in m.lower():
        retval = m.lower().index("a")
    elif "e" in m.lower():
        retval = m.lower().index("e")
    elif "ou" in m.lower():
        retval = m.lower().index("ou")
    else:
        for idx, l in enumerate(m):
            if l in pinyin_tone_marks:
                retval = idx
    return retval


pinyin_initials = ["", *list("bpmfdtnlgkhjqxrzcsyw"), *["zh", "ch", "sh"]]
pinyin_finals = ["", "n", "ng", "nr", "r", "ngr"]
pinyin_vowels = [*list(""), *["ai", "ei", "ao", "ou",
                                    "ia", "io", "ie", "iai", "iao", "iu",
                                    "ua", "uo", "uai", "ui", "ue",
                                    "üe", "üa"]]
tone_numbers = ["", *list("012345")]

pinyin_tone_marks = {
    'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì',
    'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ',
    'A': 'ĀÁǍÀ', 'E': 'ĒÉĚÈ', 'I': 'ĪÍǏÌ',
    'O': 'ŌÓǑÒ', 'U': 'ŪÚǓÙ', 'Ü': 'ǕǗǙǛ',
    'v': 'ǖǘǚǜ', 'V': 'ǖǘǚǜ'
}


def convert_syllable(s, n2a=True):
    if not n2a:
        return accented_to_numbered_syllable(s)
    tone_loc = accent_placement(s)
    tone_num = s[-1]
    if tone_num in "012345":
        retval = s[:-1]
        if tone_num in "1234":
            new_vowel = pinyin_tone_marks[s[tone_loc]][int(tone_num) - 1]
            retval = retval[:tone_loc] + new_vowel + retval[tone_loc+1:]
    else:
        retval = s
    return retval


pinyin_accented_vowels = []
for tone in "01234":
    for v in pinyin_vowels:
        a_v = convert_syllable(v+tone)
        pinyin_accented_vowels.append(a_v)


def numbered_syllables():
    for i in pinyin_initials:
        for v in pinyin_vowels:
            for f in pinyin_finals:
                for t in tone_numbers:
                    syllable = i + v + f + t
                    yield syllable


def accented_syllables():
    for i in pinyin_initials:
        for v in pinyin_accented_vowels:
            for f in pinyin_finals:
                syllable = i + v + f
                yield syllable


n_syllables_list = []
for i in numbered_syllables():
    n_syllables_list.append(i)
a_syllables_list = []
for i in accented_syllables():
    a_syllables_list.append(i)


def valid_pinyin(s):
    if len(s) < 1:
        return False
    i = "bpmfdtnlgkhjqxrzcsyw"
    v = 'aāáǎàeēéěèiīíǐìoōóǒòuūúǔùüǖǘǚǜ'
    a_v = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'
    f = "ngr"
    t = "012345"

    STATE = 0
    INITIAL = 1
    ZCS = 2
    VOWEL = 3
    FINAL = 4
    TONE = 5
    END = 6
    valid = True

    NUMBERED = False
    ACCENTED = False
    if s[-1] in t:
        NUMBERED = True
    for l in fix_u(s.lower()):
        if l in a_v:
            ACCENTED = True
    if NUMBERED and ACCENTED:
        valid = False

    for letter in (fix_u(s.lower()) + '$'):
        if STATE == 0:
            if letter in "zcs":
                STATE = ZCS
            elif letter in i:
                STATE = INITIAL
            elif letter in v:
                STATE = VOWEL
            else:
                valid = False
        elif STATE == ZCS:
            if letter == 'h':
                STATE = INITIAL
            elif letter in v:
                STATE = VOWEL
            else:
                valid = False
        elif STATE == INITIAL:
            if letter in v:
                STATE = VOWEL
            else:
                valid = False
        elif STATE == VOWEL:
            if letter in v:
                pass
            elif letter in f:
                STATE = FINAL
            elif letter in t:
                STATE = TONE
            elif letter == '$':
                STATE = END
            else:
                valid = False
        elif STATE == FINAL:
            if letter in f:
                pass
            elif letter in t:
                STATE = TONE
            elif letter == '$':
                STATE = END
            else:
                valid = False
        elif STATE == TONE:
            if letter == '$':
                STATE = END
            else:
                valid = False
            if not NUMBERED:
                valid = False
    if STATE != END:
        valid = False
    return valid


def find_first_syllable(m, numbered=False, accented=False):
    if m == '':
        return None
    for i2 in range(len(m), 0, -1):
        if valid_pinyin(m[:i2]):
            if m[:i2][-1] in "012345":
                if numbered:
                    return m[:i2]
            elif accented:
                candidate = m[:i2]
                accent_found = False
                for l in candidate:
                    if l in "āēīōūǖáéíóúǘǎěǐǒǔǚàèìòùǜ":
                        accent_found = True
                if accent_found:
                    return candidate
    return find_first_syllable(m[1:], numbered, accented)


def numbered_to_accented(s):
    s1 = fix_u(s)
    old_syl = find_first_syllable(s1, numbered=True)
    while old_syl is not None:
        new_syl = convert_syllable(old_syl)
        s1 = s1.replace(old_syl, new_syl)
        old_syl = find_first_syllable(s1, numbered=True)
    return s1


def accented_to_numbered_syllable(s):
    t1 = 'āēīōūǖ'
    t2 = 'áéíóúǘ'
    t3 = 'ǎěǐǒǔǚ'
    t4 = 'àèìòùǜ'
    accented_vowel = ""
    current_tone = ""
    for l in s:
        if l.lower() in t1+t2+t3+t4:
            accented_vowel = l
        if l.lower() in t1:
            current_tone = '1'
        elif l.lower() in t2:
            current_tone = '2'
        elif l.lower() in t3:
            current_tone = '3'
        elif l.lower() in t4:
            current_tone = '4'

    unaccented_vowel = None
    for k in pinyin_tone_marks:
        if accented_vowel in pinyin_tone_marks[k] and accented_vowel != "":
            unaccented_vowel = k
            s = s.replace(accented_vowel, unaccented_vowel)
    return s + str(current_tone)


def accented_to_numbered(s):
    s1 = fix_u(s)
    old_syl = find_first_syllable(s1, accented=True)
    while old_syl is not None:
        new_syl = convert_syllable(old_syl, n2a=False)
        s1 = s1.replace(old_syl, new_syl)
        old_syl = find_first_syllable(s1, accented=True)
    return s1


testing = True
if testing:
    a = "Ní hǎo ma? lüè"
    n = 'Ni2 hao3 ma0? lüe4'
    print(numbered_to_accented(n))
    print(accented_to_numbered(a))
    # fail?
    print(accented_to_numbered('NíNínghǎo'))
