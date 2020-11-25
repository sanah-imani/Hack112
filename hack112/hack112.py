#import module_manager
#module_manager.review()

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile
import time
import math
import random
import matplotlib.pyplot as pPlot

import json

from difflib import SequenceMatcher

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

import requests
from bs4 import BeautifulSoup

class ZoomChatApp():
    def __init__(self):
        self.root = tk.Tk()
        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, padx=20, pady=(20, 0))

        self.keywordsFrame=Frame(self.root)
        self.keywordsFrame.grid(row=1, column=0, padx=20)

        self.chatFrame=Frame(self.root)
        self.chatFrame.grid(row=0, column=2, rowspan=2, padx=20, pady=20)

        self.bottomChatFrame=Frame(self.root)
        self.bottomChatFrame.grid(row=2, column=2, padx=20, pady=(20, 0))

        ttk.Separator(self.root, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=7, sticky="ns")
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=1, sticky="ew")

        self.attentionGraphLabelFrame=Frame(self.root)
        self.attentionGraphLabelFrame.grid(row=3, column=0, padx=20)

        self.attentionGraphFrame=Frame(self.root)
        self.attentionGraphFrame.grid(row=4, column=0, padx=20, pady=(0,20))

        self.listsFrame=Frame(self.root)
        self.listsFrame.grid(row=6, column=0, padx=20, pady=(0, 20))

        self.questionsFrame=Frame(self.listsFrame)
        self.questionsFrame.grid(row=1, column=0, pady=(0, 20))

        self.studentsFrame=Frame(self.listsFrame)
        self.studentsFrame.grid(row=1, column=1, pady=(0, 20))

        self.questionsLabel=tk.Label(self.listsFrame, text="Recent Questions: ")
        self.questionsLabel.grid(row=0, column=0, padx=20)

        self.studentsLabel=tk.Label(self.listsFrame, text="Most Engaged Students: ")
        self.studentsLabel.grid(row=0, column=1, padx=20)

        self.keywords=[]
        self.chat=[]
        self.timePassed=0
        self.running=False
        self.attention=[]
        self.questions=[]
        self.engagedStudents=[]
        self.new=True
        self.highRelevantWords=[]
        self.medRelevantWords=[]
        self.lowRelevantWords=[]
        self.chatTranscript=[]

        self.classButton=tk.Button(self.root, text="START CLASS" if not self.running else "END CLASS", command=self.changeClassStatus)
        self.classButton.grid(row=6, column=2, padx=20, pady=20, ipady=5)

        self.drawAttentionGraph()
        self.drawRelevantQuestionsList()
        self.drawEngagedStudentsList()

        self.attentionsLabel=tk.Label(self.attentionGraphLabelFrame, text="Attention of Class:")
        self.attentionsLabel.pack(side=TOP, fill=BOTH)

        self.enterKeywordsLabel=tk.Label(self.frame, text="Add Keyword: ")
        self.enterKeywordsText=tk.Entry(self.frame)
        self.button = tk.Button(self.frame,text="Add", command=self.addKeyword)

        self.enterKeywordsLabel.grid(row=0, column=0, sticky=E)
        self.enterKeywordsText.grid(row=0, column=1, sticky=E)
        self.button.grid(row=0, column=2, padx=(10, 0), pady=10, ipady=10, ipadx=20)

        self.keywordsLabel=tk.Label(self.keywordsFrame, text="Keywords: ")
        self.keywordsList=tk.Listbox(self.keywordsFrame)
        self.scrollKeywords=tk.Scrollbar(self.keywordsFrame)
        
        self.keywordsLabel.pack(side=TOP, fill=BOTH)
        self.keywordsList.pack(side=LEFT, fill=BOTH)
        self.scrollKeywords.pack(side=RIGHT, fill=BOTH)
        self.keywordsList.config(yscrollcommand = self.scrollKeywords.set) 
        self.scrollKeywords.config(command = self.keywordsList.yview) 

        self.chatList=tk.Listbox(self.chatFrame)
        self.scrollChat=tk.Scrollbar(self.chatFrame)
        self.chatLabel=tk.Label(self.chatFrame, text="Chat: ")
        self.uploadChatDataButton=tk.Button(self.chatFrame, text="Upload Chat Data", command=self.uploadChatData)

        self.uploadChatDataButton.pack(side=TOP, fill=BOTH,ipady=5)
        self.chatLabel.pack(side=TOP, fill=BOTH)
        self.chatList.pack(side=LEFT, fill=BOTH)
        self.scrollChat.pack(side=RIGHT, fill=BOTH)
        self.chatList.config(yscrollcommand = self.scrollChat.set) 
        self.scrollChat.config(command = self.chatList.yview) 

        self.chatEntry=tk.Entry(self.bottomChatFrame)
        self.sendChatEntry=tk.Button(self.bottomChatFrame, text="Send", command=self.sendChatData(self.chatEntry.get(), "Professor", self.timePassed))
        self.chatEntry.pack(side=TOP, fill=BOTH)
        self.sendChatEntry.pack(side=BOTTOM, fill=BOTH,ipady=5)

        self.minuteTimer()
        self.secondTimer()
        self.fiveMinuteTimer()

        self.root.mainloop()
    
    def changeClassStatus(self):
        self.running=not self.running
        self.classButton.config(text="START CLASS" if not self.running else "END CLASS")

    def drawRelevantQuestionsList(self):
        self.questionsList=tk.Listbox(self.questionsFrame)
        self.scrollQuestions=tk.Scrollbar(self.questionsFrame)
        self.questionsList.pack(side=LEFT)
        self.scrollQuestions.pack(side=RIGHT)
    
    def drawEngagedStudentsList(self):
        self.studentsList=tk.Listbox(self.studentsFrame)
        self.scrollStudents=tk.Scrollbar(self.studentsFrame)
        self.studentsList.pack(side=LEFT)
        self.scrollStudents.pack(side=RIGHT)

    def drawAttentionGraph(self):
        fig = Figure(figsize=(3, 2), dpi=100)
        self.subplot=fig.add_subplot(111)
        self.subplot.plot(self.attention)
        self.subplot.set_xlim([0, 30])
        self.subplot.set_ylim([0, 1])

        canvas = FigureCanvasTkAgg(fig, master=self.attentionGraphFrame)
        canvas.draw()
        self.widget=canvas.get_tk_widget()
        self.widget.pack(side=BOTTOM, fill=BOTH, expand=1)

    def sendChatData(self, text, name, time):
        if(self.running and text!=""):
            chatEntry=dict()
            chatEntry["timestamp"]=time
            chatEntry["chat"]=text
            chatEntry["name"]=name
            print(f"CHAT ENTRY: {chatEntry}")
            self.chat+=[chatEntry]
            self.chatList.insert(END, chatEntry["chat"])
            self.chatEntry.delete(0,END)
            self.chatEntry.insert(0,"")

    def uploadChatData(self):
        if(not self.running):
            file = askopenfile(mode ='r', filetypes =[('JSON Files', '*.json')]) 
            if file is not None: 
                content=file.read()
                content = json.loads(content)
                for chat in content:
                    self.chatTranscript.append(chat)
                print(self.chatTranscript)
                self.changeClassStatus()

    def fiveMinuteTimer(self):
        if(self.running):
            if(self.checkBreakTime()):
                self.showBreakTimeAlert()
        self.root.after(1000*60*5, self.fiveMinuteTimer)

    def minuteTimer(self):
        if(self.running):
            self.getMostEngagedStudents()
            self.studentsList.delete(0, END)
            for s in self.engagedStudents:
                self.studentsList.insert(END, s["name"])

            if(len(self.attention)==30): self.attention.pop(0)
            self.attention.append(self.getNewAttentionVal())
            self.widget.pack_forget()
            self.drawAttentionGraph()

            newQuestions=self.findQuestions()
            if(newQuestions!=None and len(newQuestions)>0):
                self.questions+=newQuestions
                for (q, _) in newQuestions:
                    self.questionsList.insert(END, q)
                self.sortQuestionsList()
                
        self.root.after(1000*60, self.minuteTimer)

    def sortQuestionsList(self):
        self.questions.sort(key=lambda tup: tup[1])
        self.questions.reverse(key=lambda tup: tup[1])
        self.updateQuestionsListBox()

    def updateQuestionsListBox(self):
         self.questionsList.delete(0,'end')
         for (q, _) in self.questions:
             self.questionsList.insert(END, q)

    def secondTimer(self):
        if(self.running):
            self.timePassed+=1
            if(len(self.chatTranscript)>0):
                chatValueAtTime=next((item for item in self.chatTranscript if item['timestamp'] == self.timePassed), None)
                print(chatValueAtTime)
                
                if (chatValueAtTime!=None):
                    self.sendChatData(chatValueAtTime["chat"], chatValueAtTime["name"], chatValueAtTime["timestamp"])

        self.root.after(1000, self.secondTimer)

    def showBreakTimeAlert(self):
        messagebox.showinfo("Break Time!", "The class's attention has been dropping--it may be time for a break.")

    def checkBreakTime(self):
        if (len(self.attention)>5):
            lastFiveMins=self.attention[len(self.attention)-5:len(self.attention)]
            a=np.array(lastFiveMins)
            mean=np.mean(a)
            if(mean<50):
                return True
        return False

    def addKeyword(self):
        text=self.enterKeywordsText.get()
        if(text!="" and not self.running):
            self.keywords.append(text)
            self.keywordsList.insert(END, text)
            self.enterKeywordsText.delete(0,END)
            self.enterKeywordsText.insert(0,"")
            self.addRelevantWords(text)

    def findQuestions(self):
        questionWords = ['what', 'how', 'why', 'when', 'who', 'where']
        questionList = []
        index=0
        relevanceWords=self.highRelevantWords+self.medRelevantWords+self.lowRelevantWords
        recentChat=[]
        for chat in self.chat:
            timeSincePosted = ((self.timePassed) - chat["timestamp"])/60 
            if timeSincePosted <= 1:
                recentChat+=[chat]
        for chat in recentChat:
            line = chat["chat"]
            text = line.lower()
            text = text.split(' ')
            for qWord in questionWords:
                if qWord in text:
                    timeSincePosted = ((self.timePassed) - chat["timestamp"])/30
                    upvotes=0
                    for word in text:
                        relevanceScore = 0
                        if word in dict(relevanceWords):
                            relevanceScore=dict(relevanceWords)[word]
                    for i in range(5):
                        if index+i+1<len(self.chat) and '^' in self.chat[index+i+1]["chat"]:
                            upvotes += 1
                        else:
                            break
                    priority = upvotes + relevanceScore + timeSincePosted
                    questionList.append((text, priority))
            index+=1
        return questionList

    def addRelevantWords(self, query):
        q = query.replace(' ', '%20')
        URL = 'https://relatedwords.org/relatedto/' + q
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find(id = "preloadedDataEl")

        results = str(results)
        startIndex = (str(results)).find("[{")
        endIndex = (str(results)).find('}</script>')
        results = results[startIndex:endIndex]
        relevantWords = []
        lessRelevant = []
        medRelevant = []
        highRelevant = []
        results = results.split('},')
        print(results)

        for term in results:
            endIndexTerm = term.find(",")
            word = term[9:endIndexTerm-1]
            scoreStartIndex = term.find('score":')
            scoreEndIndex = term.find(",'")
            score = (term[scoreStartIndex + 7 : scoreStartIndex + 10])
            if score == '' or score == '0.':
                score = '0'
            scoreFloat = float(score)
            if scoreFloat < 0:
                break
            relevantWords.append((word.lower(), scoreFloat))
        for (word, score) in relevantWords:
            if score < 0.5:
                lessRelevant.append((word, score))
            elif score < 1:
                medRelevant.append((word, score))
            else:
                highRelevant.append((word, score))
        
        self.highRelevantWords+=[(query.lower(), 30)]
        self.highRelevantWords+=highRelevant
        self.medRelevantWords+=medRelevant
        self.lowRelevantWords+=lessRelevant

        print(f"HIGH RELEVANCE: {self.highRelevantWords}")

    def detectRelevance(self, data):
        highestRelevance = 0
        for word in data:
            for (kw,rel1) in self.highRelevantWords:
                if word == kw or self.similarityInd(kw,word) > 0.8:
                    if rel1 > highestRelevance:
                        highestRelevance = rel1
            if highestRelevance > 0:
                return highestRelevance
            for (kw,rel2) in self.medRelevantWords:
                if word == kw or self.similarityInd(kw,word) > 0.8:
                    if rel2 > highestRelevance:
                        highestRelevance = rel2
            if highestRelevance > 0:
                return highestRelevance
            for (kw,rel3) in self.lowRelevantWords:
                if word == kw or self.similarityInd(kw,word) > 0.8:
                    if rel3 > highestRelevance:
                        highestRelevance = rel3
        #if the score is 0, tries to check if its a response or opinion
        if highestRelevance == 0:
            highestRelevance = self.opinionWords(data)
        return highestRelevance

    def opinionWords(self, data):
        opinionList = ["think", "believe", "Yes", "Not Sure", "No", "I agree", "What I mean is", "Exactly", "disagree", "suppose"]
        for words in opinionList:
            if words.lower() in data.lower():
                return 0.5
        return 0

    def similarityInd(self, word1,word2):
        removeChars = "?!@#$%A^&()-+"
        for chars in removeChars:
            if chars in word2:
                word2.replace(chars,'')
        if len(word1) > 6:
            ratio = self.similar(word1,word2)
            return ratio
        return 0
    
    def similar(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def getNewAttentionVal(self):
        rawVals = []
        if(len(self.chat)==0): return 0.5
        print("CHAT: "+str(self.chat))
        for line in self.chat:
            timeSincePosted = ((self.timePassed) - line["timestamp"])/60 
            if timeSincePosted <= 1:
                if len(line["chat"]) == 0:
                    rawVals.append(0.5)
                else:
                    score = self.detectRelevance(line["chat"])
                    rawVals.append(score)
        temp = np.array(rawVals)
        return np.mean(temp)

    def updateAttentionGraph(self,val):
        print("graph")

    def getMostEngagedStudents(self):
        #finds the keyword relevance (the highest ones)
        for chat in self.chat:
            line = chat["chat"]
            timeSincePosted = ((self.timePassed) - line["timestamp"])/60 
            if timeSincePosted <= 1:
                line = chat["chat"] 
                if len(line["chat"]) != 0:
                    score = self.detectRelevance(line["chat"])
                    for key in self.engagedStudents:
                        if key == chat["name"]:
                            #updating the score of students
                            self.engagedStudents[key] = self.engagedStudents.get(key,0)+(10*score)
                            #sorting in reverse order
                            self.engagedStudents = {k: v for k, v in sorted(self.engagedStudents.items(), key=lambda item: item[1], reverse = True)}

    def updateMostEngagedStudentsList(self,students):
        print("list")

app = ZoomChatApp()
