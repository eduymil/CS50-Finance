# CS50-Finance
CS50 Finance is part of the <a href="https://cs50.harvard.edu/x/2022/">CS50: Introduction to Computer Science course.</a><br>
The project requirements can be found <a href = "https://cs50.harvard.edu/x/2022/psets/9/finance/">here.</a>
<img width="958" alt="image" src="https://user-images.githubusercontent.com/102196421/162103961-8ebbb7de-d811-4f52-9786-3130a740290b.png">
<img width="954" alt="image" src="https://user-images.githubusercontent.com/102196421/162104027-3dd64b11-a43d-4935-b34b-867700b8a278.png">
# Getting Started
<b>Requirements</b><br>
You must have <a href="https://code.visualstudio.com/docs/python/python-tutorial">Python</a> and <a href="https://code.visualstudio.com/docs/python/tutorial-flask">Flask</a> installed in your vscode<br>
<b>Download or pull the code</b><br>
`-git clone https://github.com/eduymil/CS50-Finance.git`<br>
<b>Download required dependencies</b><br>
`pip install cs50`<br>
`pip install Flask`<br>
`pip install Flask-Session`<br>
`pip install requests`<br>
<b>Get API key</b><br>
Visit <a href="https://iexcloud.io/cloud-login#/register/">iexcloud.io/cloud-login#/register/</a> and create an account<br>
Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.<br>
Once you’ve confirmed your account via a confirmation email, visit <a href="https://iexcloud.io/console/tokens">https://iexcloud.io/console/tokens </a>.<br>
Copy the key that appears under the Token column (it should begin with pk_).<br>
In your terminal window, execute
`$env:API_KEY=value` for windows users.<br>
`$ export API_KEY=value` for mac users.
