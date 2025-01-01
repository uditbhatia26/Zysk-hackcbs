from flask import Flask, redirect, request, jsonify, render_template, url_for
import os, markdown
from bs4 import BeautifulSoup
import google.generativeai as genai
import requests, random 

app = Flask(__name__)

questions = [
    {
        'Question': 'What is your primary financial goal?',
        'Options': [
            'Retirement planning (e.g., NPS, PPF)',
            'Saving for a major purchase (home, car, etc.)',
            'Education fund (for self or children)',
            'Achieving financial independence',
            'Other (please specify)'
        ]
    },
    {
        'Question': 'What is your investment horizon (how long do you plan to keep your investments)?',
        'Options': [
            'Less than 1 year',
            '1-5 years',
            '5-10 years',
            'More than 10 years'
        ]
    },
    {
        'Question': 'What’s your monthly net income (after tax)?',
        'Options': [
            'Below ₹25,000',
            '₹25,000 - ₹50,000',
            '₹50,000 - ₹1,00,000',
            'Above ₹1,00,000'
        ]
    },
    {
        'Question': 'How would you describe your current financial situation?',
        'Options': [
            'Struggling to make ends meet',
            'Living paycheck to paycheck',
            'Able to save some money each month',
            'Financially comfortable with room for investments'
        ]
    },
    {
        'Question': 'What’s your primary motivation for investing?',
        'Options': [
            'Grow wealth long-term',
            'Generate passive income',
            'Achieve financial security',
            'Explore and learn about investments'
        ]
    },
    {
        'Question': 'How much debt do you currently have (home loan, personal loan, credit cards, etc.)?',
        'Options': [
            '0',
            'Under ₹2,00,000',
            '₹2,00,000 - ₹10,00,000',
            'Above ₹10,00,000'
        ]
    },
    {
        'Question': 'Do you have an emergency fund?',
        'Options': [
            'No emergency funds',
            '3-6 months of expenses',
            'Less than 3 months of expenses',
            'No, I don’t see the need for one'
        ]
    },
    {
        'Question': 'How much risk are you willing to take with your investments?',
        'Options': [
            'Very low',
            'Low',
            'Moderate' ,
            'High'
        ]
    },
    {
        'Question': 'What type of investments are you most comfortable with?',
        'Options': [
            'Fixed deposits (FDs) and government schemes (PPF, NSC)',
            'Mutual funds or ETFs',
            'Individual stocks',
            'Real estate or gold'
        ]
    },
    {
        'Question': 'How often do you review or adjust your investments?',
        'Options': [
            'Rarely or never',
            'Annually',
            'Quarterly',
            'Monthly'
        ]
    },
    {
        'Question': 'What percentage of your income are you willing to invest?',
        'Options': [
            '0-5%',
            '5-10%',
            '10-20%',
            'More than 20%'
        ]
    },
    {
        'Question': 'How would you rate your knowledge of financial markets?',
        'Options': [
            'Beginner',
            'Intermediate',
            'Advanced',
            'Expert'
        ]
    },
    {
        'Question': 'Do you currently work with a financial advisor?',
        'Options': [
            'Yes',
            "No"
        ]
    },
    {
        'Question': 'How do you feel about credit cards?',
        'Options': [
            'Avoid them',
            'Use them but pay off monthly',
            'Carry a balance sometimes',
            'Rely on them frequently'
        ]
    },
    {
        'Question': 'Do you have a retirement savings plan?',
        'Options': [
            'Yes',
            'No'
        ]
    },
]
responses = []

