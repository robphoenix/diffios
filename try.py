import re

baseline = ['hostname {{ HOSTNAME }} yet another {{one}}']
config = ['hostname ROUTER_01 yet another two']

bs = baseline[0].split()
bsr = re.split('({{[^{}]+}})', baseline[0])

print(bsr)
print(config[0].split())

if '{{' in bs:
    print('orphans!!')

end = '}}'

indexes = []
for el in bs:
    if el == '{{':
        indexes.append(bs.index(el))
    elif el == '}}':
        indexes.append(bs.index(el))


rest, coord = [], []

for i, el in enumerate(indexes, 1):
    if i % 2 != 0:
        coord.append(el)
    else:
        coord.append(el)
        rest.append(tuple(coord))
        coord = []


