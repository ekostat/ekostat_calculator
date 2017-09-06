# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 09:06:21 2017

@author: a001985
"""
import codecs

"""
========================================================================
========================================================================
========================================================================
"""
class TextColumnFile(object):
    
    #=========================================================================
    def __init__(self, mode='r'):
        self.mode = mode
        
        
    #=========================================================================
    def write_dict(self, file_path, data, header=None, delimiter=u'\t', encoding='cp1252', missing_value=u''):
        """
        Method to write dict to txt file. 
        """
        assert self.mode=='w', u'TextColumnFile: mode is not set to write'
        
        self.file_path = file_path
        self.data = data
        self.delimiter = delimiter
        self.encoding = encoding
        self.missing_value = missing_value
        
        if not header:
            self.header = sorted(self.data.keys())
        else:
            self.header = header
            
        # Find longest list
        nr_lines = 0
        for key in self.header:
            list_len = len(self.data[key])
            if list_len > nr_lines:
                nr_lines = list_len
            
        fid = codecs.open(file_path, 'w', encoding=encoding)
        fid.write(delimiter.join(self.header))
        fid.write(u'\n')
        for k in range(nr_lines):
            line_list = []
            for item in self.header:
                try:
                    line_list.append(self.data[item][k])
                except:
                    line_list.append(self.missing_value)
            fid.write(delimiter.join(line_list))
            fid.write(u'\n')
        fid.close()
        
    
    #=========================================================================
    def read(self, file_path, 
                 header_row=0,
                 delimiter=u'\t', 
                 encoding=None, 
                 remove_blanks=False, 
                 remove_blanks_at_the_end=False, 
                 has_header=True):
        """
        Method to read txt file. Data is stored in a dict (self.data). 
        Header list is under self.header
        """
        assert self.mode=='r', u'TextColumnFile: mode is not set to read'
        self.file_path = file_path
        self.header_row = header_row
        self.encoding = encoding
        self.has_header = has_header
        
        # Dynamic check of encoding. Not sure it fully works
        if not self.encoding:
            self.encoding = self._check_encoding_cp1252()
        if not self.encoding:
            self.encoding = self._check_encoding_utf8()
        if not self.encoding:
            self.encoding = self._check_encoding_cp437()
            
        fid = codecs.open(self.file_path, 'r', encoding=self.encoding)
        
        for row_nr, line in enumerate(fid):
#             line = line.strip()
            if not line.strip():
                continue
            line = line.strip(u'\n\r ')
            line = line.strip(u'\n')
            if line:
                split_line = line.split(delimiter)
                if row_nr < self.header_row:
                    pass
                elif row_nr == self.header_row:
                    self.header = [item.strip() for item in split_line]
#                     if self.has_header: # All columns should have header. 
#                         self.header = [item.strip() for item in line.strip().split(delimiter)]
#                     else:
#                         self.header = [item.strip() for item in split_line]
                    self.data = dict((h, []) for h in self.header)
                else:
#                     print len(split_line)
                    for col_nr, value in enumerate(split_line):
#                     for col_nr in range(len(self.header)):
#                         value = split_line[col_nr]
                        if remove_blanks and not value.strip():
                            continue
                        self.data[self.header[col_nr]].append(value.strip())
        fid.close()
        
        if remove_blanks_at_the_end:
            [self.data[key].reverse() for key in self.data]
            for key in self.data:
                for i, value in enumerate(self.data):
                    if value:
                        break
                self.data[key] = self.data[key][i:]
                
            [self.data[key].reverse() for key in self.data]
                
                
        
        if not self.has_header:
            for item in self.header:
                # Add header at the top of data
                self.data[item] = [item] + self.data[item]
        

    #=========================================================================  
    def _check_encoding_utf8(self):
        
        try:
            f = codecs.open(self.file_path, encoding='utf-8', errors='strict')
            for line in f:
                pass
            f.close()
            return 'utf-8'
        except UnicodeDecodeError:
            f.close()
            return None
    
    #=========================================================================  
    def _check_encoding_cp437(self):
        
        try:
            f = codecs.open(self.file_path, encoding='cp437', errors='strict')
            for line in f:
                pass
            f.close()
            return 'cp437'
        except UnicodeDecodeError:
            f.close()
            return None
    
    #=========================================================================  
    def _check_encoding_cp1252(self):
        
        try:
            f = codecs.open(self.file_path, encoding='cp1252', errors='strict')
            for line in f:
                pass
            f.close()
            return 'cp1252'
        except UnicodeDecodeError:
            f.close()
            return None