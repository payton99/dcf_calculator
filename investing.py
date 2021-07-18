import pandas as pd
import numpy as np
import yfinance as yf
import statistics
import investpy as ip

pd.set_option('display.float_format', lambda x: '%.2f' % x)

msft = yf.Ticker("MSFT")
# print(msft)
fin = msft.financials
# print(format(statistics.median(fin.loc['Net Income'] / fin.loc['Total Revenue']), ".2f"))
cash = msft.cashflow
# print(cash)


# Function to find a company's free cash flow over the past four years.
def get_free_cash_flow(ticker):

    data = yf.Ticker(ticker)

    cash = data.cashflow
    oper_cash = cash.loc['Total Cash From Operating Activities']
    cap_ex = abs(cash.loc['Capital Expenditures'])

    return oper_cash - cap_ex

# print(get_free_cash_flow("MSFT"))


def revenue_growth_rate(ticker):

    data = yf.Ticker(ticker)

    fin = data.financials
    revenue = fin.loc['Total Revenue']

    # Reverse the list so that it is easier to iterate through.
    revenue_reversed = revenue.iloc[::-1]

    growth = []
    for i in range(len(revenue_reversed)):

        # Since we cannot have a growth rate for our starting
        # value, just skip it.
        if i == 0:
            pass
        else:
            growth.append((revenue_reversed[i] - revenue_reversed[i - 1]) / revenue_reversed[i - 1]) 
    
    # From the list we have just created, find it's median value
    # using the statistics library, and add 1 to get the growth
    # rate.
    return 1 + round(statistics.median(growth), 3)


# print(revenue_growth_rate("SBUX"))


def net_income_margin(ticker):
    
    data = yf.Ticker(ticker)
    fin = data.financials

    return round(statistics.median(fin.loc['Net Income'] / fin.loc['Total Revenue']), 3)

# print(net_income_margin("ALLY"))


def future_revenue(ticker):

    data = yf.Ticker(ticker)
    fin = data.financials
    revs = fin.loc['Total Revenue']
    future_revenues = []

    ticker_growth = revenue_growth_rate(ticker)

    future_revenues.append(round(revs[0] * ticker_growth))
    while len(future_revenues) < 4:
        future_revenues.append(round(future_revenues[-1] * ticker_growth))

    return future_revenues

# print(future_revenue("AAPL"))

# def starting_function(ticker):
#     data = yf.Ticker(ticker)
#     fin = data.financials
#     return fin

def future_net_margins(ticker):
    data = yf.Ticker(ticker)
    future_income = []

    future_revenues = future_revenue(ticker)
    net_margin = net_income_margin(ticker)
    future_income.append(round(future_revenues[0] * net_margin))
    while len(future_income) < 4:
        future_income.append(round(future_income[-1] * net_margin))

    return future_income

    
# print(future_net_margins("MDU"))

def free_cash_flow_to_net_margin(ticker):
    data = yf.Ticker(ticker)
    fin = data.financials
    fcf = get_free_cash_flow(ticker)
    net_income = fin.loc['Net Income']

    return round(statistics.median(fcf / net_income), 3)

# print(free_cash_flow_to_net_margin("AAPL"))

def get_future_cash_flows(ticker):
    data = yf.Ticker(ticker)
    fcf = get_free_cash_flow(ticker)
    fcf_rate = free_cash_flow_to_net_margin(ticker)
    future_fcf = []

    future_fcf.append(round(fcf[0] * fcf_rate))
    while len(future_fcf) < 4:
        future_fcf.append(round(future_fcf[-1] * fcf_rate))
    
    return future_fcf

# print(get_future_cash_flows("AAPL"))

### Calculate WACC

bond = ip.bonds.get_bonds_overview("United States")

t_bill_ten = bond[bond['name'] == 'U.S. 10Y']['last'] / 100

market_return = .08
info = msft.info



def cost_of_equity(ticker):

    data = yf.Ticker(ticker)
    info = data.info
    beta = 0
    for key, value in info.items():
        if key == 'beta':
            beta = value
    
    buffer = t_bill_ten + (beta * (market_return - t_bill_ten))
    buffer_dict = buffer.to_dict()
    cost = 0
    for value in buffer_dict.values():
        cost = value

    return round((cost), 3)
    

# print(cost_of_equity("AAPL"))


balance = msft.balance_sheet
info = msft.info
fin = msft.financials
# print(balance)


def cost_of_debt(ticker):
    data = yf.Ticker(ticker)
    balance = data.balance_sheet
    fin = data.financials

    total_debt = balance.loc['Short Long Term Debt'] + balance.loc['Long Term Debt']

    cost_debt = abs(fin.loc['Interest Expense']) / total_debt

    tax_rate = fin.loc['Income Tax Expense'] / fin.loc['Income Before Tax']

    after_tax = cost_debt * (1 - tax_rate)

    return round((after_tax[0]), 3)

# print(cost_of_debt("AAPL"))






aapl = yf.Ticker("AAPL")
# print(aapl.info)





def wacc(ticker):
    data = yf.Ticker(ticker)
    info = data.info
    balance = data.balance_sheet

    market_cap = 0
    for key, value in info.items():
        if key == 'marketCap':
            market_cap = value
    
    total_debt = balance.loc['Short Long Term Debt'] + balance.loc['Long Term Debt']

    cost_equity = cost_of_equity(ticker)
    cost_debt = cost_of_debt(ticker)

    share_of_equity = market_cap / (market_cap + total_debt)
    share_of_debt = total_debt / (market_cap + total_debt)

    wacc = (share_of_equity * cost_equity) + (share_of_debt + cost_debt)

    return round((wacc[0]), 3)

# print(wacc("AAPL"))


### Discount factor


def discount_factor(ticker):
    weighted = wacc(ticker)

    i = 1
    discount = []
    while i < 5:
        discounted = round(((1 + weighted) ** i), 3)
        discount.append(discounted)
        i += 1
    
    return discount

# print(discount_factor("MSFT"))


### Terminal Value

perpetual_growth_rate = .025

def terminal_value(ticker):
    future_cash = get_future_cash_flows(ticker)
    weighted = wacc(ticker)

    return (future_cash[-1] * (1 + perpetual_growth_rate)) / (weighted - perpetual_growth_rate)

# print(terminal_value("AAPL"))


### Present value of cash flows






def present_values(ticker):

    fcf = get_future_cash_flows(ticker)
    discount = discount_factor(ticker)
    terminal = terminal_value(ticker)

    fcf.append(terminal)
    discount.append(discount[-1])

    pv = [i / j for i, j in zip(fcf, discount)]

    return pv

# print(present_values("AAPL"))

def fair_value(ticker):

    data = yf.Ticker(ticker)
    info = data.info

    for key, value in info.items():
        if key == 'sharesOutstanding':
            shares = value
    
    pv = present_values(ticker)

    sum = 0
    for i in range(0, len(pv)):
        sum = sum + pv[i]
    
    return round((sum / shares), 2)

# print(fair_value("AAPL"))