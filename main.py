from data_import import load_data
from data_processing import clean_and_prepare_data
from calculations import calculate_weighted_returns, rank_funds
from output import generate_excel_output

def main():
    # 数据导入
    return_df, fund_scale_df = load_data()
    
    # 数据处理
    return_df, fund_scale_df, fund_performance = clean_and_prepare_data(return_df, fund_scale_df)
    
    # 计算
    mgrcomp_rank, result_df, contrast_df, df3 = calculate_weighted_returns(fund_performance)
    
    # 输出
    generate_excel_output(return_df, fund_scale_df, fund_performance, mgrcomp_rank, result_df, contrast_df, df3)

if __name__ == "__main__":
    main()