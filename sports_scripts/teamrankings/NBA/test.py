import pandas as pd

url = 'https://www.teamrankings.com/nba/team/minnesota-timberwolves/ats-trends'

df = pd.read_html(url)[0]
print(df)