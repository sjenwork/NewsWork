import pandas as pd
import numpy as np
import sys, os, re, time
from tqdm import trange
from tqdm import tqdm

import torch
from torch import cuda
from torch.utils.data import (DataLoader, RandomSampler, SequentialSampler, TensorDataset)
from torch.nn import CrossEntropyLoss, MSELoss
from transformers import BertTokenizer, BertModel, BertForMaskedLM, BertForSequenceClassification

from multiprocessing import Pool, cpu_count

    
def labelmap():
    return dict(zip(('毒品', '災害防治', '環境汙染', '食品安全', '其他', '無關') , [i for i in range(6) ]))

def labelmapInv():
    return {j:i for i,j in labelmap().items()}

def longcut(sentence, num=480):
    if type(sentence) != list:
        sentence = [sentence]
    def cut(string):
        head = string[:num]
        ind = list(re.compile('。|;|；|！|!|\.').finditer(head))
        if ind != []:
            ind = ind[-1].start()+1
        else:
            ind= 100
        res = [string[:ind], string[ind:]]
        return res
    i = 0
    while len(sentence[-1]) > num:
        finish = sentence[:-1]
        unfini = sentence[-1]
        res = cut(unfini)
        sentence = finish + res
        i+=1
        if i >20:
          sentence[-1] = []
    return sentence

class SettingPath():
    def __init__(self, TASK_NAME, workType):
        self.workType = workType
        self._path(TASK_NAME)
        self._name(workType)

    def _path(self, TASK_NAME):
        self.BASE_PATH  = '/content/drive/My Drive/A21_NewsPrediction'
        self.TASK_NAME  = TASK_NAME
        self.DATA_DIR   = DATA_DIR    = 'DATA'
        self.OUTPUT_DIR = OUTPUT_DIR  = 'output_model'

        self.OUTPUT_DIR_TASK = os.path.join(OUTPUT_DIR, f'{TASK_NAME}')


    def _name(self, workType):
        self.CONFIG_NAME = CONFIG_NAME = 'config.json'
        self.WEIGHT_NAME = WEIGHT_NAME = 'pytorch_model.bin'
        self.CORPUS_NAME = CORPUS_NAME = 'vocab.txt'

class preProcessor(SettingPath):
    def __init__(self, procFname ,TASK_NAME, workType, selCols=['label', 'text'], max_seq_length=480, **kwargs):
        super(preProcessor, self).__init__(TASK_NAME, workType)
        self.max_seq_length = 480
        self.procInFile(procFname, selCols, workType)

    def __read__(self, fname):
        FileForm = fname.split('.')[-1]
        print(f'    >> 讀取資料中：')
        print(f'     >>> 檔案路徑：{fname}')
        print(f'     >>> 檔案格式 is: {FileForm}')
        assert FileForm in ['xls', 'xlsx', 'csv'], f'bad file extension {FileForm}'
        read = {'xls' : pd.read_excel,
                'xlsx': pd.read_excel,
                'csv' : pd.read_csv}
        return read[FileForm](fname)

    def procInFile(self, fname, selCols, workType):
        df = self.__read__(fname)
        self.df = df = df[selCols]

        if workType in ['train', 'test']:
            print('    >> 請使用已經整理完成之訓練集資料')
            df.columns = ['label', 'text']
            df_cut = df
            df_cut.to_excel('DATA/train_set_useless.xlsx', index=False)

        elif workType == 'pred':
            print('    >> 預測資料準備中')
            df.columns = ['text']
            df['label'] = '其他'
            df_cut = self.cutNews(df['text'])
            df_cut.to_excel('DATA/pred_set_cut.xlsx', index=False)

        self.df_cut = df_cut

    def cutNews(self, text): 
        num_of_word_per_news = self.max_seq_length - 20
        print(f'     >>> 將待預測之新聞分段，每段字數小於{num_of_word_per_news}字')
        text = text.str.replace('\s+',' ')
        text_cut = pd.DataFrame(text.apply(lambda i: longcut(i, num=num_of_word_per_news)).to_list())
        text_cut.columns = [f'text_{i}' for i in text_cut.columns]
        df = (pd.concat([self.df, text_cut], axis=1)
                .drop('text', axis=1)
                .reset_index()
                )
        
        df = (pd.wide_to_long(df, 'text', i=['index', 'label'], j='count', sep='_')
               .reset_index()
               .drop(['count'], axis=1)
               .dropna(subset=['text'])
            #    .drop_duplicates(subset=['text'])
               .reset_index(drop=True)
               )

        print(f'     >>> 避免字數過少的新聞片段影響判斷結果，移除少於10字之內容')
        df = df[df.text.str.len()>10]
        return df

class lineFeatures():
    def __init__(self, label, text):
        self.label = label
        self.text  = text

class InputFeatures():
    def __init__(self, input_ids, input_mask, segment_ids, label_id):
        self.input_ids   = input_ids
        self.input_mask  = input_mask
        self.segment_ids = segment_ids
        self.label_id    = label_id

