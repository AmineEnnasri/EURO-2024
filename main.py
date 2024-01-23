import random
import pandas as pd
import tkinter as tk
from tkinter import ttk
from euro import simulate_playoff_match, simulate_match, gagnant, perdant, simulate_group_stage, calculate_points_and_ranking, simulate_draw, simulate_group_schedule, get_best_third

teams_data = pd.read_excel("countries.xlsx")

# Définir le nombre de simulations
nombre_simulations = 1

# Création de la table initiale
equipes_stats = pd.DataFrame(data={
    "equipe": teams_data["name"],
    "1er Place": 0,
    "2eme Place": 0,
    "3eme Place": 0,
    "nombre_matches": 0,
    "nombre_buts_groupe": 0,
    "nombre_buts_8eme": 0,
    "nombre_buts_quart": 0,
    "nombre_buts_classement": 0,
    "nombre_buts_demi": 0,
    "nombre_buts_finale": 0,
    "nombre_buts": 0,
    "pourcentage_gain": 0
})

for simulation in range(nombre_simulations):
    print("\n***********************************************************************")
    print(f"Simulation {simulation + 1}/{nombre_simulations}")

    # Sélectionnez les équipes issues des matchs de barrage
    playoff_teams = teams_data[teams_data["playoff"].notna()]

    # Dictionnaire pour stocker les résultats des groupes de barrage
    playoff_results = {group: [] for group in playoff_teams["playoff"].unique()}

    # Simulez les matchs de barrage
    for group, teams in playoff_teams.groupby("playoff"):
        group_teams = list(teams["name"])
        random.shuffle(group_teams)

        # Simulez les matchs entre les équipes du groupe de barrage
        for i in range(3):
            for j in range(i + 1, 4):
                team1_name, team2_name = group_teams[i], group_teams[j]
                team1 = teams_data.loc[teams_data["name"] == team1_name].iloc[0]
                team2 = teams_data.loc[teams_data["name"] == team2_name].iloc[0]

                result = simulate_playoff_match(team1, team2)
                playoff_results[group].append(((team1_name, team2_name), result))

    # Sélectionnez le vainqueur de chaque groupe de barrage
    qualified_teams = {}
    for group, results in playoff_results.items():
        qualified_team = max(results, key=lambda x: x[1])[0][0]
        qualified_teams[group] = qualified_team

    # Affichez les équipes qualifiées
    print("\nÉquipes qualifiées pour l'Euro :")
    for group, team in qualified_teams.items():
        print(f"Groupe {group}: {team}")


    draw_results = simulate_draw(qualified_teams)
    group_stage_schedule = simulate_group_schedule(draw_results)
    group_stage_results = simulate_group_stage(draw_results, group_stage_schedule)
    standings = calculate_points_and_ranking(group_stage_results)

    # Affichage des résultats du tirage au sort
    print("\nRésultats du tirage au sort :")
    for group, teams in draw_results.items():
        print(f"Groupe {group}: {teams}")

    # Affichage du calendrier et des résultats de la phase de groupe
    print("\nCalendrier de la phase de groupe :")
    for group, matches in group_stage_schedule.items():
        print(f"Groupe {group}: {matches}")

    print("\nRésultats de la phase de groupe :")
    for group, results in group_stage_results.items():
        print(f"Groupe {group}: {results}")

    # Affichage du classement
    print("\nClassement final :")
    for group, standing in standings.items():
        print("------------------------------------------------------------------")
        print(f"\nGroupe {group} :")
        print("{:<20} {:<7} {:<10} {:<15} {:<20}".format("\nÉquipe", "Points", "Buts pour", "Buts contre", "Différence de buts"))
        for team, points in sorted(standing["points"].items(), key=lambda x: (x[1], standing["goals_for"][x[0]] - standing["goals_against"][x[0]]), reverse=True):
            goals_for = standing["goals_for"].get(team, 0)
            goals_against = standing["goals_against"].get(team, 0)
            goal_difference = goals_for - goals_against
            print("{:<20} {:<7} {:<10} {:<15} {:<20}".format(team, points, goals_for, goals_against, goal_difference))
            equipes_stats.loc[equipes_stats["equipe"] == team, "nombre_buts_groupe"] += goals_for
            equipes_stats.loc[equipes_stats["equipe"] == team, "nombre_matches"] += 3


    # Extraire les équipes classées 1ères et 2èmes de chaque groupe
    group_winners = {}
    group_runners_up = {}
    for group, standing in standings.items():
        teams_sorted = sorted(standing["points"].keys(), key=lambda x: (standing["points"][x], standing["goals_for"][x] - standing["goals_against"][x]), reverse=True)
        group_winners[group] = teams_sorted[0]
        group_runners_up[group] = teams_sorted[1]

    import itertools

    # Obtenir les meilleurs 3èmes parmi tous les groupes
    best_thirds = get_best_third(standings)

    # Tirage au sort pour attribuer les meilleurs 3èmes à des matchs
    random.shuffle(best_thirds)

    # Matches des huitièmes de finale
    qualified_teams = {
        "38": (group_runners_up["A"], group_runners_up["B"]),
        "37": (group_winners["A"], group_runners_up["C"]),
        "40": (group_winners["C"], best_thirds[0]),
        "39": (group_winners["B"], best_thirds[1]),
        "42": (group_runners_up["D"], group_runners_up["E"]),
        "41": (group_winners["F"], best_thirds[2]),
        "43": (group_winners["E"], best_thirds[3]),
        "44": (group_winners["D"], group_runners_up["F"]),
    }

    # Afficher les équipes qualifiées
    print("-------------------------------------------------")
    print("\nÉquipes qualifiées pour les huitièmes de finale :")
    for match, teams in qualified_teams.items():
        print(f"Match {match}: {teams[0]} vs {teams[1]}")


    # Simulation des huitièmes de finale
    knockout_results = {}
    for match, teams in qualified_teams.items():
        team1, team2 = teams
        goals_team1, goals_team2 = simulate_match(teams_data.loc[teams_data["name"] == team1].iloc[0], teams_data.loc[teams_data["name"] == team2].iloc[0])
        knockout_results[match] = ((team1, team2), (goals_team1, goals_team2))
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_buts_8eme"] += goals_team1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_buts_8eme"] += goals_team2
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_matches"] += 1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_matches"] += 1

    # Affichage des résultats des huitièmes de finale
    print("\nRésultats des huitièmes de finale :")
    for match, (teams, scores) in knockout_results.items():
        print(f"Match {match}: {teams[0]} {scores[0]} - {scores[1]} {teams[1]}")

    # Utilisation de la fonction pour obtenir les équipes gagnantes des quarts de finale
    equipe_gagnante_37 = gagnant(knockout_results, "37")[0]
    equipe_gagnante_38 = gagnant(knockout_results, "38")[0]
    equipe_gagnante_39 = gagnant(knockout_results, "39")[0]
    equipe_gagnante_40 = gagnant(knockout_results, "40")[0]
    equipe_gagnante_41 = gagnant(knockout_results, "41")[0]
    equipe_gagnante_42 = gagnant(knockout_results, "42")[0]
    equipe_gagnante_43 = gagnant(knockout_results, "43")[0]
    equipe_gagnante_44 = gagnant(knockout_results, "44")[0]

    # Matches des quarts de finale
    quarterfinal_matches = {
        "45": (equipe_gagnante_39, equipe_gagnante_37),
        "46": (equipe_gagnante_41, equipe_gagnante_42),
        "48": (equipe_gagnante_40, equipe_gagnante_38),
        "47": (equipe_gagnante_43, equipe_gagnante_44),
    }

    # Afficher les matches des quarts de finale
    print("-------------------------------------------------")
    print("\nMatches des quarts de finale :")
    for match, teams in quarterfinal_matches.items():
        print(f"Match {match}: {teams[0]} vs {teams[1]}")

    # Simulation des quarts de finale
    quarter_finals_results = {}
    for match, teams in quarterfinal_matches.items():
        team1, team2 = teams[0], teams[1]
        goals_team1, goals_team2 = simulate_match(teams_data.loc[teams_data["name"] == team1].iloc[0], teams_data.loc[teams_data["name"] == team2].iloc[0])
        quarter_finals_results[match] = ((team1, team2), (goals_team1, goals_team2))
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_buts_quart"] += goals_team1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_buts_quart"] += goals_team2
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_matches"] += 1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_matches"] += 1

    # Affichage des résultats des quarts de finale
    print("\nRésultats des quarts de finale :")
    for match, (teams, scores) in quarter_finals_results.items():
        print(f"Match {match}: {teams[0]} {scores[0]} - {scores[1]} {teams[1]}")


    # Utilisation de la fonction pour obtenir les équipes gagnantes des quarts de finale
    equipe_gagnante_45 = gagnant(quarter_finals_results, "45")[0]
    equipe_gagnante_46 = gagnant(quarter_finals_results, "46")[0]
    equipe_gagnante_47 = gagnant(quarter_finals_results, "47")[0]
    equipe_gagnante_48 = gagnant(quarter_finals_results, "48")[0]


    # Matches des quarts de finale
    demifinal_matches = {
        "49": (equipe_gagnante_45, equipe_gagnante_46),
        "50": (equipe_gagnante_47, equipe_gagnante_48),
    }

    # Afficher les matches des quarts de finale
    print("-------------------------------------------------")
    print("\nMatches des demi de finale :")
    for match, teams in demifinal_matches.items():
        print(f"Match {match}: {teams[0]} vs {teams[1]}")

    # Simulation des quarts de finale
    demi_finals_results = {}
    for match, teams in demifinal_matches.items():
        team1, team2 = teams[0], teams[1]
        goals_team1, goals_team2 = simulate_match(teams_data.loc[teams_data["name"] == team1].iloc[0], teams_data.loc[teams_data["name"] == team2].iloc[0])
        demi_finals_results[match] = ((team1, team2), (goals_team1, goals_team2))
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_buts_demi"] += goals_team1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_buts_demi"] += goals_team2
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_matches"] += 1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_matches"] += 1

    # Affichage des résultats des quarts de finale
    print("\nRésultats des demi de finale :")
    for match, (teams, scores) in demi_finals_results.items():
        print(f"Match {match}: {teams[0]} {scores[0]} - {scores[1]} {teams[1]}")

     # Utilisation de la fonction pour obtenir les équipes gagnantes des quarts de finale
    equipe_perdante_49 = perdant(demi_finals_results, "49")[0]
    equipe_perdante_50 = perdant(demi_finals_results, "50")[0]

    # Matches des quarts de finale
    classement_matches = {
        "51": (equipe_perdante_49, equipe_perdante_50),
    }

    # Afficher les matches des quarts de finale
    print("-------------------------------------------------")
    print("\nMatche de classement (3eme Place) :")
    for match, teams in classement_matches.items():
        print(f"Match {match}: {teams[0]} vs {teams[1]}")

    # Simulation des quarts de finale
    classement_results = {}
    for match, teams in classement_matches.items():
        team1, team2 = teams[0], teams[1]
        goals_team1, goals_team2 = simulate_match(teams_data.loc[teams_data["name"] == team1].iloc[0], teams_data.loc[teams_data["name"] == team2].iloc[0])
        classement_results[match] = ((team1, team2), (goals_team1, goals_team2))
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_buts_classement"] += goals_team1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_buts_classement"] += goals_team2
        equipes_stats.loc[equipes_stats["equipe"] == team1, "nombre_matches"] += 1
        equipes_stats.loc[equipes_stats["equipe"] == team2, "nombre_matches"] += 1
        
    equipe_gagnante_classement = gagnant(classement_results, "51")
    equipes_stats.loc[equipes_stats["equipe"] == equipe_gagnante_classement[0], "3eme Place"] += 1


    # Affichage des résultats des quarts de finale
    print("\nRésultat de matche de classemrent :")
    for match, (teams, scores) in classement_results.items():
        print(f"Match {match}: {teams[0]} {scores[0]} - {scores[1]} {teams[1]}")

    # Utilisation de la fonction pour obtenir les équipes gagnantes des quarts de finale
    equipe_gagnante_49 = gagnant(demi_finals_results, "49")[0]
    equipe_gagnante_50 = gagnant(demi_finals_results, "50")[0]

    # Matches des quarts de finale
    final_matches = {
        "52": (equipe_gagnante_49, equipe_gagnante_50),
    }

    # Afficher les matches des quarts de finale
    print("-------------------------------------------------")
    print("\nMatche de finale :")
    for match, teams in final_matches.items():
        print(f"Match {match}: {teams[0]} vs {teams[1]}")

    # Simulation des quarts de finale
    final_results = {}
    for match, teams in final_matches.items():
        team1, team2 = teams[0], teams[1]
        goals_team1, goals_team2 = simulate_match(teams_data.loc[teams_data["name"] == team1].iloc[0], teams_data.loc[teams_data["name"] == team2].iloc[0])
        final_results[match] = ((team1, team2), (goals_team1, goals_team2))

    # Affichage des résultats des quarts de finale
    print("\nRésultat de la finale :")
    for match, (teams, scores) in final_results.items():
        print(f"Match {match}: {teams[0]} {scores[0]} - {scores[1]} {teams[1]}")

    # À la fin de chaque simulation, mettez à jour les statistiques des équipes
    equipe_gagnante = gagnant(final_results, "52")
    equipe_finaliste = perdant(final_results, "52")

    # Incrémentation des colonnes "gagnat" et "finaliste" pour l'équipe gagnante
    equipes_stats.loc[equipes_stats["equipe"] == equipe_gagnante[0], "1er Place"] += 1

    equipes_stats.loc[equipes_stats["equipe"] == equipe_gagnante[0], "nombre_matches"] += 1
    equipes_stats.loc[equipes_stats["equipe"] == equipe_finaliste[0], "nombre_matches"] += 1

    # Incrémentation de la colonne "finaliste" pour l'équipe finaliste
    equipes_stats.loc[equipes_stats["equipe"] == equipe_finaliste[0], "2eme Place"] += 1

    # Incrémentation de la colonne "nombre_buts" pour toutes les équipes
    equipes_stats.loc[equipes_stats["equipe"] == equipe_gagnante[0], "nombre_buts_finale"] += equipe_gagnante[1]
    equipes_stats.loc[equipes_stats["equipe"] == equipe_finaliste[0], "nombre_buts_finale"] += equipe_finaliste[1]

