import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower
from sqlalchemy import create_engine
from urllib.parse import quote_plus

def run_ab_test():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        r"SERVER=BLINDXDHAKAD\SQLEXPRESS;"
        "DATABASE=ShopPulse;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    engine = create_engine(
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(connection_string)
    )
    
    # Query to get checkout and purchase events by test group
    query = """
    WITH user_funnel AS (
        SELECT 
            w.customer_id,
            a.test_group,
            MAX(CASE WHEN w.event_type = 'checkout' THEN 1 ELSE 0 END) AS reached_checkout,
            MAX(CASE WHEN w.event_type = 'purchase' THEN 1 ELSE 0 END) AS reached_purchase
        FROM website_events w
        JOIN ab_test_assignments a ON w.customer_id = a.customer_id
        GROUP BY w.customer_id, a.test_group
    )
    SELECT 
        test_group,
        SUM(reached_checkout) AS checkout_users,
        SUM(reached_purchase) AS purchase_users
    FROM user_funnel
    WHERE reached_checkout = 1
    GROUP BY test_group;
    """
    
    df = pd.read_sql(query, engine)
    if df.empty:
        return {"error": "No data found for A/B testing."}
        
    df.set_index('test_group', inplace=True)
    
    control_success = df.loc['control', 'purchase_users']
    control_total = df.loc['control', 'checkout_users']
    
    treatment_success = df.loc['treatment', 'purchase_users']
    treatment_total = df.loc['treatment', 'checkout_users']
    
    control_rate = control_success / control_total
    treatment_rate = treatment_success / treatment_total
    
    # Hypothesis Testing (Z-test for proportions)
    count = [treatment_success, control_success]
    nobs = [treatment_total, control_total]
    stat, pval = proportions_ztest(count, nobs)
    
    # Confidence Intervals
    ci_low, ci_high = proportion_confint(treatment_success, treatment_total, alpha=0.05, method='wilson')
    ci_low_c, ci_high_c = proportion_confint(control_success, control_total, alpha=0.05, method='wilson')
    
    lift = (treatment_rate - control_rate) / control_rate
    
    # Power Analysis
    effect_size = sm.stats.proportion_effectsize(treatment_rate, control_rate)
    power = NormalIndPower().solve_power(effect_size=effect_size, nobs1=treatment_total, alpha=0.05, ratio=control_total/treatment_total)
    
    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "lift": lift,
        "p_value": pval,
        "ci_treatment": (ci_low, ci_high),
        "ci_control": (ci_low_c, ci_high_c),
        "power": power,
        "significant": pval < 0.05 and power > 0.8
    }

if __name__ == "__main__":
    results = run_ab_test()
    print("A/B Test Results:")
    for k, v in results.items():
        print(f"{k}: {v}")
