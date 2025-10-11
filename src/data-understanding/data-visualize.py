from ydata_profiling import ProfileReport
import pandas as pd

# Adjust the path as needed
# data_path = r'C:\Users\Sandeep\Documents\Work\code\candle-pattern-test\data\nifty\full-set\featured.csv'
data_path = r'C:\Users\Sandeep\Documents\Work\code\candle-pattern-test\data\nifty\samples\tradebook-ZH5601-FO.csv'

df = pd.read_csv(data_path)

profile = ProfileReport(df, title="Tradebook Understanding Report", explorative=True)
profile.to_file("tradebook_Report.html")