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
try:
    import ipdb
except Exception:
    pass


class Words():
    def __init__(self, filenames:List[str]) -> None:
        # init db
        db = "./ECDICT/ecdict.db"
        self.sd = StarDict(db, False)
        print(f"{db} 目前已收录了 {self.sd.count()} 个单词")
        
        # pdf2words
        self._words_cnt = defaultdict(int)
        for fn in filenames:
            assert fn.endswith(".pdf")
            self.pdf2words(fn)

    def pdf2words(self, fn):
        """提取pdf里的单词"""
        # pdf转化为文本
        text = extract_text(fn)

        # 预处理
        text = text.lower()
        text = text.replace("\n\n", "\n").replace("-\n", "").replace("\n", " ")
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
        )
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
        
    def translate(self):
        self._words_translate = dict()
        for word in list(self._words_cnt.keys()):
            data = self.sd.query(word)
            if data is None:
                self._words_cnt.pop(word)
                logger.warning(f"{word}无法翻译， 数据库中不存在该单词")    
            elif (   '人名' in data['translation'] 
                  or '男子名' in data['translation'] 
                  or '男名' in data['translation'] 
                  or '女子名' in data['translation']
                  or '女名' in data['translation']
                  or '姓氏' in data['translation'] 
                  or '地名' in data['translation'] 
                  ):# 去除人名、地名
                
                self._words_cnt.pop(word)
                logger.warning(f"{word} 去除人名")    
            # elif data['collins'] is None:
            #     self._words_cnt.pop(word)
            #     logger.warning(f"{word} collins不存在, 可能是某个单词的变体")
            else:
                self._words_translate[word] = data
        
        self.sorted_words = sorted(self._words_cnt.keys(), key=lambda x:self._words_cnt[x], reverse=True)

    def get_hard(self, hard_frq=500, fmt="csv", filename="./outputs/tmp.csv", my_easy_words=None):
        if not hasattr(self, "old_easy_words"):
            self.old_easy_words = []
            for csv in glob.glob("./easy_words/*.csv"):
                with open(csv, encoding="utf-8") as f:
                    self.old_easy_words += [i.split(',')[0] for i in f.readlines()]
            self.old_easy_words = set(self.old_easy_words)

        self.hard_words = self.sorted_words
        self.hard_words = list(filter(
            lambda x: not 0<self._words_translate[x]['frq']<hard_frq, 
            self.hard_words
        ))
        self.hard_words = list(filter(
            lambda x: x not in self.old_easy_words, 
            self.hard_words
        ))
        res = []
        for word in self.hard_words:
            s = self._words_translate[word]['translation'].replace('\n',' ')
            res.append([word,s])
            # print(f"    频率: {self._words_cnt[word]}")
            # print(f"    柯林斯星级: {self._words_translate[word]['collins']}")
            # print(f"    当代语料库词频顺序: {self._words_translate[word]['frq']}")
        logger.info(f"get_hard Done, got {len(res)} hard words")
        if "print" in fmt:
            print(tabulate(res, ["words", "translation"], "grid",maxcolwidths=[30, 60]))
        if "csv" in fmt:
            with open(filename, "a", encoding="gbk") as f:
                print("\n".join([i[0]+","+i[1].replace(',',";") for i in res]), file=f)
            with open(filename.replace(".csv", "-utf-8.csv"), "a", encoding="utf-8") as f:
                print("\n".join([i[0]+","+i[1].replace(',',";") for i in res]), file=f)
        if "return" in fmt:
            return res
        
def main():
    # init words
    words = Words(["inputs/YOLOV6-2209.02976.pdf"])
    words.translate()
    words.get_hard(500,"csv", "./outputs/yolov6.csv")
    
if __name__ == "__main__":
    main()