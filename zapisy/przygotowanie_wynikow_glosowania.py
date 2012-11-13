Zima = set()
Cyfry = set('0123456789')

def upper(s):
   s = clean(s)
   return unicode(s,"utf-8").upper().encode("utf-8")
   
def clean(s):
   return " ".join(s.split())
      
for x in open("zimowe_przedmioty.txt"):
   Zima.add(upper(x[:-1]))
   
zimowy = False
   
for x in open('glosowanie2012.txt'):
   L = x.split()
   if len(L) == 0: continue
   
   if not x[0] in Cyfry:
      przedmiot = upper(x)
      if przedmiot in Zima:
         print
         print "[" + przedmiot + "]"
         zimowy = True
      else:
         zimowy = False   
   else: 
      if zimowy:
         print x,
   
   
      
