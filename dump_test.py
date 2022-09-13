import pickle



a = [1,2,3,4,5,6]
b = [6,5,4,3,2,1]


with open("./test.dump",'wb') as f:
  pickle.dump(a,f)
  pickle.dump(b,f)



with open("./test.dump",'rb') as f:
  print pickle.load(f)
  print pickle.load(f)
