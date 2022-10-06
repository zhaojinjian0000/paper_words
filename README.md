# paper_words
organize and translate words in papers.

# install
```shell
# install packages
pip install loguru
pip install pdfminer.six
pip install tabulate

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

export NLTK_DATA=`pwd`/nltk_download #每次都启动终端都运行一次, 否则写在.bashrc or .zshrc里
cd ../..

# install ECDICT
git clone git@github.com:skywind3000/ECDICT.git
cd ECDICT
python -c "from stardict import *; print(convert_dict('ecdict.db', 'ecdict.csv'))"
# 出现文件ecdict.db


```
# usage
```shell
python main.py
```