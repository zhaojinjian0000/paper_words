# paper_words
organize and translate words in papers.
- 本项目可以统计论文里英语难词
- 并离线进行翻译

# install
```shell
# install packages
pip install loguru
pip install pdfminer.six
pip install tabulate
pip install fpdf

# install nltk
pip install nltk
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('averaged_perceptron_tagger')"
python -c "import nltk; nltk.download('wordnet')"
python -c "import nltk; nltk.download('omw-1.4')"

# 如下载网速太慢可以手动安装, https://www.nltk.org/data.html
mkdir nltk_download
mkdir nltk_download/tokenizers
mkdir nltk_download/taggers
mkdir nltk_download/corpora

# 下载并解压这几个文件
https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip
https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/taggers/averaged_perceptron_tagger.zip
https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/omw-1.4.zip

# 将文件夹组织为如下形式
-- nltk_download
    -- tokenizers
        -- punkt
    -- taggers
        -- averaged_perceptron_tagger
    -- corpora
        -- wordnet
        -- omw-1.4
# 如果你放在了其他目录下, 请自行修改NLTK_DATA
# export NLTK_DATA=`pwd`/nltk_download

# install ECDICT
git clone git@github.com:skywind3000/ECDICT.git
cd ECDICT
python -c "from stardict import *; print(convert_dict('ecdict.db', 'ecdict.csv'))"
# 出现文件ecdict.db
```
# usage
- 把你的文件放在inputs文件夹里
- 修改main.py的以下代码，修改输入文件夹名
```python
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
```
- 然后直接运行即可
```shell
python main.py
```
- 会在./outputs/yolov6.csv生成难词表