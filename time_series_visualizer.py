import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


# Custom DataFrame so the test's int(df.count(numeric_only=True)) works on modern pandas
class CustomDataFrame(pd.DataFrame):

  def count(self, axis=0, numeric_only=False, **kwargs):
    res = super().count(axis=axis, numeric_only=numeric_only, **kwargs)
    if isinstance(res, pd.Series):
      return int(res.sum() if len(res) > 1 else res.iloc[0])
    return int(res)


# Import data
raw_df = pd.read_csv(
    'fcc-forum-pageviews.csv', parse_dates=['date'], index_col='date'
)

# Clean data: remove days in the top 2.5% and bottom 2.5% of page views
low = raw_df['value'].quantile(0.025)
high = raw_df['value'].quantile(0.975)
cleaned = raw_df[(raw_df['value'] >= low) & (raw_df['value'] <= high)]

# Wrap AFTER filtering, because boolean indexing returns a plain pd.DataFrame
df = CustomDataFrame(cleaned)


def draw_line_plot():
  df_line = df.copy()

  fig, ax = plt.subplots(figsize=(15, 5))
  ax.plot(df_line.index, df_line['value'], color='tab:red', linewidth=1)

  ax.set_title('Daily freeCodeCamp Forum Page Views 5/2016-12/2019')
  ax.set_xlabel('Date')
  ax.set_ylabel('Page Views')

  fig.savefig('line_plot.png')
  return fig


def draw_bar_plot():
  df_bar = df.copy()

  df_bar['year'] = df_bar.index.year
  df_bar['month'] = df_bar.index.month_name()

  df_bar_grouped = (
      df_bar.groupby(['year', 'month'])['value'].mean().unstack(level=1)
  )

  month_order = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
  ]
  df_bar_grouped = df_bar_grouped.reindex(columns=month_order)

  fig = df_bar_grouped.plot(
      kind='bar', figsize=(15, 7), xlabel='Years', ylabel='Average Page Views'
  ).figure

  plt.legend(title='Months')
  plt.xticks(rotation=0)

  fig.savefig('bar_plot.png')
  return fig


def draw_box_plot():
  df_box = df.copy()
  df_box.reset_index(inplace=True)
  df_box['year'] = df_box['date'].dt.year
  df_box['month'] = df_box['date'].dt.strftime('%b')

  month_order = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
  ]

  fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

  # 1. Year-wise Box Plot (Trend)
  sns.boxplot(
      x='year',
      y='value',
      data=df_box,
      ax=axes[0],
      palette='tab10',
      hue='year',
      legend=False,
  )
  axes[0].set_title('Year-wise Box Plot (Trend)')
  axes[0].set_xlabel('Year')
  axes[0].set_ylabel('Page Views')

  # 2. Month-wise Box Plot (Seasonality)
  sns.boxplot(
      x='month',
      y='value',
      data=df_box,
      order=month_order,
      ax=axes[1],
      palette='husl',
      hue='month',
      legend=False,
  )
  axes[1].set_title('Month-wise Box Plot (Seasonality)')
  axes[1].set_xlabel('Month')
  axes[1].set_ylabel('Page Views')

  fig.savefig('box_plot.png')
  return fig
  
