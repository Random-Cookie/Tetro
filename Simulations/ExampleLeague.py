from Players.AlgorithmicPlayers import StaticHeatmapPlayer
from Simulations.SimUtils import ANSI_COLORS, run_league

if __name__ == '__main__':
    sim_players = [StaticHeatmapPlayer(ANSI_COLORS[0], 'Players/heatmaps/aggressiveX.txt'),
        StaticHeatmapPlayer(ANSI_COLORS[1], 'Players/heatmaps/bullseye.txt'),
        StaticHeatmapPlayer(ANSI_COLORS[2], 'Players/heatmaps/sidewinder.txt'),
        StaticHeatmapPlayer(ANSI_COLORS[3], 'Players/heatmaps/reverse_bullseye.txt'),
        StaticHeatmapPlayer(ANSI_COLORS[4], 'Players/heatmaps/aggressive.txt')]
    run_league(sim_players)
