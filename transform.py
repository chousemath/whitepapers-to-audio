import os
import boto3
from time import sleep
from typing import List
from dotenv import load_dotenv
load_dotenv()

root = os.getcwd()

def post_process(phrase: str) -> str:
    phrase = phrase.replace(',</emphasis>', '</emphasis>,')
    return phrase


transcripts = {}
abbreviations = {}
flipped = {}
company_acronyms = {}
words_to_emphasize = {}
_words_to_emphasize = ['InfiniBand', 'on-premises']
with open(os.path.join(root, 'apache_projects.txt')) as f:
    _words_to_emphasize.extend([x.replace('\n', '').strip() for x in f.readlines()])
languages = ["javascript", "python", "java", "swift", "typescript", "go programming language", "sql", "ruby", "r programming language", "php", "perl", "kotlin", "rust", "scheme", "erlang", "scala", "elixir", "haskell"]
_words_to_emphasize.extend(languages)
_special_words = {
        'hbase': '<emphasis><say-as interpret-as="characters">h</say-as> base</emphasis>',
        'c#': '<emphasis><say-as interpret-as="characters">c</say-as> sharp</emphasis>',
        'c++': '<emphasis><say-as interpret-as="characters">c</say-as> plus plus</emphasis>',
        '99.99%': '<emphasis>four nines</emphasis>',
        '99.999%': '<emphasis>five nines</emphasis>',
        '99.9999%': '<emphasis>six nines</emphasis>',
        '99.99999%': '<emphasis>seven nines</emphasis>',
        '99.999999%': '<emphasis>eight nines</emphasis>',
        '99.9999999%': '<emphasis>nine nines</emphasis>',
        '99.99999999%': '<emphasis>ten nines</emphasis>',
        '99.999999999%': '<emphasis>eleven nines</emphasis>',
        '99.9999999999%': '<emphasis>twelve nines</emphasis>',
        }
special_words = {}
_stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
stopwords = {}
for word in _stopwords:
    stopwords[word] = True

