
2026 update: we are using Google Sheets for data entry. If you make
direct edits to these CSVs they will likely be overwritten. Contact us
by email if you would like to access the Google Sheet and do data
entry.


UniqueID generation
-------------------

To generate the UniqueIDs in Google sheets, assuming 
- Last Name is A2
- First Name is B2 
- PositionID is C2

=REGEXREPLACE(TEXTJOIN(" ",TRUE,C2,B2,A2), "\W", "-")

Explanation:
  TEXTJOIN(" ",TRUE,C2,B2,A2) -- concatenate PositionID First_Name
  Last_Name with spaces in between. TRUE means "skip any missing
  cells"

  REGEXREPLACE(..., "\W", "-") -- take all non-word characters (not
  alphanumeric, probably in ASCII) and replace with dashes. 



To put this into Google Sheets:
- Paste the formula into the UniqueID column

- Highlight the UniqueID column, <ctrl>-click to unselect the header,
and then press <ctrl>-<Enter> to copy to all other cells in the column
