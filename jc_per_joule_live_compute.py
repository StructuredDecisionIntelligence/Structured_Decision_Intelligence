import json, sys

d = json.load(sys.stdin)
event = d.get('event', {})
audit = event.get('AUDIT', {})
metrics = audit.get('metrics', {})
entry = event.get('ENTRY', {})
meta = entry.get('meta', {})
total_tokens = meta.get('SDI_DER', {}).get('META', {}).get('tokens_actual', {}).get('total_tokens')

jc_clt = metrics.get('Jc_clt')
jc_per_joule_low = metrics.get('jc_per_joule_low')
jc_per_joule_high = metrics.get('jc_per_joule_high')

J_LOW_MJ_PER_TOKEN = 0.003
J_HIGH_MJ_PER_TOKEN = 1.0

computed_low = round(jc_clt / (total_tokens * J_HIGH_MJ_PER_TOKEN), 4) if jc_clt and total_tokens else None
computed_high = round(jc_clt / (total_tokens * J_LOW_MJ_PER_TOKEN), 4) if jc_clt and total_tokens else None

print('=== jc_per_joule, computed live from this record\'s own declared values ===')
print()
print(f'Jc_clt        = {jc_clt}')
print(f'total_tokens  = {total_tokens}')
print()
print('energy range  : 0.003 to 1.0 mJ/token')
print('source        : M. Fadel Argerich, J. Furst, M. Patino-Martinez,')
print('                "Watt Counts: Energy-Aware Benchmark for Sustainable')
print('                LLM Inference on Heterogeneous GPU Architectures,"')
print('                arXiv:2604.09048, 2026.')
print()
print('formula:')
print('  jc_per_joule_low  = Jc_clt / (total_tokens x 1.0)   [higher energy assumption]')
print('  jc_per_joule_high = Jc_clt / (total_tokens x 0.003) [lower energy assumption]')
print()
print(f'computed jc_per_joule_low  : {computed_low}')
print(f'published jc_per_joule_low : {jc_per_joule_low}')
print(f'match                      : {computed_low == jc_per_joule_low}')
print()
print(f'computed jc_per_joule_high  : {computed_high}')
print(f'published jc_per_joule_high : {jc_per_joule_high}')
print(f'match                       : {computed_high == jc_per_joule_high}')
print()
print('This is a descriptive empirical spread, not a statistical')
print('confidence interval, and not a coverage guarantee for any')
print('specific deployment. The same range is applied to every act')
print('regardless of which model produced it, since Watt Counts')
print('contains no model- or hardware-stratified result precise')
print('enough to justify differentiating the coefficient by model.')
print('Watt Counts measures models smaller than the frontier models')
print('this system runs on; this range is an extrapolation beyond')
print('directly tested data.')
