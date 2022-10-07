from ECDICT.stardict import StarDict
from words import Words
import glob

def main():
    # init words
    sd = StarDict("./ECDICT/ecdict.db", False)
    words = Words(sd)
    words.load_from_file("inputs/YOLOV6-2209.02976.pdf")
    
    # get hard words
    hard_words = words.filter_hard(
        frq_thr=500, 
        easy_words_files=glob.glob("./easy_words/*.csv"),
    )
    # 保存 or 输出
    hard_words.save(fn="./outputs/yolov6_utf8.csv", encoding="utf-8")
    hard_words.save(fn="./outputs/yolov6_gbk.csv", encoding="gbk")
    hard_words.save(fn="./outputs/yolov6.pdf", ttf="SIMYOU")
    
if __name__ == "__main__":
    main()