windows_vms = "B, Dsv3, Dv3, Dasv3, Dav3, DSv2, Dv2, Av2, DC, Fsv2, Esv3, Ev3, Easv3, Eav3, Mv2, M, DSv2, Dv2, Lsv2, NC, NCv2, NCv3, ND, NDv2, NV, NVv3, HB, HC, H"
windows_general_purpose_vms = ["Standard_B1ls1", "Standard_B1s", "Standard_B1ms", "Standard_B2s", "Standard_B2ms", "Standard_B4ms", "Standard_B8ms", "Standard_B12ms", "Standard_B16ms", "Standard_B20ms", "Standard_D2s_v3", "Standard_D4s_v3", "Standard_D8s_v3", "Standard_D16s_v3", "Standard_D32s_v3", "Standard_D48s_v3", "Standard_D64s_v3", "Standard_D2as_v3", "Standard_D4as_v3", "Standard_D8as_v3", "Standard_D16as_v3", "Standard_D32as_v3", "Standard_D48as_v3", "Standard_D64as_v3", "Standard_D2_v3", "Standard_D4_v3", "Standard_D8_v3", "Standard_D16_v3", "Standard_D32_v3", "Standard_D48_v3", "Standard_D64_v3", "Standard_D2a_v3", "Standard_D4a_v3", "Standard_D8a_v3", "Standard_D16a_v3", "Standard_D32a_v3", "Standard_D48a_v3", "Standard_D64a_v3", "Standard_DS1_v2", "Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2", "Standard_DS5_v2", "Standard_D1_v2", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_A1_v2", "Standard_A2_v2", "Standard_A4_v2", "Standard_A8_v2", "Standard_A2m_v2", "Standard_A4m_v2", "Standard_A8m_v2", "Standard_DC2s", "Standard_DC4s"]
windows_hpc_vms = ["Standard_HB60rs", "Standard_HC44rs", "Standard_H8", "Standard_H16", "Standard_H8m", "Standard_H16m", "Standard_H16r", "Standard_H16mr"]
windows_bseries_vms = ["Standard_B1ls1", "Standard_B1s", "Standard_B1ms", "Standard_B2s", "Standard_B2ms", "Standard_B4ms", "Standard_B8ms", "Standard_B12ms", "Standard_B16ms", "Standard_B20ms", "B16ms"]
windows_compute_optimized_vms = ["Standard_F2s_v2", "Standard_F4s_v2", "Standard_F8s_v2", "Standard_F16s_v2", "Standard_F32s_v2", "Standard_F48s_v2", "Standard_F64s_v2", "Standard_F72s_v22"]

windows_vms = [x.strip() for x in windows_vms.split(',')]
windows_vms.extend(windows_general_purpose_vms)
windows_vms.extend(windows_hpc_vms)
windows_vms.extend(windows_bseries_vms)
windows_vms.extend(windows_compute_optimized_vms )

for x in [x.lower() for x in windows_vms]:
    company_acronyms[x] = True
    company_acronyms[f'{x},'] = True
    company_acronyms[f'{x}.'] = True
    company_acronyms[f'({x}'] = True
    company_acronyms[f'({x},'] = True
    company_acronyms[f'{x})'] = True
    company_acronyms[f'{x})'] = True
    company_acronyms[f'{x}).'] = True
    if '_' in x:
        x = x.split('_')[1]
        company_acronyms[x] = True
        company_acronyms[f'{x},'] = True
        company_acronyms[f'{x}.'] = True
        company_acronyms[f'({x}'] = True
        company_acronyms[f'({x},'] = True
        company_acronyms[f'{x})'] = True
        company_acronyms[f'{x}).'] = True


for x in [x.lower() for x in _words_to_emphasize]:
    words_to_emphasize[x] = True
    words_to_emphasize[f'{x},'] = True
    words_to_emphasize[f'{x}.'] = True
    words_to_emphasize[f'({x}'] = True
    words_to_emphasize[f'({x},'] = True
    words_to_emphasize[f'{x})'] = True
    words_to_emphasize[f'{x})'] = True
    words_to_emphasize[f'{x}).'] = True

for key, val in _special_words.items():
    special_words[key] = val
    special_words[f'{key},'] = f'{val},'
    special_words[f'{key}.'] = f'{val}.'
    special_words[f'({key}'] = f'({val}'
    special_words[f'({key},'] = f'({val},'
    special_words[f'{key})'] = f'{val})'
    special_words[f'{key}).'] = f'{val}).'

def emphasize(phrase: str) -> str:
    return f'<emphasis>{phrase}</emphasis>'


def speak_slowly(phrase: str) -> str:
    return f'<prosody rate="slow">{phrase}</prosody>'


def spell_out(acronym: str) -> str:
    comma = ',' in acronym
    if comma:
        acronym = acronym.replace(',', '')
    if '(' in acronym and ')' in acronym:
        acronym = acronym.replace('(', '').replace(')', '')
        output = f'(<say-as interpret-as="characters">{acronym}</say-as>)'
    elif '(' in acronym:
        acronym = acronym.replace('(', '').replace(')', '')
        output = f'(<say-as interpret-as="characters">{acronym}</say-as>'
    elif ')' in acronym:
        acronym = acronym.replace('(', '').replace(')', '')
        output = f'<say-as interpret-as="characters">{acronym}</say-as>)'
    else:
        output = f'<say-as interpret-as="characters">{acronym}</say-as>'
    if comma:
        output = output + ','
    return speak_slowly(output)

with open(os.path.join(root, 'abbreviations.txt')) as f:
    abbrevs: List[str] = [x.lower() for x in f.readlines()]
with open(os.path.join(root, 'abbreviations2.txt')) as f:
    abbrevs.extend([x.lower() for x in f.readlines()])
with open(os.path.join(root, 'abbreviations3.txt')) as f:
    abbrevs.extend([x.lower() for x in f.readlines()])
with open(os.path.join(root, 'security.txt')) as f:
    abbrevs.extend([x.lower() for x in f.readlines()])
with open(os.path.join(root, 'aws1.txt')) as f:
    abbrevs.extend([x.lower() for x in f.readlines()])
for line in abbrevs:
    arr = [x.replace('\n', '') for x in line.split('----------')]
    if len(arr) != 2:
        continue
    abbreviations[arr[0]] = arr[1]
    abbreviations[f'({arr[0]})'] = f'({arr[1]})'
    abbreviations[f'({arr[0]}'] = f'({arr[1]}'
    abbreviations[f'({arr[0]},'] = f'({arr[1]},'
    abbreviations[f'{arr[0]})'] = f'{arr[1]})'
    flipped[f'({arr[1]})'] = arr[1]
    flipped[arr[1]] = arr[1]


company = 'azure'
company_edited = company + '_edited'
for filename in os.listdir(os.path.join(root, company)):
    with open(os.path.join(root, company, filename)) as f:
        lines: List[str] = [x.replace('\n', '') for x in f.readlines()]
        lines: List[str] = [x for x in lines if x]
    for index, line in enumerate(lines):
        line_lower = line.lower()
        line_arr: List[str] = line.split(' ')
        line_arr_lower: List[str] = line_lower.split(' ')
        for i, val in enumerate(line_arr_lower):
            # ignore common stop words in English language
            if val in stopwords:
                continue

            if val in special_words:
                line_arr[i] = special_words[val]
            elif val in words_to_emphasize:
                line_arr[i] = emphasize(val)
            elif val in company_acronyms:
                line_arr[i] = spell_out(val)
            elif val in abbreviations:
                if flipped[abbreviations[val]] in line_lower:
                    line_arr[i] = spell_out(val)
                else:
                    line_arr[i] = abbreviations[val]
        lines[index] =  '<p>' + post_process(' '.join(line_arr)) + '</p>\n'
    with open(os.path.join(root, company_edited, filename), 'w') as f:
        lines.insert(0, '\n\n<speak><amazon:auto-breaths>')
        lines.append('</amazon:auto-breaths></speak>\n\n')
        f.writelines(lines)
        transcripts[filename] = ''.join(lines)

target = 'azure_event_hubs_apache_kafka.txt'
output_s3_key_prefix = target.replace('.txt', '')
polly = boto3.Session(region_name='ap-northeast-2').client('polly')
response = polly.start_speech_synthesis_task(
        VoiceId='Joanna', 
        OutputS3BucketName=os.getenv('OUTPUT_S3_BUCKET_NAME'),
        OutputS3KeyPrefix=output_s3_key_prefix,
        OutputFormat='mp3', 
        Text=transcripts[target],
        TextType='ssml')
task_id = response['SynthesisTask']['TaskId']