def convert2feature(row):
    #max_seq_length = 500

    tokens      = ["[CLS]"] + tokenizer.tokenize(row.text) + ["[SEP]"]
    input_ids   = tokenizer.convert_tokens_to_ids(tokens)
    segment_ids = [0] * len(tokens)
    input_mask  = [1] * len(input_ids)
    padding     = [0] * (max_seq_length - len(input_ids))
    input_ids   += padding
    input_mask  += padding
    segment_ids += padding
    label_id = labelmap()[row.label]

    assert len(input_ids)   == max_seq_length
    assert len(input_mask)  == max_seq_length
    assert len(segment_ids) == max_seq_length

    return InputFeatures(input_ids, input_mask, segment_ids, label_id)

class toDataLoader(preProcessor):
    def __init__(self, procFname, TASK_NAME, workType, selCols, max_seq_length=480, batch_size=5):
        super(toDataLoader, self).__init__(procFname, TASK_NAME, workType, selCols, max_seq_length)
        df_feature = self.toloader(self.df_cut, batch_size)

    def toloader(self, df, batch_size):
        lines = [lineFeatures(i['label'], i['text']) for _, i in df.iterrows()]
   
        print('    >> 將新聞內容輸出成Bert要求之格式') 
        global max_seq_length 
        max_seq_length = self.max_seq_length
        with Pool(4) as p:
            loader = list(tqdm(p.map(convert2feature, lines), total=len(lines)))

        all_input_ids   = torch.tensor([i.input_ids   for i in loader], dtype=torch.long)
        all_input_mask  = torch.tensor([i.input_mask  for i in loader], dtype=torch.long)
        all_segment_ids = torch.tensor([i.segment_ids for i in loader], dtype=torch.long)
        all_label_ids   = torch.tensor([i.label_id    for i in loader], dtype=torch.long)
        data            = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids)
        
        if self.workType == 'train':
            '''
            此步驟在訓練資料時一定要做
            '''
            print(f'     >>> 訓練資料集處理，隨機挑選樣本做為訓練資料')
            data_sampler    = RandomSampler(data)
            dataloader      = DataLoader(data, sampler=data_sampler, batch_size=batch_size)
        else:
            dataloader      = DataLoader(data, batch_size=batch_size)

        self.batch_size = batch_size
        self.nlines = len(lines)
        self.n_label = len(labelmap())
        self.dataloader = dataloader

def get_predictions(model, dataloader, compute_acc=False):
    predictions = None
    correct = 0
    total = 0
      
    with torch.no_grad():
        for data in dataloader:
            if next(model.parameters()).is_cuda:
                data = [t.to("cuda:0") for t in data if t is not None]
            
            tokens_tensors, segments_tensors, masks_tensors = data[:3]
            outputs = model(input_ids=tokens_tensors, 
                            token_type_ids=segments_tensors, 
                            attention_mask=masks_tensors)
            
            logits = outputs[0]
            _, pred = torch.max(logits.data, 1)
            
            if compute_acc:
                labels = data[3]
                total += labels.size(0)
                correct += (pred == labels).sum().item()
                
            if predictions is None:
                predictions = pred
            else:
                predictions = torch.cat((predictions, pred))
    
    if compute_acc:
        acc = correct / total
        return predictions, acc
    return predictions

class trainModel(toDataLoader):
    def __init__(self, model, n_epochs, inParameter):
        super(trainModel, self).__init__(**inParameter)
        self.training(model, n_epochs)

    def training(self, model, n_epochs):
        device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f'    >> 使用{device}計算')
        model.to(device)
        model.train()
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
        
        _, acc = get_predictions(model, self.dataloader, compute_acc=True)
        print('     >>> initial acc: %.3f' %(acc))
        for epoch in trange(n_epochs, desc="Epoch"):
            running_loss = 0.0
            for step, data in enumerate(tqdm(self.dataloader, desc="Iteration")):

                tokens_tensors, segments_tensors, masks_tensors, labels = [t.to(device) for t in data]
                optimizer.zero_grad()
                
                outputs = model(input_ids=tokens_tensors, 
                                token_type_ids=segments_tensors, 
                                attention_mask=masks_tensors, 
                                labels=labels)

                loss = outputs[0]
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
            _, acc = get_predictions(model, self.dataloader, compute_acc=True)
            print('[epoch %d] loss: %.3f, acc: %.3f' %(epoch + 1, running_loss, acc))
        print('    >> 訓練完成，儲存訓練完之模型')
        model.save_pretrained('output_model/trained_model')
        self.model = model

