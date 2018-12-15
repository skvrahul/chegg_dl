# Chegg Downloader
Python script to automate the download of textbooks from Chegg.   

## Requirements
- ImageMagick(To combine a series of *png* files to a *pdf*)
- Selenium / Selenium Webdriver ( This script is specific to Chrome and hence may not work on Firefox)
- PIL

## Running
`before.sh` - Creates the directory where the *png* images are saved .    
`python -l <link to your textbook/answerbook>` .  
`after.sh` - Converts sequence of images into a single *pdf* file called *textbook.pdf*


## Note 
You may need to login to Chegg manually to bypass Chegg's captcha.
