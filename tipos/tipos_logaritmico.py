import itertools
import math

# Tabela de eficácia (Geração 6+)
type_chart = {
    'Normal': {'Rock': 0.5, 'Ghost': 0, 'Steel': 0.5},
    'Fire': {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 2, 'Bug': 2, 'Rock': 0.5, 'Dragon': 0.5, 'Steel': 2},
    'Water': {'Fire': 2, 'Water': 0.5, 'Grass': 0.5, 'Ground': 2, 'Rock': 2, 'Dragon': 0.5},
    'Electric': {'Water': 2, 'Electric': 0.5, 'Grass': 0.5, 'Ground': 0, 'Flying': 2, 'Dragon': 0.5},
    'Grass': {'Fire': 0.5, 'Water': 0.5, 'Grass': 0.5, 'Poison': 0.5, 'Ground': 2, 'Flying': 0.5, 'Bug': 0.5, 'Rock': 2, 'Dragon': 0.5, 'Steel': 0.5},
    'Ice': {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 0.5, 'Ground': 2, 'Flying': 2, 'Dragon': 2, 'Steel': 0.5},
    'Fighting': {'Normal': 2, 'Ice': 2, 'Poison': 0.5, 'Flying': 0.5, 'Psychic': 0.5, 'Bug': 0.5, 'Rock': 2, 'Ghost': 0, 'Dark': 2, 'Steel': 2, 'Fairy': 0.5},
    'Poison': {'Grass': 2, 'Poison': 0.5, 'Ground': 0.5, 'Rock': 0.5, 'Ghost': 0.5, 'Steel': 0, 'Fairy': 2},
    'Ground': {'Fire': 2, 'Electric': 2, 'Grass': 0.5, 'Poison': 2, 'Flying': 0, 'Bug': 0.5, 'Rock': 2, 'Steel': 2},
    'Flying': {'Electric': 0.5, 'Grass': 2, 'Fighting': 2, 'Bug': 2, 'Rock': 0.5, 'Steel': 0.5},
    'Psychic': {'Fighting': 2, 'Poison': 2, 'Psychic': 0.5, 'Dark': 0, 'Steel': 0.5},
    'Bug': {'Fire': 0.5, 'Grass': 2, 'Fighting': 0.5, 'Poison': 0.5, 'Flying': 0.5, 'Psychic': 2, 'Ghost': 0.5, 'Dark': 2, 'Steel': 0.5, 'Fairy': 0.5},
    'Rock': {'Fire': 2, 'Ice': 2, 'Fighting': 0.5, 'Ground': 0.5, 'Flying': 2, 'Bug': 2, 'Steel': 0.5},
    'Ghost': {'Normal': 0, 'Psychic': 2, 'Ghost': 2, 'Dark': 0.5},
    'Dragon': {'Dragon': 2, 'Steel': 0.5, 'Fairy': 0},
    'Dark': {'Fighting': 0.5, 'Psychic': 2, 'Ghost': 2, 'Dark': 0.5, 'Fairy': 0.5},
    'Steel': {'Fire': 0.5, 'Water': 0.5, 'Electric': 0.5, 'Ice': 2, 'Rock': 2, 'Steel': 0.5, 'Fairy': 2},
    'Fairy': {'Fighting': 2, 'Poison': 0.5, 'Dragon': 2, 'Dark': 2, 'Steel': 0.5, 'Fire': 0.5}
}

types = list(type_chart.keys())
combinations = list(itertools.combinations_with_replacement(types, 2))

IMMUNITY_VALUE = -3.0  # Valor logarítmico para multiplicador 0

def get_multiplier(atk, dfn):
    return type_chart.get(atk, {}).get(dfn, 1.0)

def to_log(mult):
    if mult == 0:
        return IMMUNITY_VALUE
    return math.log2(mult)

def calc_scores(t1, t2):
    off_score = 0
    def_score = 0
    
    for o1, o2 in combinations:
        # OFFENSE: Qual o melhor STAB que (t1,t2) tem contra o oponente (o1,o2)?
        m1_t1 = get_multiplier(t1, o1) * (get_multiplier(t1, o2) if o1 != o2 else 1.0)
        m2_t2 = get_multiplier(t2, o1) * (get_multiplier(t2, o2) if o1 != o2 else 1.0)
        off_score += to_log(max(m1_t1, m2_t2))
        
        # DEFENSE: Qual o melhor STAB que o oponente (o1,o2) tem contra você (t1,t2)?
        m1_o1 = get_multiplier(o1, t1) * (get_multiplier(o1, t2) if t1 != t2 else 1.0)
        m2_o2 = get_multiplier(o2, t1) * (get_multiplier(o2, t2) if t1 != t2 else 1.0)
        def_score += to_log(max(m1_o1, m2_o2))
        
    return off_score, def_score

ranking = []
for t1, t2 in combinations:
    off, dbf = calc_scores(t1, t2)
    total = off - dbf
    name = t1 if t1 == t2 else f"{t1}/{t2}"
    ranking.append({'Tipo': name, 'Off': off, 'Def': dbf, 'Total': total})

ranking = sorted(ranking, key=lambda x: x['Total'], reverse=True)

print(f"{'Rank':<5} | {'Tipagem':<15} | {'Ofensivo':<10} | {'Defensivo':<10} | {'Saldo Final'}")
print("-" * 65)
for i, r in enumerate(ranking[:172]):
    print(f"{i+1:<5} | {r['Tipo']:<15} | {r['Off']:>10.2f} | {r['Def']:>10.2f} | {r['Total']:>10.2f}")