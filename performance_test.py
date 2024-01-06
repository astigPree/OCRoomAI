import pstats

stats = pstats.Stats('oc ai.profile')
stats.sort_stats('time').print_stats()

