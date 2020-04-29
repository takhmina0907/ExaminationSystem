import itertools


def lower_headers(iterator):
    return itertools.chain([next(iterator).lower()], iterator)


# def process():
#     from string import ascii_lowercase
#     import csv, io
#     csv_str = io.StringIO(open('questions.csv').read())
#     questions = csv.DictReader(lower_headers(csv_str), delimiter=',', quotechar='"')
#     totalrow, outof = 0, 0
#     for question in questions:
#         totalrow += 1
#         correct_num = 0
#         print(question)
#         try:
#             # question['question']
#             # question['correct']
#             print('Create Question ', question['question'])
#             correct = [c.strip().lower() for c in question['correct'].split(',')]
#             print(correct)
#             for letter in ascii_lowercase:
#                 if letter in questions.fieldnames:
#                     if letter in correct:
#                         print('Create correct option', question[letter])
#                         correct_num += 1
#                     else:
#                         print('Create incorrect option', question[letter])
#
#             if correct_num > 1:
#                 print('Make question multiple choice', question['question'])
#         except KeyError:
#             outof += 1
#
#     print('%d questions were created successfully out of %d' % (totalrow-outof, totalrow))
# process()
