import random
import numpy as np
import pandas as pd

teams_data = pd.read_excel("countries.xlsx")

def simulate_playoff_match(team1, team2):
    mean_goals = 2.37
    std_dev_goals = 0.24
    goals = int(np.random.normal(mean_goals, std_dev_goals))

    ranking_factor = 1 / team1["fifa_ranking"]
    goals = int(goals * ranking_factor)

    return goals

# Tirage au sort des groupes
def simulate_draw(qualified_teams):
    chapeaux = {i: [] for i in range(1, 5)}
    
    # Tri des équipes par classement FIFA
    teams_data.sort_values("fifa_ranking", inplace=True)
    
    for _, team in teams_data.iterrows():
        if team["playoff"] is not np.nan:
            # Équipe issue des barrages
            qualified_team = qualified_teams.get(team["playoff"])
            if qualified_team:
                chapeau = team["hat"]
                if qualified_team not in chapeaux[chapeau]:
                    chapeaux[chapeau].append(qualified_team)
        else:
            # Équipe directement qualifiée
            chapeau = team["hat"]
            if team["name"] not in chapeaux[chapeau]:
                chapeaux[chapeau].append(team["name"])

    groups = {chr(65 + i): [] for i in range(6)}

    for chapeau in chapeaux.values():
        random.shuffle(chapeau)
        for group, team in zip(groups.values(), chapeau):
            group.append(team)

    return groups


# Simulation du calendrier de la phase de groupe
def simulate_group_schedule(groups):
    schedule = {}

    for group, teams in groups.items():
        schedule[group] = []
        for i in range(3):
            for j in range(i + 1, 4):
                match = (teams[i], teams[j])
                schedule[group].append(match)

    return schedule

def simulate_match(team1, team2):
    influence_factor = 0.2  # Ajustez ce facteur selon la sensibilité désirée à l'écart de classement
    mean_goals1 = np.exp(-influence_factor * team1["fifa_ranking"])
    mean_goals2 = np.exp(-influence_factor * team2["fifa_ranking"])

    mean_goals1 = min(mean_goals1, 4)
    mean_goals2 = min(mean_goals2, 4)

    max_random = random.randint(5, 7)

    ranking_difference = abs(team1["fifa_ranking"] - team2["fifa_ranking"])
    adjustment_factor = 0.2
    adjustment = max(1, ranking_difference * adjustment_factor)

    goals_team1 = max(0, min(round(np.random.normal(mean_goals1, 0.5) * adjustment), max_random))
    goals_team2 = max(0, min(round(np.random.normal(mean_goals2, 0.5) * adjustment), max_random))

    while goals_team1 == goals_team2:
        goals_team1 = max(0, min(round(np.random.normal(mean_goals1, 0.5) * adjustment), max_random))
        goals_team2 = max(0, min(round(np.random.normal(mean_goals2, 0.5) * adjustment), max_random))

    return goals_team1, goals_team2





# Simulation de la phase de groupe
def simulate_group_stage(groups, schedule):
    results = {}

    for group, matches in schedule.items():
        results[group] = []
        for match in matches:
            team1_name, team2_name = match
            team1 = teams_data.loc[teams_data["name"] == team1_name].iloc[0]
            team2 = teams_data.loc[teams_data["name"] == team2_name].iloc[0]

            goals_team1, goals_team2 = simulate_match(team1, team2)
            results[group].append((match, (goals_team1, goals_team2)))

    return results


# Calcul des points et classement
def calculate_points_and_ranking(results):
    standings = {}

    for group, matches in results.items():
        standings[group] = {"teams": {}, "points": {}, "goals_for": {}, "goals_against": {}}

        for match, (goals_team1, goals_team2) in matches:
            team1, team2 = match

            if team1 not in standings[group]["points"]:
                standings[group]["points"][team1] = 0
                standings[group]["goals_for"][team1] = 0
                standings[group]["goals_against"][team1] = 0

            if team2 not in standings[group]["points"]:
                standings[group]["points"][team2] = 0
                standings[group]["goals_for"][team2] = 0
                standings[group]["goals_against"][team2] = 0

            # Mise à jour des points
            if goals_team1 > goals_team2:
                standings[group]["points"][team1] += 3
            elif goals_team1 < goals_team2:
                standings[group]["points"][team2] += 3
            else:
                standings[group]["points"][team1] += 1
                standings[group]["points"][team2] += 1

            # Mise à jour des buts
            standings[group]["goals_for"][team1] += goals_team1
            standings[group]["goals_against"][team1] += goals_team2

            standings[group]["goals_for"][team2] += goals_team2
            standings[group]["goals_against"][team2] += goals_team1

    return standings


# Fonction pour obtenir les meilleurs 3èmes parmi tous les groupes
def get_best_third(standings):
    all_thirds = []

    for group in standings:
        if "points" in standings[group] and "goals_for" in standings[group] and "goals_against" in standings[group]:
            teams_sorted = sorted(standings[group]["points"].keys(), key=lambda x: (standings[group]["points"][x], standings[group]["goals_for"][x] - standings[group]["goals_against"][x]), reverse=True)
            if len(teams_sorted) >= 3:
                third_place = teams_sorted[2]
                all_thirds.append((group, third_place))

    # Triez les meilleurs 3èmes par points et différence de buts
    all_thirds.sort(key=lambda x: (standings[x[0]]["points"][x[1]], standings[x[0]]["goals_for"][x[1]] - standings[x[0]]["goals_against"][x[1]]), reverse=True)

    # Sélectionnez les quatre meilleurs 3èmes
    best_thirds = [team[1] for team in all_thirds[:4]]
    
    return best_thirds


def gagnant(results, match_id):
    teams, scores = results[match_id]
    if scores[0] > scores[1]:
        return teams[0], scores[0]
    elif scores[0] < scores[1]:
        return teams[1], scores[1]
    else:
        return None 
    
def perdant(results, match_id):
    teams, scores = results[match_id]
    if scores[0] < scores[1]:
        return teams[0], scores[0]
    elif scores[0] > scores[1]:
        return teams[1], scores[1]
    else:
        return None 
