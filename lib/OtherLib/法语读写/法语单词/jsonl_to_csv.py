import json
import csv
import sys
import os

input_file = 'kaikki.org-dictionary-French-words.jsonl'
output_file = 'french_words.csv'

def extract_gender(data):
    pos = data.get('pos')
    if pos != 'noun':
        return pos
    
    # Try head_templates
    head_templates = data.get('head_templates', [])
    if head_templates:
        for template in head_templates:
            args = template.get('args', {})
            # Common keys for gender in French wiktionary templates
            g = args.get('1') or args.get('g')
            if g in ['m', 'f', 'm-p', 'f-p']:
                return f"noun ({g})"
            
    # Try senses tags if head_templates didn't work
    for sense in data.get('senses', []):
        tags = sense.get('tags', [])
        if 'masculine' in tags:
            return "noun (m)"
        if 'feminine' in tags:
            return "noun (f)"
            
    return "noun"

def extract_definitions(data):
    definitions = []
    for sense in data.get('senses', []):
        glosses = sense.get('glosses', [])
        if glosses:
            definitions.extend(glosses)
    return "; ".join(definitions)

def extract_synonyms(data):
    synonyms = []
    # Check senses synonyms
    for sense in data.get('senses', []):
        for syn in sense.get('synonyms', []):
            if 'word' in syn:
                synonyms.append(syn['word'])
    return "; ".join(list(set(synonyms))) # Unique

def extract_examples(data):
    examples = []
    for sense in data.get('senses', []):
        for ex in sense.get('examples', []):
            text = ex.get('text', '')
            translation = ex.get('translation', '')
            if text:
                if translation:
                    examples.append(f"{text} ({translation})")
                else:
                    examples.append(text)
    return " | ".join(examples)

def extract_audio(data):
    audios = []
    for sound in data.get('sounds', []):
        mp3 = sound.get('mp3_url')
        if mp3:
            audios.append(mp3)
    return "; ".join(audios)

def extract_forms(data):
    forms_list = []
    for form in data.get('forms', []):
        f = form.get('form', '')
        tags = form.get('tags', [])
        if f:
            tag_str = ",".join(tags)
            forms_list.append(f"{f} [{tag_str}]")
    return "; ".join(forms_list)

def extract_derived(data):
    derived_list = []
    for d in data.get('derived', []):
        w = d.get('word')
        if w:
            derived_list.append(w)
    return "; ".join(derived_list)

def main():
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f_in, \
             open(output_file, 'w', encoding='utf-8', newline='') as f_out:
            
            writer = csv.writer(f_out)
            headers = ['单词', '词性', '英文释义', '同义词', '用例', '音频链接', '词形变化', '派生词']
            writer.writerow(headers)
            
            count = 0
            for line in f_in:
                try:
                    data = json.loads(line)
                    
                    word = data.get('word', '')
                    pos = extract_gender(data)
                    definition = extract_definitions(data)
                    synonyms = extract_synonyms(data)
                    examples = extract_examples(data)
                    audio = extract_audio(data)
                    forms = extract_forms(data)
                    derived = extract_derived(data)
                    
                    writer.writerow([word, pos, definition, synonyms, examples, audio, forms, derived])
                    count += 1
                    if count % 10000 == 0:
                        print(f"Processed {count} words...")
                except json.JSONDecodeError:
                    continue
                    
        print(f"Done! Processed {count} words. Saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
