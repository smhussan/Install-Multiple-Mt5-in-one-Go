Add script to automate MetaTrader 5 installations
This script installs additional copies of MetaTrader 5 by automating the installation wizard. It will install multiple copies in one go , to run this program you need python 11.9 and it is intended to use for windows 11, i am not sure on other versions ,you should have this file and and MT5 setup in same folder and in startup menu ,search  "cmd" → right-click → Run as administrator).than for example your folder with both files 
cd C:\Users\pc\Music
than copy paste this to cmd 
python install_mt5_copies.py
it will ask how many copies you want to install, 2 3 4 10 12 
That's it. this is  full working version.
 it will do all clicking through with the real control IDs from your wizard: Settings → set path → uncheck the checkbox → Next → wait for Finish → click it → wait for the wizard to close → move to the next one.
Run it the same way:
