# -*- coding: utf_8 -*-
import glob
import pprint
from types import SimpleNamespace

import simplejson as json


def process_synonyms(syn_list):
    return [syn.Name for syn in syn_list if syn.LangID == 'en' and (syn.Reliability >= 4 or
                                                                    ('Rank' in syn.__dict__.keys() and syn.Rank is 1))]


def clean_formula(formula: str):
    return formula.replace('_', '').replace('{', '').replace('}', '')


def filter_identifiers(id_list):
    valid_id_types = {0: 'inchi_code', 2: 'inchi_key', 1: 'smiles'}
    inchi_ver = 'v1.02s'

    clean_ids = {}
    for id in id_list:
        if id.IdentifierType in valid_id_types:
            if id.IdentifierType is 1 or (id.IdentifierType in [0, 2] and id.Version == inchi_ver):
                clean_ids[valid_id_types.get(id.IdentifierType)] = id.Value

    return clean_ids


def parse(filename, stats):
    with open(filename, 'r') as csfile:
        csobj = json.load(csfile, object_hook=lambda d: SimpleNamespace(**d))
        if not csobj.IsDeprecated:
            stats['current'] += 1
            print(f'CSID: {csobj.CSID}\n'
                  f'Deprecated: {csobj.IsDeprecated}\n'
                  f'Name: {csobj.Name}\n'
                  f'Accurate Mass: {csobj.AM}\n'
                  f'Molecular Formula: {clean_formula(csobj.MF)}\n'
                  f'Molecular Weight: {csobj.MW}\n'
                  f'Identifiers: {filter_identifiers(csobj.Identifiers)}\n'
                  f'Mol definition: {csobj.Mol}\n'
                  f'DataSourcesCount: {csobj.DataSourcesCount}\n'
                  f'ReferencesCount: {csobj.ReferencesCount}\n'
                  f'PubmedHits: {csobj.PubmedHits}\n'
                  f'RSCHits: {csobj.RSCHits}\n'
                  f'Synonyms: {process_synonyms(csobj.Synonyms)}')
        else:
            stats['deprecated'] += 1


def process_folder(csfolder):
    stats = {'deprecated': 0, 'current': 0}

    csfiles = glob.glob(f'{csfolder}/*.json')
    print(f'{len(csfiles)} files to parse\n {csfiles}')
    [parse(f, stats) for f in csfiles]

    print(stats)


if __name__ == '__main__':
    csfolder = './csfiles'
    process_folder(csfolder)
