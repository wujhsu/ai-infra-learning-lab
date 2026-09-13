"""Small causal attention proof; standard library only."""
import math

def attention(q,keys,values):
 scores=[sum(a*b for a,b in zip(q,k))/math.sqrt(len(q)) for k in keys]
 exps=[math.exp(s-max(scores)) for s in scores];weights=[e/sum(exps) for e in exps]
 return [sum(w*v[j] for w,v in zip(weights,values)) for j in range(len(values[0]))]

def run():
 old=[[1.,0.],[0.,1.]];new=[1.,1.]
 # Wq/Wk/Wv are identity for this proof. Actual networks learn these matrices.
 cached_keys=[x[:] for x in old];cached_values=[x[:] for x in old]
 cached_keys.append(new);cached_values.append(new)
 full=attention(new,old+[new],old+[new]);cached=attention(new,cached_keys,cached_values)
 assert all(abs(a-b)<1e-12 for a,b in zip(full,cached))
 print({'full_recompute':full,'cached':cached,'equal':True})
if __name__=='__main__':run()
