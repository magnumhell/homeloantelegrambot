"""
   PyDOT October 19 2020 Final Project 

   Name: Jordan Sim Yan Jie
   Email: jordansimyj@gmail.com
   Project name: Home Loan Telegram Bot
   Problem statement: Too many platforms that provide home loan calculators but no complete journey for potential 
   homeowners since information are from disparate sources. Also, some are not in the context of Singapore 

   Solution: An all-in-one platform that provides homeowners with latest SIBOR rates, home loan details and 
   a calculator to compare between loans. 


   Data source (if any)
   - data source #1 https://www.singsaver.com.sg/home-loan
   - data source #2 https://www.abs.org.sg/benchmark-rates/rates-sibor
"""
import logging
import pprint
import sibor_loan as sl
from credentials import telegram_bot_token
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,Message)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import numpy_financial as npf

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

VIEW_CALC,SHOW_LOANS,LOAN_AMT,LOAN_TENURE,INT_RATE=0,1,2,3,4

# Save records of all chats
records = {}
default_val = {'action': '',
               'loan': None}

def start(update, context):
    global records
    user_id = update.message.from_user.id

    records[user_id] = default_val.copy()
    logger.info(f"{user_id} starts")

    # Show "View Loans", "Calc Loans" and "See SIBOR" buttons for user to click
    reply_keyboard = [['View Loans', 'Calc Loans','See SIBOR']]
    update.message.reply_text(
        'Hi! Welcome to Home Loan Bot!\n\n'
        '🏠🏘🏡🤖\n\n'
        'Send /about to find out more about this bot.\n'
        'Send /cancel to stop.\n\n'
        'Would you like to View Home Loans, Calculate Home Loans or Check SIBOR Rates?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return VIEW_CALC

def handleViewCalc(update, context):
    global records
    user_id = update.message.from_user.id

    view_calc = update.message.text.upper()
    records[user_id]['action'] = view_calc
    logger.info(f"{user_id}: Action = {view_calc}")
    if view_calc=='VIEW LOANS':
        # Show different loans
        loan_names=list(sl.loan_dict.keys())
        reply_keyboard = [loan_names]
        names='\n'.join(i for i in loan_names)
        update.message.reply_text(text=
            f'Hi! Please select a loan to view.\n\n{names}\n\n'
            'Send /cancel to stop.\n\n'
            '*Lowest rate* -> HSBC Home Loan\n*Most Popular* -> Standard Chartered Home Suite',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True,one_time_keyboard=True),parse_mode=telegram.ParseMode.MARKDOWN)
        return SHOW_LOANS
    elif view_calc=='CALC LOANS':
        update.message.reply_text(f'Starting Loan Calculator. What is the loan amount?')
        return LOAN_AMT
    elif view_calc=='SEE SIBOR':
        print(sl.df_s.to_string())
        update.message.reply_text(f'\n\n    \n   {sl.df_s.to_string()}\n\n'
        'Send /start to view loans or calculate loan.\n\n')
        return ConversationHandler.END
    elif view_calc=='/ABOUT':
        return about(update,context)
    

def handleLoanAmount(update, context):
    global records
    user_id = update.message.from_user.id

    amount = update.message.text.upper()
    try:
        amount=float(amount)
    except:
        update.message.reply_text(text="Please input a number")
        return LOAN_AMT
    # action = records[user_id]['action']
    records[user_id]['loan_amount'] = amount
    logger.info(f'{user_id}: Loan Amount = {amount}')

    update.message.reply_text(f'Your loan amount is: {amount} SGD. What is the loan tenure in years?')

    return LOAN_TENURE

def handleLoanTenure(update, context):
    global records
    user_id = update.message.from_user.id
    tenure = update.message.text.upper()
    try:
        tenure=float(tenure)
    except:
        update.message.reply_text(text="Please input a number")
        return LOAN_TENURE   
    records[user_id]['loan_tenure'] = tenure
    logger.info(f'{user_id}: Loan Tenure = {tenure}')

    update.message.reply_text(text=f'Your loan tenure is: {tenure} years. What are the interest rates?\n\n'
    'Please give them in the format _<Year 1%> <Year 2%> ... <Year n%> <Rest of the years%>_',
    parse_mode=telegram.ParseMode.MARKDOWN)

    return INT_RATE