class predict(toDataLoader):
    def __init__(self, procFname, TASK_NAME, workType, selCols, batch_size, max_seq_length=500):
        super(predict, self).__init__(procFname, TASK_NAME, workType, selCols, max_seq_length, batch_size)
        self.predict()

    def predict(self):
        device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        print(f'    >> 使用{device}計算')

        predictions = None
        correct = 0
        total = 0

        with torch.no_grad():
            tmp = []
            probs = []
            preds = []
            for data in tqdm(self.dataloader, desc="Evaluating"):
                if next(model.parameters()).is_cuda:
                    data = [t.to("cuda:0") for t in data if t is not None]

                tokens_tensors, segments_tensors, masks_tensors = data[:3]
                outputs = model(input_ids=tokens_tensors, 
                                token_type_ids=segments_tensors, 
                                attention_mask=masks_tensors)
                
                logits = outputs[0]
                m = torch.nn.Softmax(dim=1)
                prob, pred = torch.topk(m(logits), 1)
                probs+=prob.tolist()
                preds+=pred.tolist()
                    
                if predictions is None:
                    predictions = pred[0]
                else:
                    predictions = torch.cat((predictions, pred[0]))
        
        self.tmp = tmp
        self.preds = predictions
        self.probs = probs
        self.preds = preds

class saveLabel2file(SettingPath):
    def __init__(self, preds, probs, procFname, TASK_NAME, workType, **kwargs):
        print(f'    ------------------------------------------------')
        super(saveLabel2file, self).__init__(TASK_NAME, workType)
        self.procFname = procFname
        self.df = df = self.read(procFname)
        print('    >> 讀取分段後之待預測新聞內容：DATA/pred_set_cut.xlsx')
        self.df_cut = df_cut = self.read('DATA/pred_set_cut.xlsx')
        self.preds = preds
        self.relabel(df, df_cut, preds, probs)

    def __read__(self, fname):
        FileForm = fname.split('.')[-1]
        print(f'   >> 讀取原始待預測之新聞內容：{fname}')
        assert FileForm in ['xls', 'xlsx', 'csv'], f'bad file extension {FileForm}'
        read = {'xls' : pd.read_excel,
                'xlsx': pd.read_excel,
                'csv' : pd.read_csv}
        return read[FileForm](fname)

    def read(self, fname):
        df = self.__read__(fname)
        return df

    def relabel(self, df, df_cut, preds, probs):
        preds = pd.DataFrame(preds).replace(labelmapInv()).iloc[:,[0]]
        probs = pd.DataFrame(probs).iloc[:,[0]]
        preds.columns = ['preds']
        probs.columns = ['probs']
        df_cut = pd.concat([df_cut, preds, probs], axis=1)
        print('    >> 輸出預測完成之分段後新聞：DATA/Result_cut.xlsx')
        df_cut.to_excel('DATA/Result_cut.xlsx')

        print('    >> 根據分段新聞之預測結果，決定新聞最終之分類')
        prob = df_cut.pivot_table(index='index', columns='preds', aggfunc='mean').fillna(0).droplevel(0, axis=1)
        df = pd.concat([self.df, prob], axis=1)
        self.df_cut = df_cut
        self.prob = prob
        self.df = df

        dirname = os.path.dirname(self.procFname)
        #form    = self.procFname.split('.')[-1]
        outName = os.path.join(dirname, f'Result_merged.xlsx')
        print(f'    >> 輸出預測完成且整併完成之檔案：{outName}')
        df.to_excel(outName)
        print(f'     >>> 執行結果： {os.listdir("DATA/")}')

if __name__ == '__main__':
    do_train = False
    do_pred = True

    if do_pred:
        nlabels   = len(labelmap())
        TASK_NAME = 'news_classification'
        BERT_MODEL = 'bert-base-chinese'
        
        
        parameter = { 'TASK_NAME'  : TASK_NAME, 
                      'procFname'  : 'DATA/pred_set.xlsx',
#                      'selCols'    : ['內文'],
                      'selCols'    : ['news_content'],
                      'workType'   : 'pred',
                      'max_seq_length' : 500,
                      'batch_size' : 10,
                     }

        BERT_MODEL_trained  = os.path.join('output_model', f'trained_model')
        # BERT_MODEL          = 'bert-base-chinese'
        tokenizer           = BertTokenizer.from_pretrained(BERT_MODEL_trained)
        model               = BertForSequenceClassification.from_pretrained(BERT_MODEL_trained, num_labels=nlabels)
        p                   = predict(**parameter)
        s                   = saveLabel2file(p.preds, p.probs, **parameter)

    if do_train:
        os.chdir('/content/drive/My Drive/A21_NewsPrediction')
        nlabels   = len(labelmap())
        TASK_NAME = 'news_classification'
        BERT_MODEL = 'bert-base-chinese'

        tokenizer = BertTokenizer.from_pretrained(BERT_MODEL)
        model     = BertForSequenceClassification.from_pretrained(BERT_MODEL, num_labels=nlabels)

        model.to(device)
        parameter = { 'TASK_NAME'  : TASK_NAME, 
                      'procFname'  : 'DATA/train_set.xlsx',
                      'selCols'    : ['label', 'text'],
                      'workType'   : 'train',
                      'batch_size' : 10,
                     }
        m = trainModel(model, 6, parameter)

        # for test
