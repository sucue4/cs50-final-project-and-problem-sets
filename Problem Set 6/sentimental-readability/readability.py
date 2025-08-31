letters = 0
sentences = 0
words = 1

text = input("Text: ")

for char in text:
    if (char.isalpha()):
        letters += 1
    elif (char == ' '):
        words += 1
    elif (char == '.' or char == '?' or char == '!'):
        sentences += 1

index = round(0.0588 * letters / words * 100 - 0.296 * sentences / words * 100 - 15.8)

if (index < 1):
    print("Before Grade 1")
if (index >= 16):
    print("Grade 16+")
else:
    print("Grade ", index)
