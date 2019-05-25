# ThinkHR

### How to execute 
1. Clone the repository
2. Navigate to folder
3. Activate the venv by executing following command 
```bash
source venv/bin/activate
```
4. Run program
```bash
USAGE: python pii_converter.py --in inputfile [--out outputfile]
USAGE: python pii_converter.py inputfile [outputfile]
``` 

### Assumption
I have made following assumption to validate lines
1. lines in following format are valid lines
```text
LastName, FirstName, (703)-711-0996, Blue, 11013 
FirstName LastName, Purple, 14537, 713 905 0383
```
2. phone number, zip code and color can be in any order but required 
3. phone number should be in following formats only
```text
(703)-711-0996 OR 713 905 0383
```
4. zip code should only 5 digit. 9 digit zip code is not valid
5. Confusion around following line if it should be valid or not due to conflict between example shared and word document. I have currently consider this as valid line, however I have to comment out a regex rule to make it invalid.
```text
LastName, FirstName, 12023, 636 121 1111, Yellow 
``` 
