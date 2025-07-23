import pandas as pd
from WindPy import w

w.start()

def load_data():
    # 读取基金代码数据
    fof_data = pd.read_excel('./data/基金代码.xlsx').fillna(0)
    fund_code = fof_data['证券代码'].to_list()
    
    # 从Wind中获取基金公司和业绩数据
    fund_return = w.wss(fund_code, "return_1y, return_2y, return_3y", "annualized=0;tradeDate=20240630").Data
    fund_mgrcomp = w.wss(fund_code, "fund_mgrcomp, fund_setupdate, sec_name").Data
    
    return_df = pd.DataFrame({
        '基金代码': fund_code, 
        '基金简称': fund_mgrcomp[2],
        '成立日期': fund_mgrcomp[1], 
        '基金公司': fund_mgrcomp[0],
        '近一年回报': fund_return[0], 
        '近两年回报': fund_return[1], 
        '近三年回报': fund_return[2]
    })
    return_df = return_df.drop(index=0)
    # 获取规模数据
    scale_data = get_scale_data(fund_code, fund_mgrcomp)
    fund_scale_df = pd.DataFrame(scale_data)
    
    return return_df, fund_scale_df

def get_scale_data(fund_code, fund_mgrcomp):
    # 获取季度时间段
    quarters = pd.date_range('2021-09-30', '2024-06-30', freq='3M').to_list()
    scale_data = {
        '基金代码': fund_code,
        '基金简称': fund_mgrcomp[2],
        '基金公司': fund_mgrcomp[0],
        '成立日期': fund_mgrcomp[1]
    }
    for date in quarters:
        wind_data = w.wss(fund_code, "netasset_total", f"unit=1;tradeDate={date.strftime('%Y-%m-%d')}").Data[0]
        wind_data = [round(x / 1e8, 2) if isinstance(x, (int, float)) else x for x in wind_data]
        scale_data[date.strftime('%Y%m%d')] = wind_data
    return scale_data