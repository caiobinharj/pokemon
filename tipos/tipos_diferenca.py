import itertools

# Tabela de eficácia (Geração 6+). 
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

def get_multiplier(atk, dfn):
    """Retorna o multiplicador de dano direto."""
    return type_chart.get(atk, {}).get(dfn, 1.0)

def calc_defense_score_171(t1, t2):
    """
    Simula o Pokémon (t1/t2) recebendo ataques STAB de todos os 
    171 possíveis atacantes da pokedex teórica.
    """
    score = 0
    for atk1, atk2 in combinations:
        # O atacante usará o golpe que causar mais dano (melhor STAB)
        mult1 = get_multiplier(atk1, t1) * (get_multiplier(atk1, t2) if t1 != t2 else 1.0)
        mult2 = get_multiplier(atk2, t1) * (get_multiplier(atk2, t2) if t1 != t2 else 1.0)
        
        best_incoming_mult = max(mult1, mult2)
        score += best_incoming_mult
    return score

# O cálculo ofensivo permanece o mesmo:
# calc_offense_score(t1, t2) -> Ataca as 171 combinações



def calc_offense_score(atk1, atk2):
    """
    Soma os multiplicadores do melhor ataque (STAB) contra as 171 combinações defensivas.
    Valores maiores = melhor ataque (causa mais dano no geral).
    """
    score = 0
    for def1, def2 in combinations:
        mult1 = get_multiplier(atk1, def1) * (get_multiplier(atk1, def2) if def1 != def2 else 1.0)
        mult2 = get_multiplier(atk2, def1) * (get_multiplier(atk2, def2) if def1 != def2 else 1.0)
        
        best_mult = max(mult1, mult2)
        score += best_mult
        
    return score



ranking = []
for t1, t2 in combinations:
    # Agora ambos usam a base 171
    def_score = calc_defense_score_171(t1, t2)
    off_score = calc_offense_score(t1, t2)
    
    total_score = total_score = off_score-def_score
    name = t1 if t1 == t2 else f"{t1}/{t2}"
    
    ranking.append({
        'Tipagem': name,
        'Ataque': off_score,
        'Defesa': def_score,
        'Total': total_score
    })

# Ordenar do maior saldo (melhor) para o menor saldo (pior)
ranking = sorted(ranking, key=lambda x: x['Total'], reverse=True)

# Exibir o Top 20
print(f"{'Rank':<5} | {'Tipagem':<15} | {'Ataque (Causa)':<15} | {'Defesa (Sofre)':<15} | {'Total (Saldo)'}")
print("-" * 75)
for i, r in enumerate(ranking[:171]):
    print(f"{i+1:<5} | {r['Tipagem']:<15} | {r['Ataque']:<15.2f} | {r['Defesa']:<15.2f} | {r['Total']:.2f}")