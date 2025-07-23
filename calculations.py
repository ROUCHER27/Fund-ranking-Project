import pandas as pd
import numpy as np

def calculate_weighted_returns(fund_scale_df):
    # 加权回报计算
    fund_performance = calculate_performance(fund_scale_df)
    # 基金管理公司排名
    mgrcomp_rank = rank_funds(fund_performance)
    # 准备输出数据
    result_df, contrast_df, df3 = prepare_output_data(mgrcomp_rank, fund_scale_df, fund_performance)
    return mgrcomp_rank, result_df, contrast_df, df3

def calculate_performance(fund_scale_df):
    fund_performance = fund_scale_df.merge(return_df, on='基金代码')

    # 计算加权回报
    fund_performance['近三年加权回报'] = fund_performance['近三年规模权重'] * fund_performance['近三年回报']
    fund_performance['近两年加权回报'] = fund_performance['近两年规模权重'] * fund_performance['近两年回报']
    fund_performance['近一年加权回报'] = fund_performance['近一年规模权重'] * fund_performance['近一年回报']
    fund_performance.drop(['近三年规模权重', '近两年规模权重', '基金简称_y', '成立日期_y', '近一年规模权重', '近三年回报', '近两年回报', '近一年回报'] ,axis=1, inplace=True)
    fund_performance.drop(['近三年总规模','近两年总规模','近一年总规模','基金公司_y','近三年平均规模','近两年平均规模','近一年平均规模','20210930','20211231','20220331','20220630','20220930','20221231','20230331','20230630','20230930','20231231','20240331','20240630'],axis=1,inplace=True)
    fund_performance.reset_index()
    
    return fund_performance

def rank_funds(fund_performance):
    # 初始化管理公司排名 DataFrame
    mgrcomp_list = grouped['基金公司'].tolist()
    mgrcomp_rank = pd.DataFrame()

    # 定义 NaN 处理函数
    def sum_for_nan(series):
        if series.count() == 0:
            return np.nan
        else:
            return series.sum()

    # 计算每个管理公司的总回报
    for mgrcomp in mgrcomp_list:
        sum_3y = sum_for_nan(fund_performance['近三年加权回报'][fund_performance['基金公司'] == mgrcomp])
        sum_2y = sum_for_nan(fund_performance['近两年加权回报'][fund_performance['基金公司'] == mgrcomp])
        sum_1y = sum_for_nan(fund_performance['近一年加权回报'][fund_performance['基金公司'] == mgrcomp])
        new_row = pd.DataFrame([{
            '基金公司': mgrcomp,
            '近三年收益率': sum_3y,
            '近两年收益率': sum_2y,
            '近一年收益率': sum_1y
        }])
        mgrcomp_rank = pd.concat([mgrcomp_rank, new_row], ignore_index=True)

    # 对回报进行排名
    mgrcomp_rank['近三年排名'] = mgrcomp_rank['近三年收益率'].rank(method='min', ascending=False)
    mgrcomp_rank['近两年排名'] = mgrcomp_rank['近两年收益率'].rank(method='min', ascending=False)
    mgrcomp_rank['近一年排名'] = mgrcomp_rank['近一年收益率'].rank(method='min', ascending=False)
    mgrcomp_rank.insert(2,'近三年排名',mgrcomp_rank.pop('近三年排名'))
    mgrcomp_rank.insert(4,'近两年排名',mgrcomp_rank.pop('近两年排名'))

    return mgrcomp_rank