def handleIntRate(update, context):
    global records
    user_id = update.message.from_user.id

    int_rate = update.message.text.upper()
    # action = records[user_id]['action']
    records[user_id]['int_rate'] = int_rate
    logger.info(f'{user_id}: Int Rate = {int_rate}')
    
    # Get final result
    result = generate_result(update,records[user_id])
    update.message.reply_text(result)

    return ConversationHandler.END

def handleLoanDetails(update, context):
    loan_name = update.message.text
    if loan_name=='/cancel':
        return cancel(update, context)
    features = sl.beautifyDict(sl.loan_dict[loan_name])
    # more_details = sl.loan_dict_w_more_details[loan_name]['More details:']
    update.message.reply_text(
        f'{loan_name}:\n\n{features}\n\n\n'
              'Send /start to view another loan, calculate loan or SIBOR rates.\n\n')
    return ConversationHandler.END

def generate_result(update,user_input):
    loan_amount = float(user_input['loan_amount'])
    loan_tenure = float(user_input['loan_tenure'])
    int_rate=user_input['int_rate']
    int_rate=int_rate.split()
    if len(int_rate)==1:
        print((float(int_rate[0])/1200))
        int_amt=loan_amount*(float(int_rate[0])/1200)
        mon_pay= int_amt+loan_amount/(loan_tenure*12)
        print(int_amt,mon_pay)
        IR=npf.rate(12*loan_tenure, -mon_pay, loan_amount, 0.0, when=0)
        print(IR)
        EIR= ((1+IR)**12)-1
        TLP=mon_pay*loan_tenure*12
        print(EIR)
        return (f'EIR is {round(EIR*100,4)}% Total Repayment Amount is {round(TLP,2)} SGD\n\n'
        'Send /start to view another loan or calculate loan.')
    
    elif len(int_rate)==0:
        update.message.reply_text('No interest rate added. Send /start to start over again.'
        'Send /start to view another loan or calculate loan.')
        return ConversationHandler.END
    else:
        roy_int=float(int_rate[-1])
        roy=float(loan_tenure-len(int_rate)+1)
        EIR=1
        TLP=loan_amount
        for i in int_rate[:-1]:
            int_amt=loan_amount*float(i)/1200
            TLP+=int_amt*12
            EIR=EIR*float(i)/100

        roy_int_amt=loan_amount*(roy_int/1200)
        roy_eir=(((1+roy_int/1200)**(roy))-1)
        EIR=(1+EIR)*(1+roy_eir)-1
        
        TLP+=roy_int_amt*roy*12
        return (f'EIR is {round(EIR*100,4)}% Total Repayment Amount is {TLP} SGD\n\n'
                'Send /start to view another loan or calculate loan.')

def cancel(update, context):
    global records
    user_id = update.message.from_user.id
    # user = update.message.from_user

    logger.info(f'{user_id}: Cancelled')
    update.message.reply_text('Bye! Send /start to start over again.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def about(update,context):
    global records
    user_id = update.message.from_user.id

    logger.info(f'{user_id}: Cancelled')
    update.message.reply_text('About\n\n'
            'This home loan bot is made for Singaporean home buyers!\n\n'
            'Your one stop platform to view and compare loans for your private home, calculate Effective Interest Rates (EIR) and total repayment and see SIBOR rates. Home Loan details are taken from Singsaver while SIBOR rates are taken from The Association of Banks in Singapore (ABS).\n\n'
            'If you liked this bot, please share it with your friends! Thank you for your support! 😊\n\n'
            'To go back, Send /start for the main menu.\n\n',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            VIEW_CALC: [MessageHandler(Filters.regex('^(?i)(View Loans|Calc Loans|See SIBOR)$'), handleViewCalc)],
            SHOW_LOANS: [MessageHandler(Filters.text, handleLoanDetails)],
            LOAN_AMT: [MessageHandler(Filters.text, handleLoanAmount)],
            LOAN_TENURE: [MessageHandler(Filters.text, handleLoanTenure)],
            INT_RATE: [MessageHandler(Filters.text, handleIntRate)],

        },

        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('help', help),
                   CommandHandler('about', about)
                   ]
    )

    dp.add_handler(conv_handler)

    # Log all errors
    dp.add_error_handler(error)


    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()



if __name__ == '__main__':
    main()
