# 批量离线翻译（ctranslate2 + sentencepiece 直接调用 Argos 模型包，整批 translate_batch，比逐句 argos 快很多）
import os,ctranslate2,sentencepiece as spm
PK=os.path.expanduser('~/.local/share/argos-translate/packages')
DIR={'zh|en':'translate-zh_en-1_9','en|ja':'en_ja','en|ko':'en_ko','en|es':'en_es','en|de':'translate-en_de-1_3',
     'en|fr':'translate-en_fr-1_9','en|ms':'translate-en_ms-1_9','en|vi':'translate-en_vi-1_9'}
_M={}
def _load(k):
    if k not in _M:
        d=os.path.join(PK,DIR[k])
        _M[k]=(ctranslate2.Translator(os.path.join(d,'model'),device='cpu',inter_threads=1,intra_threads=int(os.environ.get('CT2_THREADS','4'))),
               spm.SentencePieceProcessor(model_file=os.path.join(d,'sentencepiece.model')))
    return _M[k]
import re
SYM=re.compile(r'(\s*(?:→|->|≥|≤|≈|~|¥|×|•|·)\s*)')
JUNK=re.compile(r'^\s*@\s?\w+\s*:|_BAR_')
def batch(texts,f,t,cache=None,bs=32):
    """符号（→ ≥ ~ ¥ 等）先切开分段翻译再拼回，避免模型词表缺字产生 <unk>/_；明显的垃圾输出回退原文"""
    cache=cache if cache is not None else {}
    k=f+'|'+t
    segs={s:SYM.split(s) for s in texts}
    pieces=sorted({p for v in segs.values() for p in v[::2] if re.search(r'[A-Za-z\u4e00-\u9fff]',p)})
    m=_raw(pieces,f,t,cache,bs)
    out={}
    for s,v in segs.items():
        r=''.join((m.get(p,p) if i%2==0 else p) for i,p in enumerate(v))
        out[s]=r
        cache[k+'|'+s]=r
    return out
def _raw(texts,f,t,cache=None,bs=32):
    k=f+'|'+t; cache=cache if cache is not None else {}
    todo=sorted({s for s in texts if k+'|'+s not in cache and s.strip()},key=len)
    if todo:
        tr,sp=_load(k)
        for i in range(0,len(todo),bs):
            chunk=todo[i:i+bs]
            toks=[sp.encode(s,out_type=str)[:400] for s in chunk]
            res=tr.translate_batch(toks,beam_size=2,max_decoding_length=512,max_batch_size=bs,replace_unknowns=True)
            for s,r in zip(chunk,res):
                o=''.join(r.hypotheses[0]).replace('\u2581',' ').strip()
                cache[k+'|'+s]=s if JUNK.search(o) or ('_' in o and '_' not in s) else o
    return {s:cache.get(k+'|'+s,s) for s in texts}
