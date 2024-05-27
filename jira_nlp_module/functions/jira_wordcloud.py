import jieba, re, os
from jieba import analyse
from jira_nlp_module.functions.jira_preprocess import jiraprocess
from wordcloud import WordCloud  
import matplotlib.pyplot as plt

class gen_wordcloud:
    def __init__(self, source_file_path, topk):
        self.path = str(source_file_path)
        self.topk = int(topk)
        self.name = re.split("\.", os.path.basename(self.path))[0]
        self.dir  = os.path.dirname(self.path)
        self.python_file_name = str("py-" + self.name)
        x = jiraprocess(jira_input_csv_path =self.path, output_csv_name=self.python_file_name)
        self.df, self.col = x.run()
        return
    
    def jieba_seg(self):
        userdict_p = "C:\\Users\\westwell\\Documents\\.WorkDocuments\\JiraNLP\\extra_dict\\userdict.txt"
        stopword_p = "C:\\Users\\westwell\\Documents\\.WorkDocuments\\JiraNLP\\extra_dict\\stop_words.txt"
        
        jieba.load_userdict(userdict_p)
        jieba.analyse.set_stop_words(stopword_p)

        TEXTS = list(self.df['BUG故障描述'].values)
        TEXT = ''
        for str in TEXTS:
            # print(str)
            str = re.sub("[\'\：\·\—\，\。\“ \”\n\u3000\？\、\'*\',\']", "", str)
            str = re.sub("溜破", "溜坡", str)
            str = re.sub(r"\人工拉车|\人工接管", "人工介入", str)
            str = re.sub("QC", "岸桥", str)
            TEXT += str
            # seg_list = jieba.cut(str, use_paddle=True)
            # print('/'.join(list(seg_list)), '\n')
        
        tags = jieba.analyse.extract_tags(TEXT, topK=K, withWeight=True)
        tokens = []
        for i in range(len(tags)):
            tokens.append(tags[i][0])
        return tokens

    def draw(self):
        tokens = self.jieba_seg()
        wordcloud = WordCloud(
            font_path='msyh.ttc', 
            width=800, 
            height=600, 
            mode='RGBA', 
            background_color=None,).generate(text = ' '.join(tokens)) 

        plt.imshow(wordcloud)
        plt.show()
        wordcloud.to_file(self.dir + '\\'+ self.name + '.png')
        return


WEEK_NUM = 17
FILENAME = "Jira 2024-04-25T17_35_39+0800" + ".csv"

basep = f"C:\\Users\\westwell\\Documents\\.WorkDocuments\\JiraNLP\\.Data\\Y24W{WEEK_NUM}\\"

PATH = basep+FILENAME
K = 15

y = gen_wordcloud(source_file_path=PATH, topk=K)
y.draw()