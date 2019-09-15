import os
from typing import List

root = os.getcwd()

abbreviations = {}
flipped = {}

def speak_slowly(phrase: str) -> str:
    return f'<prosody rate="slow">{phrase}</prosody>'


def spell_out(acronym: str) -> str:
    if '(' in acronym:
        acronym = acronym.replace('(', '').replace(')', '')
        output = f'(<say-as interpret-as="characters">{acronym}</say-as>)'
    else:
        output = f'<say-as interpret-as="characters">{acronym}</say-as>'
    return speak_slowly(output)

with open(os.path.join(root, 'abbreviations.txt')) as f:
    abbrevs: List[str] = [x.lower() for x in f.readlines()]
with open(os.path.join(root, 'abbreviations2.txt')) as f:
    abbrevs.extend([x.lower() for x in f.readlines()])
for line in abbrevs:
    arr = [x.replace('\n', '') for x in line.split('----------')]
    abbreviations[arr[0]] = arr[1]
    abbreviations[f'({arr[0]})'] = f'({arr[1]})'
    flipped[f'({arr[1]})'] = arr[1]
    flipped[arr[1]] = arr[1]



company = 'azure'
company_edited = company + '_edited'
for filename in os.listdir(os.path.join(root, company)):
    with open(os.path.join(root, company, filename)) as f:
        lines: List[str] = [x.replace('\n', '') for x in f.readlines()]
    for index, line in enumerate(lines):
        line_lower = line.lower()
        line_arr: List[str] = line.split(' ')
        line_arr_lower: List[str] = line_lower.split(' ')
        for i, val in enumerate(line_arr_lower):
            if val in abbreviations:
                if flipped[abbreviations[val]] in line_lower:
                    line_arr[i] = spell_out(val)
                else:
                    line_arr[i] = abbreviations[val]
        lines[index] = ' '.join(line_arr) + '\n'
    with open(os.path.join(root, company_edited, filename), 'w') as f:
        f.writelines(lines)
