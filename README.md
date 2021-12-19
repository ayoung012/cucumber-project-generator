### Cucumber project generator

Generate a large cucumber project with some randomly generated
step definitions and scenarios to match.

A primitive rolling shutter of the dictionary tries to group vocabulary
within each step definitions class.

#### Requirements
- python3

#### Usage
```
# Download a dictionary of words (at least 4000 unique words)
wget https://pastebin.com/CEiijxrm

# Run the cucumber project generator with the dictionary
python3 gen.py CEiijxrm
```