def calculate_comprehensive_scores(mgrcomp_rank, fund_scale_df):
    """
    计算综合得分和排名。
    
    参数:
    mgrcomp_rank: 基金管理公司排名的DataFrame
    fund_scale_df: 包含基金规模信息的DataFrame
    
    返回:
    result_df: 综合得分结果的DataFrame
    """
    df2 = fund_performance.groupby('基金公司').agg(
        近三年总和=('近三年加权回报', 'sum'),
        近两年总和=('近两年加权回报', 'sum'),
        近一年总和=('近一年加权回报', 'sum')
    )
    df2 = df2.rename(columns={'近三年总和': '近三年收益率', '近两年总和': '近两年收益率', '近一年总和': '近一年收益率'})
    
    df2_filtered = fund_scale_df[['基金公司', '近三年总规模', '近两年总规模', '近一年总规模']].drop_duplicates(subset='基金公司')
    result_df = pd.merge(df2, df2_filtered, on='基金公司', how='left')

    # 计算百分位
    result_df['收益率百分位3'] = result_df['近三年收益率'].rank(pct=True)
    result_df['收益率百分位2'] = result_df['近两年收益率'].rank(pct=True)
    result_df['收益率百分位1'] = result_df['近一年收益率'].rank(pct=True)
    result_df['规模百分位3'] = result_df['近三年总规模'].rank(pct=True)
    result_df['规模百分位2'] = result_df['近两年总规模'].rank(pct=True)
    result_df['规模百分位1'] = result_df['近一年总规模'].rank(pct=True)

    # 计算得分和排名
    result_df['得分3'] = (result_df['收益率百分位3'] + result_df['规模百分位3']) / 2
    result_df['得分2'] = (result_df['收益率百分位2'] + result_df['规模百分位2']) / 2
    result_df['得分1'] = (result_df['收益率百分位1'] + result_df['规模百分位1']) / 2
    result_df['排名3'] = result_df['得分3'].rank(ascending=False, method='min')
    result_df['排名2'] = result_df['得分2'].rank(ascending=False, method='min')
    result_df['排名1'] = result_df['得分1'].rank(ascending=False, method='min')

    # 删除多余的列
    columns_to_drop = ['收益率百分位3','收益率百分位2','收益率百分位1','规模百分位3','规模百分位2','规模百分位1']
    result_df = result_df.drop(columns=columns_to_drop)

    # 计算总行数和阈值
    threshold_E = result_df['排名3'].max() * 0.7
    threshold_I = result_df['排名2'].max() * 0.7
    threshold_M = result_df['排名1'].max() * 0.7
    
    result_df['得分是否在后30%'] = result_df.apply(lambda row: calculate_score(row, threshold_E, threshold_I, threshold_M), axis=1)
    result_df = result_df.sort_values(by='排名1', ascending=True).reset_index(drop=True)

    return result_df


def prepare_output_data(mgrcomp_rank, fund_scale_df, fund_performance):
    """
    准备最终输出的数据，包括综合得分和对比数据。
    
    参数:
    mgrcomp_rank: 基金管理公司排名的DataFrame
    fund_scale_df: 包含基金规模信息的DataFrame
    fund_performance: 包含基金加权回报的DataFrame
    
    返回:
    result_df: 综合得分结果的DataFrame
    contrast_df: 低分名单的DataFrame
    df3: 其他对比数据的DataFrame
    """
    # 综合得分计算
    result_df = calculate_comprehensive_scores(mgrcomp_rank, fund_scale_df)
    
    # 提取业绩和得分都在后30%的基金公司
    filtered_df1 = mgrcomp_rank[mgrcomp_rank['业绩排名是否在后30%'] == '是']
    filtered_df2 = result_df[result_df['得分是否在后30%'] == '是']

    companies_df1 = filtered_df1['基金公司']
    companies_df2 = filtered_df2['基金公司']
    contrast_df = pd.DataFrame({
        '业绩排名都在后30%的基金公司': companies_df1.reset_index(drop=True),
        '综合得分都在后30%的基金公司': companies_df2.reset_index(drop=True)
    })

    # 读取其他对比数据
    df3 = pd.read_excel('./data/基金公司.xlsx', sheet_name='Sheet1')
    df3 = compare_companies_with_scores(df3, contrast_df, result_df)
    
    return result_df, contrast_df, df3