equipes_stats["nombre_buts"] = equipes_stats["nombre_buts_groupe"] + equipes_stats["nombre_buts_8eme"] + equipes_stats["nombre_buts_quart"] + equipes_stats["nombre_buts_demi"] + equipes_stats["nombre_buts_classement"] + equipes_stats["nombre_buts_finale"]
equipes_stats["moyenne_buts"] = (equipes_stats["nombre_buts"] / equipes_stats["nombre_matches"]).fillna(0)

# Calcul du pourcentage de gain
equipes_stats["pourcentage_gain"] = (equipes_stats["1er Place"] / nombre_simulations) * 100

equipes_stats = equipes_stats.sort_values(by="pourcentage_gain", ascending=False)

# Affichage des statistiques finales
print("\n*********************************************************************************************\n")
print("\nStatistiques finales :\n")
print(equipes_stats[["equipe", "1er Place", "2eme Place", "3eme Place", "nombre_buts", "nombre_matches", "moyenne_buts", "pourcentage_gain"]])


def create_tournament_gui(draw_results, knockout_results, quarter_finals_results, demi_finals_results, final_results):
    root = tk.Tk()
    root.title("Résultats du Tournoi")
    root.state('zoomed') 

    tab_control = ttk.Notebook(root)

    group_tab = ttk.Frame(tab_control)
    tab_control.add(group_tab, text="Groupes")
    create_group_tab(group_tab, draw_results)

    knockout_tab = ttk.Frame(tab_control)
    tab_control.add(knockout_tab, text="Huitièmes de finale")
    create_knockout_tab(knockout_tab, knockout_results)

    quarterfinals_tab = ttk.Frame(tab_control)
    tab_control.add(quarterfinals_tab, text="Quarts de finale")
    create_knockout_tab(quarterfinals_tab, quarter_finals_results)

    semifinals_tab = ttk.Frame(tab_control)
    tab_control.add(semifinals_tab, text="Demi-finales")
    create_knockout_tab(semifinals_tab, demi_finals_results)

    classement_tab = ttk.Frame(tab_control)
    tab_control.add(classement_tab, text="3eme Place")
    create_knockout_tab(classement_tab, classement_results)

    final_tab = ttk.Frame(tab_control)
    tab_control.add(final_tab, text="Finale")
    create_knockout_tab(final_tab, final_results)

    tab_control.pack(expand=1, fill="both")

    def close_window():
        root.destroy()

    close_button = ttk.Button(root, text="Fermer", command=close_window)
    close_button.pack(pady=10)

    root.mainloop()

def create_group_tab(group_tab, draw_results):
    for group_name, group_teams in draw_results.items():
        group_frame = ttk.Frame(group_tab)
        group_frame.pack(side="left", padx=10, pady=10)

        label_group = ttk.Label(group_frame, text=f"Groupe {group_name}", font=('Helvetica', 16, 'bold'))
        label_group.grid(row=0, column=0, pady=10, columnspan=2)

        for i, team in enumerate(group_teams, start=1):
            ttk.Label(group_frame, text=f"{i}. {team}", font=('Helvetica', 12)).grid(row=i, column=0, sticky="w", padx=5, pady=2)


def create_knockout_tab(tab, results):
    for i, (match, (teams, scores)) in enumerate(results.items(), start=1):
        ttk.Label(tab, text=f"Match {match}: {teams[0]} vs {teams[1]} ({scores[0]} - {scores[1]})", font=('Helvetica', 12)).pack(pady=5)



if nombre_simulations == 1:
    create_tournament_gui(draw_results, knockout_results, quarter_finals_results, demi_finals_results, final_results)
