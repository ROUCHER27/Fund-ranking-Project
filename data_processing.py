import pandas as pd
import numpy as np

def clean_and_prepare_data(return_df, fund_scale_df):
    # 计算平均规模
    fund_scale_df['近三年平均规模'] = fund_scale_df.iloc[:, 2:14].mean(axis=1)
    fund_scale_df['近两年平均规模'] = fund_scale_df.iloc[:, 6:14].mean(axis=1)
    fund_scale_df['近一年平均规模'] = fund_scale_df.iloc[:, 10:14].mean(axis=1)
    
    # 处理NaN值
    fund_scale_df = handle_nan_values(fund_scale_df)
    fund_scale_df.insert(4, '近三年平均规模', fund_scale_df.pop('近三年平均规模'))
    fund_scale_df.insert(5, '近两年平均规模', fund_scale_df.pop('近两年平均规模'))
    fund_scale_df.insert(6, '近一年平均规模', fund_scale_df.pop('近一年平均规模'))
    
    # 计算总规模
    grouped = fund_scale_df.groupby('基金公司').agg({
        '近三年平均规模': 'sum',
        '近两年平均规模': 'sum',
        '近一年平均规模': 'sum'
    }).reset_index()
    grouped.columns = ['基金公司', '近三年总规模', '近两年总规模', '近一年总规模']
    
    # 合并总规模到原DataFrame
    fund_scale_df = fund_scale_df.merge(grouped, on='基金公司')

    # 计算规模权重
    fund_scale_df['近三年规模权重'] = fund_scale_df['近三年平均规模'] / fund_scale_df['近三年总规模']
    fund_scale_df['近两年规模权重'] = fund_scale_df['近两年平均规模'] / fund_scale_df['近两年总规模']
    fund_scale_df['近一年规模权重'] = fund_scale_df['近一年平均规模'] / fund_scale_df['近一年总规模']

    # 调整列的顺序
    fund_scale_df.insert(7, '近三年总规模', fund_scale_df.pop('近三年总规模'))
    fund_scale_df.insert(8, '近两年总规模', fund_scale_df.pop('近两年总规模'))
    fund_scale_df.insert(9, '近一年总规模', fund_scale_df.pop('近一年总规模'))
    fund_scale_df.insert(4, '近三年规模权重', fund_scale_df.pop('近三年规模权重'))
    fund_scale_df.insert(5, '近两年规模权重', fund_scale_df.pop('近两年规模权重'))
    fund_scale_df.insert(6, '近一年规模权重', fund_scale_df.pop('近一年规模权重'))
    fund_scale_df.insert(2,'成立日期',fund_scale_df.pop('成立日期'))
    return return_df, fund_scale_df, calculate_weighted_returns(fund_scale_df)

def handle_nan_values(fund_scale_df):
    # 处理 NaN 值的逻辑
    index_1 = fund_scale_df.loc[fund_scale_df.iloc[:, 2:14].isnull().any(axis=1)].index
    index_2 = fund_scale_df.loc[fund_scale_df.iloc[:, 6:14].isnull().any(axis=1)].index
    index_3 = fund_scale_df.loc[fund_scale_df.iloc[:, 10:14].isnull().any(axis=1)].index
    fund_scale_df['近三年平均规模'][index_1] = np.nan
    fund_scale_df['近两年平均规模'][index_2] = np.nan
    fund_scale_df['近一年平均规模'][index_3] = np.nan
    return fund_scale_df

