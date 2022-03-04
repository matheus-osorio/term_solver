from organizer import Organizer
import eel

eel.init('front')

f = open('word_list_5.txt')
words = f.read().split('\n')
organizer = Organizer(words)

@eel.expose
def get_best_words():
  return organizer.get_best_words()

@eel.expose
def filter_words(word, similarity):
  organizer.filter_words(word, similarity)
  return True

@eel.expose
def get_word_spectrum(word):
  spectrum = organizer.create_word_spectrum(word)
  order = organizer.possibilities

  return {
    'names': order,
    'values': [spectrum[v] for v in order]
  }


eel.start('term.html', mode='chrome')