genai.configure(api_key=os.getenv("API_KEY"))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="Context: You are an AI financial advisor. Your goal is to generate a personalized financial analysis and investment strategy based on user-provided details about their financial goals, income, risk tolerance, and investment preferences. Provide the output such that it can be rendered in an html file.\n\nInstruction:\n\nInput: You will receive a prompt containing a set of user responses that describe their financial situation, including:\n\nPrimary Financial Goal: This could be retirement planning, wealth accumulation, buying a house, etc.\nInvestment Horizon: Duration over which the user plans to invest (e.g., short-term, long-term).\nIncome Level: The user’s monthly income range.\nRisk Tolerance: The user’s comfort level with risk (low, medium, high).\nInvestment Preferences: Types of investment options the user prefers (e.g., Fixed Deposits, stocks, bonds, etc.).\nDebt Situation: Whether the user has current debt obligations.\nSavings and Expenditure Patterns: Information on the user’s emergency fund, monthly savings, and spending habits.\nOutput: Generate a detailed financial analysis and investment strategy recommendation, including the following:\n\nFinancial Profile: Based on the user’s financial goal, income, and spending habits, describe their financial situation, including how they approach saving and investing.\n\nIncome and Expenditure Analysis: Describe the user’s ability to save, their current savings habits, and any important considerations regarding their income and expenses.\n\nRisk Tolerance and Investment Preferences: Based on their risk tolerance and preferred investment types, provide insights into their investment choices and how they align with their goals.\n\nFinancial Knowledge and Attitudes: Comment on the user’s understanding of their financial situation, risk, and the level of active involvement they have in managing investments.\n\nSavings and Spending Habits: Provide analysis on their ability to meet financial goals based on their savings rate and expenditure habits.\n\nFuture Financial Planning: Offer insights into their future financial outlook based on the data provided, including the steps they are taking to ensure financial security.\n\nInvestment Strategy Recommendation: Based on the financial profile, recommend a personalized investment strategy, tailored to their risk tolerance, goals, and preferences. Include suggestions for low, medium, or high-risk investments and appropriate asset allocation to achieve the user's financial goals.\n\nPrompt Template Example:\n\nThe user’s primary financial goal is retirement planning, with a long-term investment horizon of more than 10 years. They have a monthly net income between ₹50,000 and ₹1,00,000 and describe themselves as financially comfortable. Their motivation is to grow wealth over the long term, with no current debt obligations and an emergency fund covering 3-6 months of expenses. However, they have a very low risk tolerance, preferring stable investments like Fixed Deposits (FDs) or government schemes such as PPF. They review their investments annually and are willing to allocate 10-20% of their income to investments.\n\nExample of Generated Output:\nFinancial Profile: Based on your responses, you have a clear focus on building long-term wealth, with retirement planning as your primary goal. Your stable income and disciplined saving habits position you well to achieve your financial goals over time. Your preference for low-risk investments reflects a cautious approach to wealth accumulation.\n\nIncome and Expenditure: You have a steady income and a strong focus on saving, allocating a significant portion of your earnings towards your investments. Your emergency fund, which covers 3-6 months of expenses, provides additional financial security.\n\nRisk Tolerance and Investment Preferences: You exhibit a very low risk tolerance and prefer stable, guaranteed returns from options such as Fixed Deposits and government-backed schemes like PPF. This aligns with your goal of long-term wealth accumulation without the risk of significant losses.\n\nInvestment Strategy Recommendation: Given your preference for low-risk investments, consider allocating the majority of your portfolio to Fixed Deposits, PPF, and high-quality bonds. You may also explore other government-backed schemes with tax benefits. A small portion of your portfolio may be allocated to debt mutual funds to add diversity while maintaining low risk. Review your portfolio annually to ensure it remains aligned with your long-term goals.\n\n\nSample Prompt: The user’s primary financial goal is retirement planning, with a long-term investment horizon of more than 10 years, indicating a preference for stable, growth-oriented options. They have a monthly net income between ₹50,000 and ₹1,00,000 and describe themselves as financially comfortable, allowing room for regular investments. Their motivation is to grow wealth over the long term, with no current debt obligations and an emergency fund covering 3-6 months of expenses. However, they have a very low risk tolerance, preferring stable investments like Fixed Deposits (FDs) or government schemes such as PPF. They are comfortable with low-risk, secure investment options, review their investments annually, and are willing to allocate 10-20% of their income to investments. Based on this profile, generate a personalized investment strategy focused on secure, long-term growth aligned with retirement planning.\n\nSample Output: Your primary financial goal is retirement planning, with a long-term investment horizon of over 10 years. This indicates that you are focused on building wealth over an extended period, with a preference for stability and low-risk investments. Your current financial comfort, with a monthly income between ₹50,000 and ₹1,00,000, allows you to save and invest regularly without the stress of meeting immediate financial obligations. Your emergency fund is well-established, covering 3-6 months of expenses, ensuring you’re financially secure during unforeseen circumstances.\n\nIncome and Expenditure:\nYour steady income and lack of current debt obligations place you in a strong position to allocate a portion of your earnings to investments. With 10-20% of your income designated for savings, you are setting a firm foundation for future growth. Your financial habits reflect a balanced approach, ensuring you maintain a healthy buffer for emergencies while investing for long-term wealth.\n\nRisk Tolerance and Investment Preferences:\nYou have a very low risk tolerance, which makes sense given your focus on long-term security rather than speculative gains. This aligns with your preference for conservative investment options like Fixed Deposits (FDs) and government-backed schemes such as the Public Provident Fund (PPF), which provide guaranteed returns over time. Your preference for low-risk, stable investments is well-suited to your financial goals, ensuring that you maintain steady growth without the volatility that comes with higher-risk assets.\n\nFinancial Knowledge and Attitudes:\nYou have a clear understanding of your risk tolerance and investment preferences. While you review your investments annually, you prefer low-maintenance investment options, indicating a desire for passive wealth accumulation with minimal active management. Your investment approach reflects caution and careful planning, ensuring a secure financial future with a focus on avoiding unnecessary risk.\n\nSavings and Spending Habits:\nYour disciplined approach to saving and spending allows you to allocate a reasonable portion of your income to investments. Your emergency fund and budgeting habits show that you prioritize financial stability and long-term planning. By setting clear goals and regularly contributing to your investments, you are building a strong financial foundation that will support you in retirement.\n\nFuture Financial Planning:\nAs you plan for retirement, your stable income and careful management of finances position you well to meet your long-term goals. Your avoidance of debt and commitment to saving, combined with your preference for low-risk investments, ensures that you can steadily grow your wealth while protecting your principal. Your focus on financial security and a stable retirement is clear, and your financial habits reflect that commitment.\n\nInvestment Strategy Recommendation\nGiven your preference for low-risk investments and a long-term horizon, a conservative investment strategy is recommended. Focus on guaranteed returns through Fixed Deposits (FDs) and government-backed schemes like PPF, which provide safety and stable growth over time. You can also consider a mix of high-rated bonds or debt mutual funds for some diversification within your risk tolerance, ensuring you earn more than traditional savings accounts without taking on too much risk.\n\nWhile equity markets might seem appealing for long-term growth, your low-risk preference makes them less suitable at this time. Instead, maintain a secure and reliable growth trajectory by maximizing contributions to tax-saving schemes like PPF, which also offer tax benefits.\n\nRegularly reviewing your portfolio annually, as you currently do, will allow you to ensure your investments are in line with your goals. By sticking to low-risk options and maintaining a steady savings rate, you’ll be well-positioned to achieve a financially secure retirement.\n\n\nSample Prompt: \"The user's financial goal is retirement planning. The investment horizon is more than 10 years. The income level is above ₹1,00,000, and their financial situation is financially comfortable. The motivation for investing is to grow wealth long-term. The user's savings rate is greater than 20%, and they have no debt. Their monthly expenditure is between ₹30,000 and ₹50,000, and they have an emergency fund that is sufficient to cover 3-6 months of expenses. They follow a strict budget and have a high risk tolerance. The user prefers investing in growth stocks and reviews their investments monthly. They invest 10-20% of their income, with a preference for dividend-paying stocks. Their financial knowledge is at an intermediate level, and they occasionally use an advisor. Sustainability is very important to them, and they are somewhat interested in alternative investments. They rely on credit cards, paying them monthly, and have a retirement plan.\"\n\n\n\nSample Output:  Financial Profile\nBased on your responses, you have a clear focus on building long-term wealth, with retirement planning as your primary goal. You aim to grow wealth over an extended period, demonstrated by your 10+ years investment horizon and disciplined financial situation. With a strong income level above ₹1,00,000 and a high savings rate (greater than 20%), you are well-positioned to achieve your long-term objectives. Your focus on retirement planning reflects a commitment to financial independence and security.\n\nIncome and Expenditure\nYour income level, which exceeds ₹1,00,000, combined with a well-managed budget, allows you to save and invest with confidence. You have an emergency fund sufficient to cover 3-6 months of expenses, indicating that you're prepared for unforeseen financial challenges. Your monthly expenditure between ₹30,000 and ₹50,000 falls within a structured budget, enabling you to prioritize saving and investing for the future while maintaining a stable lifestyle.\n\nRisk Tolerance and Investment Preferences\nYou demonstrate a high risk tolerance and a preference for growth stocks. This suggests you are willing to take on more risk to achieve potentially higher returns over time. Your interest in growth stocks and dividend-paying stocks reflects your desire for both capital appreciation and regular income. Reviewing your portfolio on a monthly basis allows you to remain actively involved in managing your investments and adjusting your strategy to remain aligned with your financial goals.\n\nFinancial Knowledge and Attitudes\nWith an intermediate understanding of financial markets, you are knowledgeable enough to manage your investments and financial strategies effectively. You occasionally seek external advice from financial advisors, which helps to enhance your investment approach without fully relying on them. Your interest in sustainable investing demonstrates your desire to align your financial goals with your ethical values, ensuring that your investment decisions reflect your broader life priorities.\n\nSavings and Spending Habits\nYou have a disciplined approach to saving, consistently allocating more than 20% of your income toward future goals. By maintaining a strict budget and tracking your expenses, you ensure that you are living within your means and preparing for your financial future. Your commitment to a strict budget supports a proactive financial strategy that prioritizes saving, making you well-positioned to reach your long-term goals.\n\nFuture Financial Planning\nYou have taken steps to secure your financial future and that of your family. This includes having a will in place, ensuring that your legacy and financial plans are protected. Your focus on tax minimization and avoiding debt further reflects your dedication to maintaining a financially secure and stable future. These steps show you are focused on building a long-term strategy for both personal and family financial well-being.\n\nInvestment Strategy Recommendation\nStrategy Recommendation\nGiven your focus on long-term wealth accumulation and retirement planning, a balanced investment strategy is ideal for you. With a high savings rate and a 10+ year investment horizon, you can afford to take on a higher level of risk while also ensuring steady income.\n\nA diversified portfolio of growth stocks, dividend-paying stocks, and socially responsible ETFs will provide both capital appreciation and regular income. Growth stocks will help you achieve higher returns, while dividend stocks offer stability. To balance the risk, consider adding bonds or low-volatility assets for stability during market downturns.\n\nSince sustainability is important to you, consider ESG funds that align with your values and offer long-term growth. Regularly reviewing your portfolio will ensure it remains aligned with your retirement goals, while tax-minimizing strategies will help you retain more of your investment gains.\n\nBy focusing on both growth and security, you can build a stable foundation for a comfortable retirement while staying true to your ethical investment preferences.\n\nSample Prompt: The user’s financial goal is achieving financial independence with a long-term investment horizon of over 10 years. They earn above ₹1,00,000 per month and are financially comfortable. Their motivation is long-term wealth growth, with a savings rate of >20% and no debt. Monthly expenses range between ₹30,000 and ₹50,000, with a sufficient emergency fund. They have a high risk tolerance, prefer individual stocks, and review investments quarterly. The user allocates >20% of their income to investments, prefers growth stocks, and values sustainability. They have intermediate financial knowledge, occasionally consult a financial advisor, and have a retirement plan.\n\nSample Output: Financial Profile:\nYour primary goal of achieving financial independence with a long-term horizon indicates a strong focus on building wealth over time. With a comfortable income and a disciplined savings rate of more than 20%, you are positioned for robust financial growth. Your ability to allocate a significant portion of your income toward investments is a testament to your commitment to long-term financial success.\n\nIncome and Expenditure:\nYour monthly income above ₹1,00,000 provides ample room for saving and investing. With expenses between ₹30,000 and ₹50,000, you maintain a good balance, while your emergency fund is well-stocked to cover 3-6 months of expenses, giving you a safety net in case of unforeseen events. Your strict budget and solid financial habits support your continued growth.\n\nRisk Tolerance and Investment Preferences:\nYou have a high risk tolerance, which suits your preference for individual stocks. This indicates a willingness to embrace higher volatility in pursuit of greater long-term gains. Your quarterly review of investments ensures you're actively managing your portfolio, aligning it with your financial goals.\n\nFinancial Knowledge and Attitudes:\nWith intermediate financial knowledge, you are capable of navigating your investments with confidence. Your occasional use of a financial advisor allows you to refine strategies without fully relying on external guidance. Additionally, your interest in sustainability reflects a desire to align your investment choices with your personal values.\n\nSavings and Spending Habits:\nYour savings rate of more than 20% demonstrates a strong commitment to growing your wealth, and your ability to live within a reasonable monthly budget supports this goal. You have a clear focus on long-term growth, and your consistent allocation to investments showcases financial discipline.\n\nFuture Financial Planning:\nYour well-defined retirement plan and the absence of debt show that you are already on the right path to securing your financial future. With no immediate financial obligations or concerns, you are well-positioned to continue building wealth sustainably.\n\nInvestment Strategy Recommendation:\n\nGiven your financial profile and long-term goal of achieving financial independence, a well-diversified, growth-focused investment strategy will serve you best. With a high risk tolerance and a strong preference for individual stocks, you are well-positioned to pursue higher returns, particularly in growth sectors such as technology, renewable energy, and healthcare. These industries are known for their long-term potential and can provide both capital appreciation and strong returns over time.\n\nTo balance your aggressive growth strategy, consider adding exposure to sustainable investments, such as ESG (Environmental, Social, and Governance) funds or socially responsible ETFs. This will allow you to pursue financial growth while remaining aligned with your personal values, which you value highly. A portion of your portfolio could also be allocated to international stocks, providing geographic diversification and tapping into emerging markets that offer additional growth opportunities.\n\nGiven your preference for individual stocks, it's important to focus on companies with strong fundamentals, solid growth trajectories, and a commitment to sustainability. Look for blue-chip stocks or those with strong market positions, but also remain open to mid-cap stocks that offer high growth potential, especially in emerging sectors. While individual stocks can be volatile, your high risk tolerance will allow you to weather short-term fluctuations for long-term gains.\n\nAdditionally, continue reviewing your investments quarterly. This will allow you to adjust your portfolio to adapt to changing market conditions, opportunities, and risks. Since you allocate more than 20% of your income to investments, you have the flexibility to periodically rebalance your portfolio, ensuring it stays aligned with your long-term goals and risk preferences.\n\nConsider incorporating some alternative investments into your strategy as well. Although you are focused on individual stocks, diversifying into real estate, commodities like gold, or even bonds for a small portion of your portfolio can provide stability during market volatility while still allowing for significant growth. By including a mix of assets, you can ensure that your wealth-building strategy remains resilient over the long term.\n\nLastly, your financial knowledge will enable you to make informed decisions, but continue leveraging the insights from a financial advisor when needed. They can provide an external perspective to help refine your investment strategy and ensure it remains optimized as your financial situation evolves.\n\nThis strategic approach will help you build wealth steadily while balancing the high-growth potential of individual stocks with sustainable, long-term investment principles.\n\nSample Input: The user’s financial goal is saving for a major purchase with an investment horizon of 1-5 years. They earn ₹50,000-₹1,00,000 per month, save 10-20%, and have debt under ₹2,00,000. Monthly expenses are ₹15,000-₹30,000, with an emergency fund covering less than 3 months of expenses. They track spending loosely, have a moderate risk tolerance, and prefer mutual funds or ETFs, reviewing investments annually. They allocate 5-10% of their income to investments, prefer growth stocks, and have intermediate financial knowledge. They’re considering a financial advisor, value sustainability, and use credit cards occasionally, with a retirement plan in place. \n\nSample Output: Financial Profile Report\n\nFinancial Overview:\nWith a primary goal of saving for a significant purchase within the next 1-5 years, you have established a solid financial foundation. Earning between ₹50,000 and ₹1,00,000 monthly, you are in a position to save regularly and manage moderate debt levels. Your savings rate of 10-20% and low monthly expenses of ₹15,000-₹30,000 reflect disciplined spending habits. Maintaining an emergency fund, even if it currently covers less than three months’ expenses, adds a layer of financial security for short-term needs.\n\nIncome and Expenditure:\nYour ability to save monthly despite a moderate debt level (under ₹2,00,000) shows a balanced approach to managing income and expenditure. This disciplined budgeting approach allows for consistent savings, while your preference for loose spending tracking keeps you adaptable in achieving both short- and long-term financial objectives.\n\nInvestment Preferences and Strategy:\nYour moderate risk tolerance aligns well with a diversified portfolio of mutual funds or ETFs, as these offer both stability and potential for growth. Since you prefer growth stocks within this category, your choice supports capital appreciation over time, suitable for your investment horizon. Allocating 5-10% of your monthly income to investments, coupled with an annual review, helps you stay on course while adjusting for market shifts.\n\nRisk Tolerance and Financial Knowledge:\nGiven your moderate risk tolerance and interest in growth-focused investments, you demonstrate a balanced approach to wealth-building. Your intermediate knowledge level equips you to make informed choices, and your openness to consulting a financial advisor in the future could further refine your strategy, helping you adapt as market conditions and your financial situation evolve.\n\nSustainability and Spending Habits:\nYou place importance on sustainability, which reflects your long-term approach to financial health and ethical investment choices. Occasional use of credit cards, along with a structured repayment habit, supports this approach, minimizing high-interest debt and reinforcing a responsible spending model.\n\nInvestment Strategy Recommendation:\nTo achieve your goal of saving for a major purchase within the next 1-5 years, consider a balanced strategy emphasizing capital preservation and growth. A portfolio primarily focused on mutual funds or ETFs can offer both stability and the growth potential you seek, with a heavier allocation towards growth-oriented ETFs in line with your moderate risk tolerance. As market conditions fluctuate, prioritize ETFs that have a good track record of stable performance, especially those aligned with sustainability if this aligns with your values.\n\nAdditionally, consider including a small allocation in dividend-paying funds or fixed-income assets to generate regular income and balance market volatility. Regular annual reviews will allow you to make minor adjustments and ensure your investments align with your upcoming financial needs. Consulting with a financial advisor on an as-needed basis can provide insights into optimizing this strategy, particularly if your debt level changes or you approach your purchase timeline.\n",
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "The user’s financial goal is saving for a major purchase with an investment horizon of 1-5 years. They earn ₹50,000-₹1,00,000 per month, save 10-20%, and have debt under ₹2,00,000. Monthly expenses are ₹15,000-₹30,000, with an emergency fund covering less than 3 months of expenses. They track spending loosely, have a moderate risk tolerance, and prefer mutual funds or ETFs, reviewing investments annually. They allocate 5-10% of their income to investments, prefer growth stocks, and have intermediate financial knowledge. They’re considering a financial advisor, value sustainability, and use credit cards occasionally, with a retirement plan in place.",
      ],
    },
    {
      "role": "model",
      "parts": [
        "## Financial Profile:\n\nYou are focused on achieving a specific short-term goal – saving for a major purchase within 1-5 years. Your moderate risk tolerance and preference for mutual funds and ETFs reflect a balanced approach to investing. You are financially comfortable, earning ₹50,000-₹1,00,000 per month, but your debt obligation under ₹2,00,000 and an emergency fund covering less than 3 months of expenses require attention. \n\n## Income and Expenditure:\n\nYou have a stable income with a healthy savings rate of 10-20%, indicating a good foundation for achieving your short-term goal. However, your debt obligation needs to be addressed to enhance your financial stability. Your monthly expenses fall within a reasonable range, but a more disciplined approach to tracking spending could further improve your savings potential.\n\n## Risk Tolerance and Investment Preferences:\n\nYour moderate risk tolerance aligns well with your preferred investment options – mutual funds and ETFs. You are comfortable with some level of volatility but prefer a more controlled approach. Your preference for growth stocks reflects a desire for potential capital appreciation, making it important to choose funds focused on growth sectors within your preferred investment timeframe.\n\n## Financial Knowledge and Attitudes:\n\nYour intermediate financial knowledge is a good starting point. You are comfortable managing your investments independently but considering a financial advisor demonstrates an openness to professional guidance, which can be beneficial, especially with the added complexity of your debt situation and short-term goals. \n\n## Savings and Spending Habits:\n\nYou have established good savings habits, but a more disciplined approach to tracking spending and managing debt would further strengthen your financial position. Consider budgeting tools or apps to gain better control over your expenses and increase your savings rate. \n\n## Future Financial Planning:\n\nYour existing retirement plan demonstrates long-term planning, but focusing on addressing your debt and increasing your emergency fund is crucial for financial security.  \n\n## Investment Strategy Recommendation:\n\n**Short-Term Goal:**\n\n1. **Debt Management:** Prioritize paying off your debt as quickly as possible. Consider debt consolidation or debt-reduction strategies to minimize interest costs and free up more cash flow for savings.\n2. **Emergency Fund:**  Focus on building your emergency fund to cover at least 3-6 months of expenses. This will provide a safety net, reducing the risk of dipping into your savings for unforeseen emergencies.\n3. **Investment Strategy:**\n    * **Mutual Funds and ETFs:** Focus on short-term or mid-cap growth-oriented mutual funds and ETFs, aligning with your preference for growth stocks and your 1-5 year investment horizon. Consider funds focusing on sectors relevant to your major purchase goal.\n    * **Sustainability:** Incorporate ESG (Environmental, Social, and Governance) focused funds into your portfolio to align your investments with your values.\n\n**Long-Term Planning:**\n\n1. **Retirement Planning:** Periodically review your existing retirement plan and ensure it aligns with your long-term goals. Consider increasing contributions as your financial situation improves.\n2. **Financial Advisor:**  Consider engaging a financial advisor, especially to address your debt, build your emergency fund, and formulate a comprehensive investment strategy for your long-term goals.\n\n**Additional Considerations:**\n\n* **Credit Card Usage:** Minimize your credit card usage and strive to pay your balance in full each month to avoid accumulating debt.\n* **Investment Reviews:** Continue reviewing your investments annually and consider adjusting your portfolio as your financial situation changes and your investment horizon approaches.\n* **Budgeting:**  Implement a more disciplined budgeting approach to track your spending and allocate funds efficiently towards debt reduction, emergency fund building, and investment goals.\n\nBy focusing on debt reduction, building your emergency fund, and investing strategically, you can achieve your short-term goal of saving for a major purchase while simultaneously laying a solid foundation for long-term financial security. Remember that by seeking professional advice and making informed financial decisions, you can navigate your financial journey with confidence and success. \n",
      ],
    },
  ]
)

gpt_response = ''

def send_update():
    return ''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # When the button is clicked, invoke the function
        send_update()  # This will call the backend function
        return redirect(url_for('index'))  # Redirect back to the homepage
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    # Collect responses from form data
    responses = request.form.getlist('responses')
    user_profile = f"""
    The user’s financial goal is {responses[0]} with an investment horizon of {responses[1]}.
    They earn {responses[2]} per month, save {responses[9]}, and have debt of {responses[5]}.
    Their current financial situation is: {responses[3]}.
    The user has emergency funds to cover {responses[6]} months of expenses.
    The user's risk tolerance is {responses[7]} and they prefer to invest in {responses[8]}.
    They review investments {responses[10]}, and they are willing to invest {responses[11]} of their income.
    They rate their financial knowledge as {responses[12]} and do not currently work with a financial advisor, {responses[13]} credit cards, and {responses[14]} a retirement savings plan.
    """
    gpt_response = chat_session.send_message(user_profile)
    return render_template('analysis.html', model_response=markdown.markdown(gpt_response.text))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
