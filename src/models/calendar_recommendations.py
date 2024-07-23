from src.pipeline.data_processor import DataProcessor, CleanedData
from enum import Enum
from datetime import date, timedelta
import pandas as pd
import re


dp = DataProcessor()
calendar = dp.load_table(CleanedData.CALENDAR)

class LearningCycle(Enum):
    DAF = ["Daf Yomi", "category_Gemara", "d_masechta", "d_num"]
    WEEKLY_DAF = ["Daf Hashvua", "category_Gemara", "dw_masechta", "dw_num"]
    MISHNAH = ["Mishna Yomi LZN Daniel Ari ben Avraham Kadesh", "category_Mishna", "m_masechta", "m_num1", "m_num2"]
    PARSHA = ["category_Parsha", "parashat"]
    NACH = ["Nach Yomi", "category_Nach", "n_sefer", "n_num"]
    YERUSHALMI = ["Yerushalmi Yomi", "category_Yerushalmi", "y_masechta", "y_num"]


class CycleRecommendations():
     def __init__(self):
          self.dp = DataProcessor()
          self.calendar = dp.load_table(CleanedData.CALENDAR)

     def get_learning_cycle_recommendations(self, cycle:LearningCycle, date:date=date.today()):
          if str(date) not in calendar['date'].values:
               return []
          date_data = calendar[calendar['date'] == str(date)]
          if cycle in [LearningCycle.DAF, LearningCycle.WEEKLY_DAF, LearningCycle.NACH, LearningCycle.YERUSHALMI]:
               df = self.get_standard_learning(cycle, date_data)
          elif cycle == LearningCycle.PARSHA:
               df = self.get_parsha_recommendations(cycle, date_data)
          elif cycle == LearningCycle.MISHNAH:
               df = self.get_mishna_recommendation(cycle, date_data)
          else:
               return []
          return(df["shiur"].tolist())

     def get_standard_learning(self, cycle:LearningCycle, row:pd.DataFrame):
          subcategory = row.iloc[0][cycle.value[2]]
          subcategory = f'[{subcategory}]' if ' ' in subcategory else subcategory
          df_categories = dp.load_table(CleanedData.CATEGORIES)
          df_shiurim = dp.load_table(CleanedData.SHIURIM)
          df_merged = pd.merge(df_categories, df_shiurim, on='shiur', suffixes=('_cat', '_shiur'))
          df = df_merged.loc[
          (df_merged[cycle.value[1]] == 1) & 
          (df_merged[row.iloc[0][cycle.value[2]]] == 1) &
          (df_merged['series_name'] == cycle.value[0])
          ].copy()
          df.loc[:, 'numbers'] = df['title'].apply(self.__extract_numbers)
          cycle_value1 = int(row[cycle.value[3]].item() if hasattr(row[cycle.value[3]], 'item') else row[cycle.value[3]])
          filtered_df = df[df['numbers'].apply(lambda x: x[0] == cycle_value1 if len(x) > 0 else False)]
          filtered_df = filtered_df.drop(columns=['numbers'])
          return filtered_df

     def get_parsha_recommendations(self, cycle:LearningCycle, row:pd.DataFrame):
          subcategory = row.iloc[0][cycle.value[1]]
          subcategory = f'[{subcategory}]' if ' ' in subcategory else subcategory
          df_categories = dp.load_table(CleanedData.CATEGORIES)
          df_shiurim = dp.load_table(CleanedData.SHIURIM)
          df_merged = pd.merge(df_categories, df_shiurim, on='shiur', suffixes=('_cat', '_shiur'))
          filtered_df = df_merged[
          (df_merged[cycle.value[0]] == 1) & 
          (df_merged[subcategory] == 1)
          ]
          return filtered_df

     def get_mishna_recommendation(self, cycle:LearningCycle, row:pd.DataFrame):
          subcategory = row.iloc[0][cycle.value[2]]
          subcategory = f'[{subcategory}]' if ' ' in subcategory else subcategory
          df_categories = dp.load_table(CleanedData.CATEGORIES)
          df_shiurim = dp.load_table(CleanedData.SHIURIM)
          df_merged = pd.merge(df_categories, df_shiurim, on='shiur', suffixes=('_cat', '_shiur'))
          df = df_merged.loc[
          (df_merged[cycle.value[1]] == 1) & 
          (df_merged[row.iloc[0][cycle.value[2]]] == 1) &
          (df_merged['series_name'] == cycle.value[0])
          ].copy()
          df.loc[:, 'numbers'] = df['title'].apply(self.__extract_numbers)
          print(df[['title', 'numbers']])
          cycle_value1 = int(row[cycle.value[3]].item() if hasattr(row[cycle.value[3]], 'item') else row[cycle.value[3]])
          cycle_value2 = int(row[cycle.value[4]].item() if hasattr(row[cycle.value[4]], 'item') else row[cycle.value[4]])
          filtered_df = df[df['numbers'].apply(lambda x: (x[0] == cycle_value1 and x[1] == cycle_value2) if len(x) > 1 else False)]
          filtered_df = filtered_df.drop(columns=['numbers'])
          return filtered_df

     def __extract_numbers(title):
          return [int(num) for num in re.findall(r'\b\d+\b|(?<=[:\-])\d+', title)]

     def get_holiday(self, start_date:date=date.today(), end_date:date=date.today()+timedelta(3)):
          if str(start_date) not in calendar['date'].values:
               return []
          holiday_data = calendar[(calendar['date'] >= str(start_date)) & (calendar['date'] <= str(end_date))]
          no_holiday = holiday_data['holiday'].isna().all()
          no_roshchodesh = holiday_data['roshchodesh'].isna().all()
          if no_holiday == False:
               first_holiday = holiday_data['holiday'].dropna().iloc[0]
               df_categories = dp.load_table(CleanedData.CATEGORIES)
               df_shiurim = dp.load_table(CleanedData.SHIURIM)
               df_merged = pd.merge(df_categories, df_shiurim, on='shiur', suffixes=('_cat', '_shiur'))
               filtered_df = df_merged[(df_merged[first_holiday] == 1)]
               return(filtered_df["shiur"].tolist())
          elif no_roshchodesh == False:
               first_roshchodesh = holiday_data['holiday'].dropna().iloc[0]
               df_categories = dp.load_table(CleanedData.CATEGORIES)
               df_shiurim = dp.load_table(CleanedData.SHIURIM)
               df_merged = pd.merge(df_categories, df_shiurim, on='shiur', suffixes=('_cat', '_shiur'))
               filtered_df = df_merged[(df_merged[first_roshchodesh] == 1)]
               return(filtered_df["shiur"].tolist())
          else:
               return []
