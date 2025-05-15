import os

def create_directory_structure(base_path="/Users/kamahl/BLOG_AI/"):
    # Define the main branches
    branches = [
        "sports/espn/sport/MLB/teams",
        "sports/teamrankings/MLB/teams",
        "sports/teamrankings/MLB/stats",
        "sports/teamrankings/MLB/rankings",
        "sports/teamrankings/MLB/2025_MLB_Schedule",
    ]

    # ESPN MLB Teams structure
    espn_mlb_teams = {
        "teams": {
            "(team_name)_roster": {
                "(player_name)": {
                    "(player_name)_stats.py": "",
                    "(player_name)_splits.py": "",
                    "(player_name)_news.py": "",
                    "(player_name)_gamelog.py": "",
                    "(player_name)_batvspitch.py": "",
                }
            },
            "(team_name)_stats.py": "",
            "(team_name)_splits.py": "",
            "(team_name)_depth_chart.py": "",
            "(team_name)_injuries.py": "",
            "(team_name)_transactions.py": "",
        }
    }

    # TeamRankings MLB Teams structure
    teamrankings_mlb_teams = {
        "teams": {
            "(team_name)_roster": {
                "(player_name)": {
                    "(player_name)_stats.py": "",
                    "(player_name)_splits.py": "",
                    "(player_name)_bio.py": "",
                    "(player_name)_news.py": "",
                    "(player_name)_gamelog.py": "",
                    "(player_name)_batvspitch.py": "",
                }
            },
            "(team_name)_gamelog.py": "",
            "(team_name)_stats": {
                "power_rankings.py": "",
                "projections.py": "",
            },
            "(team_name)_player_stats.py": "",
            "(team_name)_schedule.py": "",
            "(team_name)_depth_chart.py": "",
            "(team_name)_injuries.py": "",
            "(team_name)_transactions.py": "",
            "(team_name)_runline_results.py": "",
            "(team_name)_over_under_results.py": "",
            "(team_name)_win_loss_trends.py": "",
            "(team_name)_run_line_trends.py": "",
            "(team_name)_over_under_trends.py": "",
        }
    }

    # TeamRankings MLB Stats structure
    teamrankings_mlb_stats = {
        "stats": {
            "team_stats": {
                "team_batting": {
                    "runs_per_game.py": "",
                    "at_bats_per_game.py": "",
                    "hits_per_game.py": "",
                    "home_runs_per_game.py": "",
                    "singles_per_game.py": "",
                    "doubles_per_game.py": "",
                    "triples_per_game.py": "",
                    "rbis_per_game.py": "",
                    "walks_per_game.py": "",
                    "strikeouts_per_game.py": "",
                    "stolen_bases_per_game.py": "",
                    "stolen_bases_attempted_per_game.py": "",
                    "caught_stealing_per_game.py": "",
                    "sacrifice_hits_per_game.py": "",
                    "sacrifice_flys_per_game.py": "",
                    "left_on_base_per_game.py": "",
                    "team_left_on_base_per_game.py": "",
                    "hit_by_pitch_per_game.py": "",
                    "grounded_into_double_plays_per_game.py": "",
                    "runners_left_in_scoring_position_per_game.py": "",
                    "total_bases_per_game.py": "",
                    "batting_average.py": "",
                    "slugging_percentage.py": "",
                    "on_base_percentage.py": "",
                    "on_base_plus_slugging_percentage.py": "",
                },
                "team_advanced_batting": {
                    "plate_appearances.py": "",
                    "run_differential.py": "",
                    "batting_average_on_balls_in_play.py": "",
                    "isolated_power.py": "",
                    "secondary_average.py": "",
                },
                "team_batting_ratios": {
                    "at_bats_per_home_run.py": "",
                    "home_run_percentage.py": "",
                    "strikeout_percentage.py": "",
                    "walk_percentage.py": "",
                    "extra_base_hit_percentage.py": "",
                    "hits_for_extra_bases_percentage.py": "",
                    "stolen_base_percentage.py": "",
                    "hits_per_run.py": "",
                },
                "team_pitching": {
                    "outs_pitched_per_game.py": "",
                    "earned_runs_against_per_game.py": "",
                    "earned_run_average.py": "",
                    "walks_plus_hits_per_inning_pitched.py": "",
                    "strikeouts_per_9.py": "",
                    "hits_per_9.py": "",
                    "home_runs_per_9.py": "",
                    "walks_per_9.py": "",
                    "strikeouts_per_walk.py": "",
                    "shutouts.py": "",
                },
                "team_fielding": {
                    "double_plays_per_game.py": "",
                    "errors_per_game.py": "",
                },
                "opponent_batting": {
                    "opponent_runs_per_game.py": "",
                    "opponent_at_bats_per_game.py": "",
                    "opponent_hits_per_game.py": "",
                    "opponent_home_runs_per_game.py": "",
                    "opponent_singles_per_game.py": "",
                    "opponent_doubles_per_game.py": "",
                    "opponent_triples_per_game.py": "",
                    "opponent_rbis_per_game.py": "",
                    "opponent_walks_per_game.py": "",
                    "opponent_strikeouts_per_game.py": "",
                    "opponent_stolen_bases_per_game.py": "",
                    "opponent_stolen_bases_attempted.py": "",
                    "opponent_caught_stealing_per_game.py": "",
                    "opponent_sacrifice_hits_per_game.py": "",
                    "opponent_sacrifice_flys_per_game.py": "",
                    "opponent_left_on_base_per_game.py": "",
                    "opponent_team_left_on_base_per_game.py": "",
                    "opponent_hit_by_pitch_per_game.py": "",
                    "opponent_grounded_into_double_plays_per_game.py": "",
                    "opponent_runners_left_in_scoring_pos_per_game.py": "",
                    "opponent_total_bases_per_game.py": "",
                    "opponent_batting_average.py": "",
                    "opponent_slugging_percentage.py": "",
                    "opponent_on_base_percentage.py": "",
                    "opponent_on_base_plus_slugging_percentage.py": "",
                },
                "opponent_advanced_batting": {
                    "opponent_plate_appearances.py": "",
                    "opponent_run_differential.py": "",
                    "opponent_batting_average_on_balls_in_play.py": "",
                    "opponent_isolated_power.py": "",
                    "opponent_secondary_average.py": "",
                },
                "opponent_batting_ratios": {
                    "opponent_at_bats_per_home_run.py": "",
                    "opponent_home_run_percentage.py": "",
                    "opponent_strikeout_percentage.py": "",
                    "opponent_walk_percentage.py": "",
                    "opponent_extra_base_hit_percentage.py": "",
                    "opponent_hits_for_extra_bases_percentage.py": "",
                    "opponent_stolen_base_percentage.py": "",
                    "opponent_hits_per_run.py": "",
                },
                "opponent_pitching": {
                    "opponent_outs_pitched_per_game.py": "",
                    "opponent_earned_runs_against_per_game.py": "",
                    "opponent_earned_run_average.py": "",
                    "opponent_walks_plus_hits_per_innings_pitched.py": "",
                    "opponent_strikeouts_per_9.py": "",
                    "opponent_hits_per_9.py": "",
                    "opponent_home_runs_per_9.py": "",
                    "opponent_walks_per_9.py": "",
                    "opponent_strikeouts_per_walk.py": "",
                    "opponent_shutouts.py": "",
                },
                "opponent_fielding": {
                    "opponent_double_plays_per_game.py": "",
                    "opponent_errors_per_game.py": "",
                },
                "other": {
                    "games_played.py": "",
                    "yes_run_first_inning_percentage.py": "",
                    "no_run_first_inning_percentage.py": "",
                    "opponent_yes_run_first_inning_percentage.py": "",
                    "opponent_no_run_first_inning_percentage.py": "",
                    "1st_inning_runs_per_game.py": "",
                    "2nd_inning_runs_per_game.py": "",
                    "3rd_inning_runs_per_game.py": "",
                    "4th_inning_runs_per_game.py": "",
                    "5th_inning_runs_per_game.py": "",
                    "6th_inning_runs_per_game.py": "",
                    "7th_inning_runs_per_game.py": "",
                    "8th_inning_runs_per_game.py": "",
                    "9th_inning_runs_per_game.py": "",
                    "extra_inning_runs_per_game.py": "",
                    "opponent_1st_inning_runs_per_game.py": "",
                    "opponent_2nd_inning_runs_per_game.py": "",
                    "opponent_3rd_inning_runs_per_game.py": "",
                    "opponent_4th_inning_runs_per_game.py": "",
                    "opponent_5th_inning_runs_per_game.py": "",
                    "opponent_6th_inning_runs_per_game.py": "",
                    "opponent_7th_inning_runs_per_game.py": "",
                    "opponent_8th_inning_runs_per_game.py": "",
                    "opponent_9th_inning_runs_per_game.py": "",
                    "opponent_extra_inning_runs_per_game.py": "",
                    "first_4_innings_runs_per_game.py": "",
                    "first_5_innings_runs_per_game.py": "",
                    "first_6_innings_runs_per_game.py": "",
                    "last_2_innings_runs_per_game.py": "",
                    "last_3_innings_runs_per_game.py": "",
                    "last_4_innings_runs_per_game.py": "",
                    "opponent_first_4_innings_runs_per_game.py": "",
                    "opponent_first_5_innings_runs_per_game.py": "",
                    "opponent_first_6_innings_runs_per_game.py": "",
                    "opponent_last_2_innings_runs_per_game.py": "",
                    "opponent_last_3_innings_runs_per_game.py": "",
                    "opponent_last_4_innings_runs_per_game.py": "",
                    "winning_percentage.py": "",
                    "win_percentage_all_games.py": "",
                    "win_percentage_close_games.py": "",
                    "opponent_win_percentage_all_games.py": "",
                    "opponent_win_percentage_close_games.py": "",
                },
            },
            "player_stats": {
                "pitching": {
                    "strikeouts.py": "",
                    "innings_pitched.py": "",
                    "hits_allowed.py": "",
                    "runs_allowed.py": "",
                    "earned_runs_allowed.py": "",
                    "walks.py": "",
                    "games_pitched.py": "",
                    "games_started.py": "",
                    "home_runs_allowed.py": "",
                    "pitches_thrown.py": "",
                    "strikes_thrown.py": "",
                    "ground_ball_outs.py": "",
                    "fly_ball_outs.py": "",
                    "batters_faced.py": "",
                    "earned_run_average.py": "",
                    "walks_plus_hits_per_inning_pitched.py": "",
                },
                "pitching_results": {
                    "quality_starts.py": "",
                    "wins.py": "",
                    "losses.py": "",
                    "no_decisions.py": "",
                    "holds.py": "",
                    "saves.py": "",
                    "blown_saves.py": "",
                    "save_percentage.py": "",
                    "complete_games.py": "",
                    "shutouts.py": "",
                    "win_percentage.py": "",
                    "percent_of_starts_won.py": "",
                    "cheap_wins.py": "",
                    "tough_losses.py": "",
                    "quality_start_percentage.py": "",
                },
                "advanced_pitching": {
                    "strikeouts_per_9.py": "",
                    "hits_allowed_per_9.py": "",
                    "home_runs_allowed_per_9.py": "",
                    "walks_per_9.py": "",
                    "strikeouts_per_walk.py": "",
                    "pitches_per_plate_appearance.py": "",
                    "pitches_per_game.py": "",
                    "fielding_independent_pitching.py": "",
                },
                "pitching_ratios": {
                    "strike_percentage.py": "",
                    "home_run_percentage.py": "",
                    "strikeout_percentage.py": "",
                    "walk_percentage.py": "",
                    "ground_outs_to_air_outs.py": "",
                },
                "batting": {
                    "games_played.py": "",
                    "games_started.py": "",
                    "at_bats.py": "",
                    "runs.py": "",
                    "hits.py": "",
                    "singles.py": "",
                    "doubles.py": "",
                    "triples.py": "",
                    "home_runs.py": "",
                    "total_bases.py": "",
                    "runs_batted_in.py": "",
                    "walks.py": "",
                    "intentional_walks.py": "",
                    "strikeouts.py": "",
                    "hit_by_pitch.py": "",
                    "stolen_bases.py": "",
                    "caught_stealing.py": "",
                    "grounded_into_double_plays.py": "",
                    "left_on_base.py": "",
                    "two_out_rbis.py": "",
                    "runners_left_in_scoring_position.py": "",
                    "batting_average.py": "",
                    "on_base_percentage.py": "",
                    "slugging_percentage.py": "",
                    "on_base_plus_slugging.py": "",
                    "fielding_errors.py": "",
                },
                "advanced_batting": {
                    "plate_appearances.py": "",
                    "outs_made.py": "",
                    "batting_average_on_balls_in_play.py": "",
                    "isolated_power.py": "",
                    "secondary_average.py": "",
                    "at_bats_per_home_run.py": "",
                },
                "batting_ratios": {
                    "home_run_percentage.py": "",
                    "strikeout_percentage.py": "",
                    "base_on_balls_percentage.py": "",
                    "extra_base_hit_percentage.py": "",
                    "hits_for_extra_bases_percentage.py": "",
                    "stolen_base_percentage.py": "",
                },
                "batting_events": {
                    "games_with_a_hit.py": "",
                    "percent_of_games_with_a_hit.py": "",
                    "percent_of_starts_with_a_hit.py": "",
                    "games_with_a_home_run.py": "",
                    "percent_of_games_with_a_home_run.py": "",
                    "percent_of_starts_with_a_home_run.py": "",
                    "games_with_a_run.py": "",
                    "percent_of_games_with_a_run.py": "",
                    "percent_of_starts_with_a_run.py": "",
                    "games_with_a_run_batted_in.py": "",
                    "percent_of_games_with_a_run_batted_in.py": "",
                    "percent_of_starts_with_a_run_batted_in.py": "",
                    "games_with_2_plus_total_bases.py": "",
                    "percent_of_games_with_2_plus_total_bases.py": "",
                    "percent_of_starts_with_2_plus_total_bases.py": "",
                    "games_with_a_stolen_base.py": "",
                    "percent_of_games_with_a_stolen_base.py": "",
                    "percent_of_starts_with_a_stolen_base.py": "",
                },
            },
        },
        "rankings": {
            "predictive_power_rating.py": "",
            "home_power_rating.py": "",
            "away_power_rating.py": "",
            "home_advantage_power_rating.py": "",
            "strength_of_schedule_power_rating.py": "",
            "future_sos_power_rating.py": "",
            "season_sos_power_rating.py": "",
            "sos_power_rating_basic_method.py": "",
            "in_division_sos_power_rating.py": "",
            "non_division_sos_power_rating.py": "",
            "last_5_games_power_rating.py": "",
            "last_10_games_power_rating.py": "",
            "in_division_power_rating.py": "",
            "non_division_power_rating.py": "",
            "luck_power_rating.py": "",
            "consistency_power_rating.py": "",
            "vs_teams_1_5_power_rating.py": "",
            "vs_teams_6_10_power_rating.py": "",
            "vs_teams_11_16_power_rating.py": "",
            "vs_teams_17_22_power_rating.py": "",
            "vs_teams_23_30_power_rating.py": "",
        },
        "2025_MLB_Schedule": {
            "mlb_schedule.py": "",
        },
        "projections_and_standings": {
            "current_standings.py": "",
            "projected_standings.py": "",
            "postseason_seeds.py": "",
        },
        "team_trends": {
            "win_loss.py": "",
            "run_line.py": "",
            "over_under.py": "",
        },
        "betting_odds.py": "",
    }

    # MLB.com placeholder (to be updated later)
    mlb_com = {
        "MLB.com": {},
    }

    # Combine all structures
    full_structure = {}
    for branch in branches:
        if "espn" in branch:
            full_structure[branch] = espn_mlb_teams
        elif "teamrankings" in branch:
            if "stats" in branch:
                full_structure[branch] = {"stats": teamrankings_mlb_stats["stats"]}
            elif "rankings" in branch:
                full_structure[branch] = {"rankings": teamrankings_mlb_stats["rankings"]}
            elif "2025_MLB_Schedule" in branch:
                full_structure[branch] = {"2025_MLB_Schedule": teamrankings_mlb_stats["2025_MLB_Schedule"]}
            else:
                full_structure[branch] = teamrankings_mlb_teams
        elif "MLB.com" in branch:
            full_structure[branch] = mlb_com

    # Create directories and files
    for branch, structure in full_structure.items():
        current_path = os.path.join(base_path, branch)
        create_nested_structure(current_path, structure)

def create_nested_structure(path, structure):
    """Recursively create directories and empty .py files based on the structure."""
    for key, value in structure.items():
        new_path = os.path.join(path, key.replace(" ", "_"))
        if isinstance(value, dict):
            os.makedirs(new_path, exist_ok=True)
            create_nested_structure(new_path, value)
        elif value == "":
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            with open(new_path, "w") as f:
                pass  # Create empty .py file

if __name__ == "__main__":
    create_directory_structure()