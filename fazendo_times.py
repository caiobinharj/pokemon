import pandas as pd
import numpy as np
import re
import math
from scipy.optimize import milp, LinearConstraint, Bounds

def ajustar_score_tipagem(score_original):
    """
    Aplica a lógica logarítmica para scores positivos (retornos decrescentes)
    e linear para negativos (punição direta).
    """
    peso_log = 20.0  # Ajusta a escala do log para ser comparável ao BST
    if score_original >= 0:
        # np.log1p é o logaritmo de (1 + x), evita erro com zero e é mais preciso
        return np.log1p(score_original) * peso_log
    else:
        # Mantém a punição linear para tipos ruins
        return score_original * 1.5

def parse_md_tables(file_path):
    pokemons = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    rows = re.findall(r'\| (\d+) \| \*\*(.*?)\*\* \| (.*?) \| (.*?) \| (.*?) \((\d+)\) \|', content)
    for row in rows:
        p_id, name, t1, t2, stats, bst = row
        name = name.strip()
        t1 = t1.strip()
        t2 = t2.strip() if t2.strip() != '' else None
        if t1 == t2: t2 = None 
        bst = int(bst)
        
        if name not in pokemons:
            pokemons[name] = {'name': name, 'type1': t1, 'type2': t2, 'bst': bst}
    return list(pokemons.values())

def extract_rankings_robust(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    res = {}
    lines = content.split('\n')
    current_type = None
    for line in lines:
        type_match = re.search(r'([A-Z][a-z]+(?:/[A-Z][a-z]+)?)\s*\|', line)
        if type_match:
            current_type = type_match.group(1).strip()
        nums = re.findall(r'-?\d+\.\d+', line)
        if current_type and nums:
            score = float(nums[-1])
            if '/' in current_type:
                t1, t2 = current_type.split('/')
                res[tuple(sorted([t1.strip(), t2.strip()]))] = score
            else:
                res[(current_type.strip(),)] = score
    return res

# --- CARREGAMENTO E PROCESSAMENTO COM A NOVA LÓGICA ---
pokes = parse_md_tables('clover/tabelas_por_tipo.md')
typing_scores = extract_rankings_robust('tipos/ranking_tipagem_pokemon_logaritmica.csv')

data = []
for p in pokes:
    t_key = tuple(sorted([p['type1'], p['type2']])) if p['type2'] else (p['type1'],)
    t_score_original = typing_scores.get(t_key, 0)
    
    # APLICAÇÃO DA IDEIA LOGARÍTMICA
    t_score_ajustado = ajustar_score_tipagem(t_score_original)
    
    p['score_tipagem_original'] = t_score_original
    p['score_tipagem_ajustado'] = t_score_ajustado
    p['score'] = p['bst'] + t_score_ajustado  # O score final usado na otimização
    data.append(p)

df = pd.DataFrame(data)

all_types = sorted(list(set(df['type1']).union(set(df['type2'].dropna()))))
N = len(df)

# Configuração MILP
c = -df['score'].values
bounds = Bounds(0, 1)
integrality = np.ones(N)

A_eq = np.ones((1, N))
b_eq = np.array([6])
A_ub_list = []
b_ub_list = []

for t in all_types:
    row = np.zeros(N)
    for i in range(N):
        if df.iloc[i]['type1'] == t or df.iloc[i]['type2'] == t:
            row[i] = 1
    A_ub_list.append(row)
    b_ub_list.append(1)

teams = []
num_teams_to_find = 100

print(f"Otimizando 100 times com lógica logarítmica (Peso: 20)...")
for rank in range(1, num_teams_to_find + 1):
    if len(A_ub_list) > 0:
        A_ub = np.vstack(A_ub_list)
        b_ub = np.array(b_ub_list)
    else:
        A_ub = None
        b_ub = None
        
    constraints = [LinearConstraint(A_eq, b_eq, b_eq)]
    if A_ub is not None:
        constraints.append(LinearConstraint(A_ub, -np.inf, b_ub))
        
    res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)
    
    if res.success:
        selected_indices = [i for i, val in enumerate(res.x) if val > 0.5]
        team_pokes = df.iloc[selected_indices]
        teams.append({
            'rank': rank,
            'total_score': team_pokes['score'].sum(),
            'total_bst': team_pokes['bst'].sum(),
            'members': team_pokes.to_dict('records')
        })
        
        # Corte para excluir este time da próxima iteração
        row = np.zeros(N)
        for i in selected_indices:
            row[i] = 1
        A_ub_list.append(row)
        b_ub_list.append(5) 
    else:
        break

teams.sort(key=lambda x: (x['total_score'], x['total_bst']), reverse=True)

for i, team in enumerate(teams):
    team['rank'] = i + 1

# Geração do arquivo
with open('ranking_times_pokemon_logaritmico.txt', 'w', encoding='utf-8') as f:
    f.write("RANKING DE TIMES POKÉMON - LÓGICA LOGARÍTMICA\n")
    f.write("Critério: BST + (Log(Score Tipagem + 1) * 20) para positivos.\n")
    f.write("Punição: Score Tipagem * 1.5 para negativos.\n")
    f.write("=" * 90 + "\n\n")
    
    for team in teams:
        f.write(f"TIME RANK #{team['rank']}\n")
        f.write(f"Score Otimizado: {team['total_score']:.2f} | Total BST: {team['total_bst']}\n")
        f.write("-" * 50 + "\n")
        for p in team['members']:
            t2_str = f"/{p['type2']}" if p['type2'] else ""
            f.write(f"• {p['name']:<15} | Tipo: {p['type1']}{t2_str:<12} | BST: {p['bst']} | Score Tipagem: {p['score_tipagem_original']:>6.2f} (Ajustado: {p['score_tipagem_ajustado']:>6.2f})\n")
        f.write("\n")

print("Processo finalizado! O arquivo 'ranking_times_pokemon_logaritmico.txt' foi gerado.")