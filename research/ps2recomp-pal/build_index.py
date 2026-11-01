"""Index local PS2Recomp output against OpenRAC, without copying game code."""
import argparse
import collections
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated-main', required=True, type=Path)
    parser.add_argument('--generated-frontbin', required=True, type=Path)
    parser.add_argument('--base-ref', default='origin/main')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    base = subprocess.check_output(['git', 'rev-parse', args.base_ref], cwd=root, text=True).strip()

    def original(path):
        return subprocess.check_output(['git', 'show', base + ':' + path], cwd=root, text=True)

    def statuses(text):
        result = collections.defaultdict(set)
        for line in text.splitlines():
            if line and not line.startswith('#'):
                fields = line.split('\t')
                for name in re.findall(r'func_(?:(?:L\d\d|FB)_)?[0-9A-F]{8}', fields[3]):
                    result[name].add(fields[2])
        return result

    before = statuses(original('config/pal/map.tsv'))
    after = statuses((root / 'config/pal/map.tsv').read_text())
    pairs = dict(line.split('\t') for line in original('config/pal/frontend_pairs.tsv').splitlines()
                 if line and not line.startswith('#'))
    outputs = {'main': args.generated_main, 'frontbin': args.generated_frontbin}
    files = {program: {p.name: p for p in directory.glob('*.cpp')}
             for program, directory in outputs.items()}
    registrations = {program: {int(a, 16) for a in re.findall(r'// 0x([0-9a-fA-F]+)',
                     (directory / 'register_functions.cpp').read_text())}
                     for program, directory in outputs.items()}
    rows = []
    counts = {program: collections.Counter() for program in outputs}
    for line in original('config/pal/inventory.tsv').splitlines():
        if not line or line.startswith('#'):
            continue
        program, section, address, size, kind = line.split('\t')
        number = int(address, 16)
        direct_name = ('func_FB_' if program == 'frontbin' else 'func_') + address
        canonical = pairs.get(direct_name, direct_name)
        source = files[program].get(f'sub_{address}_0x{number:x}.cpp')
        text = source.read_text() if source else ''
        header = re.search(r'// Address: 0x([0-9a-fA-F]+) - 0x([0-9a-fA-F]+)', text)
        assert header and int(header[1], 16) == number and int(header[2], 16) == number + int(size), direct_name
        assert number in registrations[program], direct_name
        unhandled = len(re.findall(r'throw std::runtime_error\(', text))
        baseline = 'match' if 'match' in before[canonical] else ','.join(sorted(before[canonical])) or 'no_source_mapping'
        if baseline == 'match':
            classification = 'already_matched'
        elif 'match' in after[canonical]:
            classification = 'new_matching_c'
        elif kind == 'remnant':
            classification = 'fragment_unverified'
        elif unhandled:
            classification = 'generated_with_unhandled'
        else:
            classification = 'generated_unverified'
        if program == 'frontbin' and canonical != direct_name:
            if classification == 'already_matched':
                classification = 'paired_main_existing_match'
            elif classification == 'new_matching_c':
                classification = 'paired_main_new_match'
        counts[program][classification] += 1
        rows.append([program, section, address, size, kind, canonical, baseline, classification, unhandled])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    index = args.output_dir / 'translation-index.tsv'
    with index.open('w', encoding='utf-8', newline='') as output:
        writer = csv.writer(output, delimiter='\t', lineterminator='\n')
        writer.writerow(['program', 'section', 'address', 'size', 'kind', 'canonical_name',
                         'baseline_status', 'classification', 'generated_throws'])
        writer.writerows(rows)
    summary = {
        'base_commit': base,
        'inventory_ranges': len(rows),
        'classification_counts': counts,
        'new_matching_canonical_functions': sorted({r[5] for r in rows if r[7] == 'new_matching_c'}),
        'generated_throw_count_per_program': {p: sum(r[8] for r in rows if r[0] == p) for p in outputs},
        'index_sha256': hashlib.sha256(index.read_bytes()).hexdigest(),
        'limitations': [
            'Generated C++ is a translation candidate, not a matching C decompilation.',
            'Frontend pairs are normalized using OpenRAC metadata, not counted as independent matches.',
            'Index covers the main/frontend inventory only; level programs are not translated here.',
            'Instruction comments and runtime throws do not prove semantic correctness or reachability.',
            'Fragments and embedded data can appear in executable ranges.',
        ],
    }
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
