import re
import os
import numpy as np
import pandas as pd


class jiraprocess():
    def __init__(self, jira_input_csv_path = None, jira_exported_html_path=None, output_csv_name=str) -> None:
        if jira_exported_html_path != None:
            self.df = pd.read_html(jira_exported_html_path)[1]
            self.output_path = os.path.dirname(jira_exported_html_path) + '\\' + output_csv_name + '.csv'
        elif jira_input_csv_path != None:
            self.df = pd.read_csv(jira_input_csv_path, on_bad_lines='skip', encoding='utf-8-sig')
            self.output_path = os.path.dirname(jira_input_csv_path) + '\\' + output_csv_name + '.csv'
        if 'Development' in self.df.columns:
            self.df = self.df.drop(['Development'], axis=1)
        return 

    def run(self):
        # filter on useful columns and rename columns
        col = ['问题关键字',
               '项目关键字', 
               '描述', 
               '自定义字段(是否人工进场介入)',
               '自定义字段(故障造成的耗时)']
        dict = {
            '问题关键字': 'Key',
            '项目关键字': 'Project',
            '描述': 'Description',
            '自定义字段(是否人工进场介入)': '人工介入',
            '自定义字段(故障造成的耗时)': 'Duration',
        }
        self.df = self.df[col]
        self.df.rename(columns=dict, inplace=True)

        # Preprocessing and keyword extracting
        ## To replace column names 
        replace_dict = {
            "Car number:|车辆：": '车号：',
            'BUG occurrence location:|Bug 出现位置：':'BUG出现位置：',
            'BUG occurrence time:|Bug 出现时间：|时间：' : 'BUG出现时间：',
            'BUG fault description:|问题描述：| Bug 故障描述：' : 'BUG故障描述：',
            'BUG handling method:|Bug 处理方式：' : 'BUG处理方式：',
            'Whether the vehicle has a box:|带箱信息：': '车辆是否带箱：',
            'Vehicle fault code:' : '车辆故障码：',
        }
        self.df['Description'] = self.df['Description'].apply(lambda x: self.search_replace(x, replace_dict))
        self.df['Description'] = self.df['Description'].apply(lambda x: self.sign_removal(x))
        self.df['Description'] = self.df['Description'].apply(lambda x: self.kwd_extract(x))
        
        # Duration clean
        if 'Duration' in self.df.columns:
            self.df['Duration'] = self.df['Duration'].apply(lambda x: self.duration_extract(x))
            self.df['Duration'], self.df['unit'] = self.df['Duration'].str.split(r'(\d+)', expand=True)[1].fillna(0.0001), self.df['Duration'].str.split(r'(\d+)', expand=True)[2].fillna('None')
            self.df['duration_min'] = self.df.apply(lambda d: self.timeCovertor(d['Duration'], d['unit']), axis=1)

        # Split keywords dictionary into seperate columns
        dcol = ['泊位', '车号', '船次', 'BUG出现时间', 'BUG出现位置', 'BUG处理方式', 'BUG故障描述', '车辆是否带箱', '车辆故障码',]

        for c in dcol:
            self.df[str(c)] = self.df['Description'].apply(lambda x: x[str(c)].replace(r'\s|\*','').strip() if (len(x)!=0 and str(c) in x.keys()) else 'None')

        self.df[dcol[0]] = self.df[dcol[0]].str.replace(r'泊位|场|\*|\、',"").str.strip()
        self.df[dcol[1]] = self.df[dcol[1]].str.replace(r'\*|车',"").str.strip()
        self.df[dcol[2]] = self.df[dcol[2]].replace(r"\D|\/","")


        # Specific column encoding
        self.df['BUG处理方式'] = self.df['BUG处理方式'].apply(lambda x: self.bug_res_clean(x))
        self.df['BUG处理方式_label'] = self.df.apply(lambda df: self.bug_res_labelling(df['人工介入'], df['BUG处理方式']), axis=1)
        self.df['BUG处理方式_label'] = self.df.apply(lambda df: self.bug_res_relabel(df['BUG处理方式_label'], df['BUG故障描述']), axis=1)
        self.df['BUG处理方式_zh'] = self.df['BUG处理方式_label'].apply(lambda x: self.label_to_zh(x))

        # working status labelling
        self.df['作业状态'] = self.df['BUG故障描述'].apply(lambda x: self.label_if_running(x))
        ind = self.df[(self.df['船次'] != '/') & (self.df['船次']!='None')].index
        self.df.loc[ind,'作业状态'] = int(1)

        # export
        self.df.to_csv(self.output_path, encoding='utf-8-sig')
        return self.df, self.df.columns

    def search_replace(self, text, replace_dict):
        '''Function to perform search and replace'''
        if pd.isnull(text):  # Check for NaN
            return text  # If NaN, return as is
        try:
            for old, new in replace_dict.items():
                text = text.replace(old, new)
                old_subs = old.split('|')
                for sub in old_subs:
                    text = text.replace(sub, new)
            return text
        except AttributeError:
            return text  # If not a string, return as is

    def sign_removal(self, TEXT):
        if type(TEXT)==str:
            return ''.join(re.split('\*', TEXT))
        else:
            return

    def kwd_extract(self, TEXT):
        if type(TEXT)==str:
            # display(TEXT)
            TEXT = TEXT.upper()
            TEXT = 'BUG'.join(TEXT.split('BUG '))
            TEXT = '：'.join(re.split('(?<=\D)\:', TEXT)) # use ：(CN) for kwd extraction
            TEXT = ':'.join(re.split('(?<=\d)\：(?=\d)', TEXT)) # use :(EN) for time variable
            TEXT = ''.join(re.split('\s(?=\：)', TEXT))
            TEXT = ' '.join(re.split('\r|\n', TEXT))
            # display(TEXT)
            TEXT = re.sub(r'(^|\n\s)(\车辆)', '  车号', TEXT)
            TEXT = re.sub(r'(^|\n|\s)(\船号)', '  船次', TEXT)
            TEXT = re.sub(r'(^|\n|\s)(\时间|\问题时间|\发生时间|TIME)', '  BUG出现时间', TEXT)
            TEXT = re.sub(r'(BUG失效描述|(BUG handling method))', 'BUG故障描述', TEXT)
            TEXT = re.sub(r'(^|\n|\s)(\问题描述|\现象|\问题模块|\问题|\描述|DESCRIPTION)(\：)', '  BUG故障描述：', TEXT)
            TEXT = re.sub(r'(^|\n|\s)(\带箱信息|BOX)', '  车辆是否带箱', TEXT)
            TEXT = re.sub(r'(^|\n|\s)(\处理方式|\解决方式|\解决方案|METHOD)', '  BUG处理方式', TEXT)
            # display(TEXT)
            keywords = dict(re.findall(r'(\w*)\：(.*?)(?=\w*\：|$)', TEXT))
            # display(keywords)
        else:
            keywords = {}
        return keywords

    def bug_res_clean(self, TEXT):
        if type(TEXT)==str:
            return TEXT.replace(r'*|\s', "")
        else:
            return

    def bug_res_labelling(self, label, TEXT):
        if label=='是': return int(0) # 人工介入==是
        else:
            TEXT = str(TEXT)
            if len(re.findall(r'人|手|拉车|MAN|按|进场|下场', TEXT)) > 0:
                return int(0)
            elif len(re.findall(r'重|复位|远程|平行|上下电|控制|任务|GUI|RES|清除', TEXT)) > 0:
                return int(1)
            elif len(re.findall(r'恢复', TEXT)) > 0:
                return int(2)
            else:
                return np.NaN
        
    def bug_res_relabel(self, label, TEXT):
        if label!=0 and label!=1 and label!=2:
            TEXT = str(TEXT)
            if len(re.findall(r'人|手|拉车|MAN|按|进场', TEXT)) > 0:
                return int(0)
            elif len(re.findall(r'重|复位|远程|平行|上下电|控制|任务|GUI|RES|清除|回退', TEXT)) > 0:
                return int(1)
            elif len(re.findall(r'恢复|自行|自己|驶离', TEXT)) > 0:
                return int(2)
            else:
                return np.NaN
        else: return label

    def label_to_zh(self, LABEL):
        if LABEL==0:
            return "人工介入"
        elif LABEL==1:
            return "远程介入"
        elif LABEL==2:
            return "自行恢复"
        else:
            return '暂无记录'
        
    def label_if_running(self, text):
        """0.非作业期间 1.作业期间 2.未知"""
        if type(text)==str:
            if len(re.findall(r"作业|箱|任务", text)) > 0:
                return int(1)
            elif len(re.findall(r"测试|充电|停车", text)) > 0:
                return int(0)
            else:
                return int(2)
        else:
            return

    def duration_extract(self, TEXT):
        if type(TEXT)==str:
            return ''.join(re.split(r'\s', TEXT))
        else:
            return np.nan

    def timeCovertor(self, number, unit):
        number = float(number)
        if r'M|m|分钟' in unit: 
            return number
        elif r'H|h|小时' in unit: 
            return number * 60
        elif r'D|d|天' in unit: 
            return number * 24 * 60
        elif r'S|s|秒' in unit and r'M|m|分钟' not in unit and r'H|h|小时' not in unit: 
            return number/60
        else: 
            if 0.1 < number < 60: return number
            elif number >= 60: return number/ 60
            else: return np.NaN

