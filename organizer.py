import json

class Organizer:
  def __init__(self, word_list, get_file = None, accuracy = 5):
    self.word_list = word_list
    self.word_size = len(word_list[0])
    self.list_history = []
    self.possibilities = self.create_all_possibilities()
    self.make_word_points()
    self.make_points_by_word()
    self.accuracy = accuracy
    
  def make_word_points(self):
    word_points = {
      'size': self.word_size,
      'by_letter': {},
      'by_place': {}
    }

    for i in range(1, self.word_size+1):
      word_points['by_place'][str(i)] = {}
    
    for letter in range(ord('a'), ord('z')+1):
      letter = chr(letter)
      word_points['by_letter'][letter] = 0
      for i in range(1, self.word_size+1):
        word_points['by_place'][str(i)][letter] = 0
    
    for word in self.word_list:
      word_set = list(set(list(word)))
      for letter in word_set:
        word_points['by_letter'][letter] += 1
      
      for enum in enumerate(word):
        index, letter = enum
        word_points['by_place'][str(index+1)][letter] += 1
    
    self.word_points = word_points
  
  def create_all_possibilities(self):
    full_array = []
    def recursive(left, arr = []):
      for i in range(3):
        arr.append(i)
        if not left:
          full_array.append(arr.copy())
        else:
          recursive(left-1, arr)
        arr.pop()
    
    recursive(self.word_size-1)

    str_array = []
    for line in full_array:
      str_array.append(''.join([str(v) for v in line]))
    
    
    for i in range(len(str_array)):
      value1 = str_array[i]
      similarity1 = self.get_similarity(value1)
      for j in range(i+1, len(full_array)):
        value2 = str_array[j]
        similarity2 = self.get_similarity(value2)

        if similarity1 > similarity2:
          str_array[i],str_array[j] = str_array[j],str_array[i]
          similarity1 = similarity2
    
    return str_array
          
  def create_word_spectrum(self, word):
    possibilities = self.possibilities.copy()
    spectrum = {}
    for possibility in possibilities:
      spectrum[possibility] = 0
    
    for word2 in self.word_list:

      result = self.compare_words(word,word2)
      spectrum[result] += 1
    
    return spectrum

  def compare_words(self,word, word2):
    result = ['0' for i in range(self.word_size)]
    
    for enum in enumerate(word2):
      index, letter = enum
      if letter == word[index]:
        result[index] = '2'
      elif letter in word:
        result[index] = '1'
    
    return ''.join(result)

  def get_similarity(self, similarity):
    letters = 25
    permutations = self.word_size - 1
    percentage_by_char = 100/self.word_size
    points = [percentage_by_char for i in range(self.word_size)]
    final_percentage = 0
    for value in similarity:
      if value == '0':
        letters -= 1
      elif value == '2':
        permutations -= 1
    
    if permutations <= 1:
      permutations = letters

    for value in similarity:
      sum_percentage = 1
      if value == '0':
        sum_percentage = letters
      elif value == '1':
        sum_percentage = permutations
      final_percentage += percentage_by_char/sum_percentage
    
    return final_percentage
  
  def filter_words(self, word, similarity, replace_list = True):
    sim_obj = self.make_sim_obj(word, similarity)
    print(sim_obj)
    possible_words = []

    for word in self.word_list:
      add_word = True
      for rule in sim_obj:
        letter = rule['letter']
        if 'not_included' in rule:
          if letter in word:
            add_word = False
            break

        elif 'not_in' in rule:
          index = rule['not_in']

          if word[index] == letter:
            add_word = False
            break

          if letter not in word:
            add_word = False
            break
        
        elif 'in' in rule:
          index = rule['in']

          if word[index] != letter:
            add_word = False
            break
      
      if add_word:
        possible_words.append(word)
    if(replace_list):
      self.replace_list(possible_words)

  def replace_list(self, new_list):
    self.list_history.append(self.word_list)
    self.word_list = new_list

  def make_sim_obj(self, word, similarity):
    sim_obj = []
    for enum in enumerate(similarity):
      index, sim_type = enum
      obj = {
        'letter': word[index]
      }
      if sim_type == '0':
        obj['not_included'] = True
      elif sim_type == '1': 
        obj['not_in'] = index
      else:
        obj['in'] = index
      
      sim_obj.append(obj)
    
    return sim_obj

  def get_word_points(self, word):
    letter_points = 0
    place_points = 0

    for enum in enumerate(word):
      index, letter = enum
      place_points += self.word_points['by_place'][str(index+1)][letter]
    
    for letter in list(set(word)):
      letter_points += self.word_points['by_letter'][letter]
    return {
      'letter_points': letter_points,
      'place_points': place_points
    }
  
  def make_points_by_word(self):
    self.points_by_word = {}
    for word in self.word_list:
      self.points_by_word[word] = self.get_word_points(word)

  def get_best_words(self):
    best_word = max(self.word_list, key = lambda x: self.points_by_word[x]['letter_points'])
    min_value =  self.points_by_word[best_word]['letter_points']*(100-self.accuracy)/100
    best_words = []

    for word in self.word_list:
      if self.points_by_word[word]['letter_points'] >= min_value:
        best_words.append(word)
    max_len = len(best_words)
    for i in range(max_len):
      for j in range(i+1, max_len):
        word1 = best_words[i]
        word2 = best_words[j]
        points1 = self.points_by_word[word1]
        points2 = self.points_by_word[word2]
        if points1['letter_points'] < points2['letter_points']:
          best_words[i], best_words[j] = best_words[j], best_words[i]
          continue
        if points1['letter_points'] == points2['letter_points'] and points1['place_points'] < points2['place_points']:
          best_words[i], best_words[j] = best_words[j], best_words[i]
          continue
    
    if len(best_words) < 10:
      best_words = list(set(best_words + self.word_list[:10]))
    
    
    return [{
      'word': word,
      'letter_points': self.points_by_word[word]['letter_points'],
      'place_points': self.points_by_word[word]['place_points']} 
      for word in best_words]
    






  

  


