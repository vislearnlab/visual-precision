# Instruction on sending out gift cards

## Update cdi data in polygon server
Subject data and response are stored in polygon server.

1. Navigate to polygon server for storing cdi data
- Connect to the lab polygon server using your own username and password
- Navigate to `/Volumes/vislearnlab/experiments/visual-precision/data/raw/lookit/cdi` where the subject response is stored

2. Download newest cdi data
- Open https://www.qualtrics.com in your browser and login using lab email and password
- Previous step might require you to login to lab email account and use the code sent by qualtrics through email
- Open **LWL: CDI - Level 1** and **VVI: CDI - Level 2A** separately and navigate to **Data & Analysis** section
- Click **Export & Import** and select **Export Data...**
- Download csv format using **Export values**

3. Update cdi data in polygon server
-  Drag the downloaded level1 and level2a data into `/Volumes/vislearnlab/experiments/visual-precision/data/raw/lookit/cdi`
- Delete the previous **cdi_level1.csv** and **cdi_level2a.csv**
- Change the corresponding file names into **cdi_level1.csv** and **cdi_level2a.csv**

## Generate gift card emails

1. Run the compensation script
- Open `compensation.qmd` in this folder
- Run the script

2. Check the generated emails
- Navigate to `/Volumes/vislearnlab/experiments/visual-precision/data/raw/lookit` 
- Open `matched_gift_cards.txt`, which contains the formatted emails ready to be sent

## Send out emails

1. Place to send email
- Go to https://childrenhelpingscience.com/login/ and login using your own email address and password
- Navigate to **Can you find the rose?** study page
- Go to **Message Participants**
- Remember to select **Transactional emails** everytime before you send email

2. Send emails
- check the `subject_data.csv` for **parent_hashed_id**, its order is matched to the order of emails in `matched_gift_cards.txt`
- Input id into **Recipients**
- Copy the corresponding email for this parent from `matched_gift_cards.txt` into **Body**
- For the email title, if you see survey link in the email content, use **Survey reminder and gift card for 'Can you find the rose?'**, otherwise use **Gift card for 'Can you find the rose?'**
- Click **Submit**

## Update three sheets

1. Update `subject_data.csv`
- For each email you sent, find corresponding row based on **parent_hashed_id**
- Update the **Paid** column value as Yes for that row
- Save the changes

2. Update `gift_cards.csv`
- Each email contains the gift card code, use that to locate the gift card being used
- Update the **Used** column of gift card codes you used to Yes
- Save

3. Update `matched_gift_cards.txt`
- Delete the email you just sent from the file
