#!/usr/bin/python
import os.path
import sys
import time
import email.parser
import multiprocessing
import traceback
import nltk
import argparse
import datetime
import Queue
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
from message_decorator import MessageDecorator
from neo4j_loader import neo4jLoader
from word_counter import wordCounter
from cStringIO import StringIO
from time import strptime

args = {}

def parser_worker(fileQ, loaderQ, args):
    parser = email.parser.Parser()
    counter = wordCounter(word_types=args.word_types, subject_only=args.words_subject_only, words_per_message=args.words_max_per_message, debug=args.verbose)

    while True:
        fileName = fileQ.get()
        if args.verbose and fileName is not None:
            print "PARSING: " + fileName
        if fileName is None:
            fileQ.task_done()
            break
        
        rootLen = len(args.depot_dir)
        if fileName[rootLen] == '/' or fileName[rootLen] == '\\':
            rootLen += 1
        
        try:
            eFile, eExt = os.path.splitext(fileName[rootLen:])
            if eExt.lower() == '.pdf':
                email_msg = MessageDecorator(from_pdf(fileName))
            else:
                email_msg = MessageDecorator.from_file(fileName)
                
            if len(email_msg.message._headers) > 0:
                t = email_msg.message._headers[0]
                if t[1] == 'VCARD':
                    "vcard - skip"
                elif t[1] == 'VCALENDAR':
                    "vcalendar - skip"
                else:
                    #email_msg.word_counts=counter.common_word_counts(email_msg)
                    loaderQ.put( (email_msg.message, eFile) )

        except Exception, e:
            print e
            traceback.print_exc()
            pass
        
        fileQ.task_done()
            
    loaderQ.put(None)
    return

def from_pdf(pdfFile):
    try:
        pagenos = set()
        strfp = StringIO()
        codec = 'utf-8'
        
        laparams = LAParams()
        #laparams.char_margin = 10
        laparams.line_margin = 20
        #laparams.word_margin = 10
        laparams.boxes_flow = -1
        
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, strfp, codec=codec, laparams=laparams)
        
        fp = file(pdfFile, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos, check_extractable=True):
            interpreter.process_page(page)
    except Exception, e:
        print e
        traceback.print_exc()
        pass
        
    email_txt = strfp.getvalue()
    strfp.close()
    fp.close()
    device.close()
    
    keys = ['From', 'Sent', 'To', 'Cc', 'Bcc', 'Bee', 'Subject']
    lines = email_txt.splitlines(True)
    email_out = ''
    bmerge_lines = False
    last_line = None
    in_body = False
    for line in lines:
        if in_body:
            email_out += line
            continue
        
        values = line.split(':', 1)

        if bmerge_lines:
            bmerge_lines = False
            if not values[0] in keys:
                email_out += line.strip() + '\n'
                continue
            else:
                email_out += '\n'
                          
        if values[0] in keys:
            if values[0] == 'Sent':
                values[0] = 'Date'
            elif values[0] == 'Bee':
                values[0] = 'Bcc'
            elif values[0] == 'Subject':
                in_body = True
                
            if len(values[1].strip()) > 0:
                email_out += values[0] + ': ' + values[1].strip() + '\n'
            elif not last_line is None:
                email_out += values[0] + ': ' + last_line
                last_line = None
            else:
                email_out += values[0] + ': '
                bmerge_lines = True
        else:
            last_line = line
                  
    email_msg = email.parser.Parser().parsestr(email_out, headersonly=False)
    
    return email_msg

def traverse_dir(folder):
    for root,dirs,files in os.walk(folder):
        if args.verbose:
            loader.msg("Examining folder: " + root)
        for name in files:
            yield (os.path.join(root, name))
    return

def service_loader_q(loaderQ, block, numRunning):
    try:
        while numRunning > 0:
            if (block):
                item = loaderQ.get()
            else: 
                item = loaderQ.get_nowait()

            if item == None:
                numRunning = numRunning - 1
            else:
                if args.verbose:
                    print "ADDING: " + item[1]
                loader.add(item[0], item[1])
    except Exception,e:
        pass

    return numRunning


def process_args():
    parser = argparse.ArgumentParser(description='Load emails into Minezy')
    parser.add_argument('-c', '--complete', default=False, help="Run only the completion step")
    parser.add_argument('-d', '--depot_dir', required=True,
                       help="The [depot_dir] parameter should point to a parent folder of a parsed PST dump (eg: as generated by <a href='http://www.five-ten-sg.com/libpst/rn01re01.html'>readpst</a> tool)")
    parser.add_argument('-n', '--depot_name',  default="Un-named", help='Name of the account')
    parser.add_argument('-p', '--processes', default=8, type=int, help="Number of parallel processes to use to parse emails ")
    parser.add_argument('-v', '--verbose', nargs='?', const=True, default=False, type=bool, help="Print additional progress output")
    loader_opts = neo4jLoader.options()
    parser.add_argument('-l', '--load_options', nargs='*', choices=loader_opts, default=loader_opts, help="Select which email elements to load.")
    parser.add_argument('-s', '--sample', default=1, type=int, help="Use every n-th email from the depot (used for debugging).")
    word_types = wordCounter.word_types()
    parser.add_argument('-w', '--word_types', nargs='*', choices=word_types, default=word_types, help="Select which types of words to count.")
    parser.add_argument('-m', '--words_max_per_message', default=-1, type=int, help="How many word counts to save from each email message. (-1 for all)")
    parser.add_argument('-j', '--words_subject_only', nargs='?', const=True, default=False, type=bool, help="Only scan email subject for word counts")

    global args
    args = parser.parse_args()

def num_files_in_dir(dir):
    numFiles = 0
    for fileName in traverse_dir(args.depot_dir):
        numFiles = numFiles + 1
    return numFiles

def process_dir(dir, loader, numProcs):
    numRunning = numProcs

    # using multiprocessing and generator 'traverse_dir' to speed things up
    fileQ = multiprocessing.JoinableQueue(1000)
    loaderQ = multiprocessing.Queue(1000*numProcs)
    
    procs = []
    for i in range(numProcs):
        p = multiprocessing.Process(target=parser_worker, args=(fileQ,loaderQ, args))
        procs.append(p)
        p.start()
    
    numFiles = num_files_in_dir(args.depot_dir)
    fileNum = 0
    for fileName in traverse_dir(args.depot_dir):
        if (fileNum % args.sample) != 0:
            fileNum = fileNum + 1
            continue

        while True:
            try:
                fileQ.put(fileName, True, 1)
                fileNum = fileNum + 1
                if args.verbose:
                    print "QUEUED: " + str(fileNum) + " of " + str(numFiles)
                break
            except Queue.Full:
                numRunning = service_loader_q(loaderQ, False, numRunning)
            except Exception,e:
                print e
                numRunning = service_loader_q(loaderQ, False, numRunning)

    for i in range(len(procs)):
        fileQ.put(None)

    service_loader_q(loaderQ, True, numRunning)
    fileQ.join()

if __name__ == '__main__':
    t0 = time.time()
    process_args();

    account = args.depot_dir.replace("\\", "/").replace("//", "/")
    loader = neo4jLoader(account, args.load_options, args.depot_name, args.verbose)
        
    if not args.complete:
        process_dir(args.depot_dir, loader, args.processes)

    loader.complete()
    t1 = time.time()
    
    print "All Done ("+str(t1-t0) + " seconds)"
    
    