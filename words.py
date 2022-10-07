import os
if "NLTK_DATA" not in os.environ:
    os.environ['NLTK_DATA']=f"{os.getcwd()}/nltk_download"
from math import ceil
from ECDICT.stardict import StarDict
from typing import List
from collections import defaultdict
from pdfminer.high_level import extract_text
import re
from loguru import logger
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from tabulate import tabulate
import glob
try: import ipdb
except Exception: pass

def read(*args, **kwargs):
    encodings = [kwargs["encoding"]] if "encoding" in kwargs else []
    encodings += ["gbk", "utf-8"]
    for encoding in encodings:
        try:
            kwargs["encoding"] = encoding
            with open(*args, **kwargs) as f:
                text = f.read()
            return text
        except UnicodeDecodeError as e:
            logger.warning(e)

class Words:
    def __init__(
            self,
            sd = None, # StarDict("./ECDICT/ecdict.db", False)
        ):
        self._words_cnt = defaultdict(int)
        self._words_translation = dict()
        self.sd = sd
        print(f"数据集目前已收录了 {self.sd.count()} 个单词")

    def load(self, text):
        self.text2words(text)
    
    def load_from_file(self, fn):
        if fn.endswith(".pdf"):
            text = extract_text(fn)
        elif fn.endswith(".txt"):
            text = read(fn)
        else:
            raise NotImplementedError(f"{fn} fmt dont support")
        self.text2words(text)
        
    def text2words(self, text):
        # 预处理
        text = text.lower()
        for _ in range(3):  # 多个回车
            text = text.replace("\n\n", "\n")
        text = text.replace("-\n", "").replace("- \n", "") # 被分割的单词
        text = text.replace("\n", " ") # 删除回车
        text = " " + text + " "
        
        # 去除奇怪的字符
        text = text.replace("ﬁ", "fi")
        text = text.replace("×", "x")
        text = text.replace("ﬂ", "fl")
        s = set(
            "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789" 
            ",.()[]{}<>?!@/\\+-~\"\' :\*%;=‘’`_|”“·¨´"
            "∗†"
            "𝟑–𝑁𝟏‡•"
            "\x0c"
            "ΑαΒβΓγΔδΕεϵΖζΗηΘθΙιΚκΛλΜμµΝνΞξΟοΠπΡρΣσςΤτΥυΦφϕΧχΨψΩω"
        ) #合法字符字典
        unsupported = set(filter(lambda x:x not in s,text))
        if len(unsupported) > 0:
            logger.warning(f"有些字符可能不支持, 需要手动添加规则: {list(unsupported)}")

        # 只保留的英语单词(最多带着-)
        # wanted, unwanted = "[a-zA-Z\-]", "[^a-z^A-Z^\-]"
        wanted, unwanted = "[a-zA-Z]", "[^a-z^A-Z]"
        words = re.findall(f"{unwanted}({wanted}+){unwanted}", text)
        
        # 去除太短的英语单词
        words = list(filter(lambda x:len(x)>4, words))
               
        # 还原单词词性
        words = [self.Lemmatization(word) for word in words]
        
        # 去重, 统计频率
        for word in words:
            self._words_cnt[word] += 1
        
        # 翻译并删除不合法的单词
        for word in list(self._words_cnt.keys()):
            data = self.sd.query(word)
            if data is None:
                self._words_cnt.pop(word)
                logger.warning(f"{word} 去除数据库中不存在的单词")    
            elif any(list(map(lambda x:x in data['translation'],
                    ("人名", "男子名","男名","女子名","女名","姓氏","地名")))):
                self._words_cnt.pop(word)
                logger.warning(f"{word} 去除人名地名")    
            else:
                data['translation'] = data['translation'].replace('\n',' ')
                self._words_translation[word] = data

    def Lemmatization(self, word):
        if not hasattr(self, "wnl"):
            self.wnl = WordNetLemmatizer()
        def get_wordnet_pos(tag):
            if tag.startswith('J'):
                return wordnet.ADJ
            elif tag.startswith('V'):
                return wordnet.VERB
            elif tag.startswith('N'):
                return wordnet.NOUN
            elif tag.startswith('R'):
                return wordnet.ADV
            else:
                return None
        sentence = word
        tokens = word_tokenize(sentence)  # 分词
        tagged_sent = pos_tag(tokens)     # 获取单词词性
        wnl = WordNetLemmatizer()
        lemmas_sent = []
        for tag in tagged_sent:
            wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
            lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos)) # 词形还原
        return lemmas_sent[0]


    def filter_hard(
            self, 
            frq_thr=500, 
            easy_words_files=[], # glob.glob("./easy_words/*.csv")
        ):
        # 获得简单单词表
        easy_words = []
        for fp in easy_words_files:
            easy_words += [i.split(',')[0] for i in read(fp).split()]
        easy_words = set(easy_words)
        
        # 滤除
        hard_words = [x for x in self._words_cnt.keys() 
            if (not 0<self._words_translation[x]['frq']<frq_thr) 
            and (x not in easy_words)
        ]
        
        # 构建新的Words类
        words = Words(self.sd)
        for k in hard_words:
            words._words_cnt[k] = self._words_cnt[k]
            words._words_translation[k] = self._words_translation[k]
        return words

    def save(
            self, 
            sort=True,
            fn="./outputs/tmp.csv",
            encoding="gbk",
            ttf="SIMYOU"
        ):
        words = self._words_cnt.keys()
        if sort:
            words = sorted(words, key=lambda x:self._words_cnt[x], reverse=True)
        data = [[x, self._words_translation[x]['translation']] for x in words]
        if fn.endswith(".csv"):
            with open(fn, "w", encoding=encoding) as f:
                f.write("\n".join(list(map(lambda i:f"{i[0]},{i[1]}", data))))
        elif fn.endswith(".txt"):
            with open(fn, "w", encoding=encoding) as f:
                f.write("\n".join(list(map(lambda i:f"{i[0]:30}\t{i[1]:60}", data))))
        elif fn.endswith(".pdf"):
            import fpdf
            import fpdf.ttfonts
            fpdf.ttfonts.warnings.filterwarnings("ignore")
            pdf = fpdf.FPDF()
            pdf.set_top_margin(10)
            pdf.set_auto_page_break(True, 10)
            pdf.add_page()
            pdf.add_font(ttf,'',f'./ttf/{ttf}.TTF',True) 
            pdf.set_font(ttf, size=10)
            length = 55
            for i, (w, t) in enumerate(data):
                pdf.cell(40, txt=f"{w:20} : ")
                pdf.cell(40, txt=t[:length])
                pdf.ln(5)
                for i in range(1, ceil(len(t)/length)):
                    pdf.cell(40, txt="")
                    pdf.cell(40, txt=t[i*length:(i+1)*length] )
                    pdf.ln(5)
            pdf.output(fn, "F")            
        else:
            logger.error(f"保存失败, 文件格式不支持:{fn}")
            print(tabulate(data, ["words", "translation"], "grid", maxcolwidths=[30, 60]))
        
    def __len__(self):
        return len(self._words_cnt)