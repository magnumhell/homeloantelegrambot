# Singapore Home Loan Calculator Bot on Telegram
This home loan bot is made for Singaporean home buyers! View and compare loans for your private home, calculate Effective Interest Rates (EIR) and total repayment and see SIBOR rates. Home Loan details are taken from Singsaver while SIBOR rates are taken from The Association of Banks in Singapore (ABS).

Effective Interest Rate is useful for home buyers to compare loans with different payment terms and tenure. By calculating EIR and determining the lowest, home buyers can identify the best loan for themselves.

The Effective Interest Rate is calculated with payment expected at end of month. It makes use of the formula given in the python library np.financial (https://numpy.org/numpy-financial/latest/)
The calculation is done iteratively by solving a non-linear equation. Hence, many home loan calculators do not publish the underlying formula. 

Example case:
  int_rate=1.8%
  loan_tenure=30 years
  loan_amount=500000
  number of payments in a year =12

  int_amt=loan_amount*(float(int_rate)/1200)
  monthly_payment= int_amt+loan_amount/(loan_tenure*12)

  AIR=npf.rate(12*loan_tenure, -monthly_payment, loan_amount, 0.0, when=0)

  EIR= ((1+IR)**12)-1

Result:
  EIR is 3.1588% Total Repayment Amount is 770000.0 SGD
