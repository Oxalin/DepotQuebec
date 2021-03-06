#!/usr/bin/env python3
# -*- coding: cp1252 -*-
# *  Modification by CB (2016)

# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

""" addons.xml generator """

import os
import sys
import zipfile
import md5
import re
baseP = os.path.dirname(os.path.abspath(__file__))+"/"

# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

class Generator:
    addons_xml=""
    
    def __init__( self ):
        # generate files
        # final addons text
        print "RECHERCHE DE FICHIERS .ZIP"
        print "--------------------------"
        self.addons_xml = u("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n")
        self._generate_addons_file(baseP)
        print "--------------------------"
        
        # clean and add closing tag
        self.addons_xml = self.addons_xml.strip() + u("\n</addons>\n")
        # save file
        print "Sauvegarde du nouveau addon.xml"
        self._save_file( self.addons_xml.encode( "UTF-8" ), file=baseP+"/addons.xml" )


             
        self._generate_md5_file(baseP+"addons.xml")
        # notify user
        print("Finished updating addons xml and md5 files")
    
    def _generate_addons_file( self , basePath ):
        # addon list
        addons = os.listdir( basePath+"." )
        most_recent_file = ""
        versionMostRecent = self.getVersion("")
        #print addons

        # loop thru and add each addons addon.xml file
        for addon in addons:
            fullPath = basePath + addon
            #print fullPath
            _path=""
            #try:
            # skip any file or .svn folder or .git folder
            if (fullPath.endswith(".zip")):
                #print "ZIP FILE : " + fullPath
                self._generate_md5_file(fullPath)
                thisVersion = self.getVersion(fullPath)
                if (self.isRecent(thisVersion, versionMostRecent)):
                    versionMostRecent = thisVersion
                    most_recent_file = fullPath

            elif ( not os.path.isdir(fullPath ) or addon == ".svn" or addon == ".git" ):
               # print "Je rejete " + addon
               pass
            elif (os.path.isdir(fullPath)):
               # print fullPath + " Est un path"
                self._generate_addons_file(fullPath+"/")

            #except Exception as e:
                # missing or poorly formatted addon.xml
                #print("Excluding %s for %s" % ( _path, e ))
                #pass
        if (most_recent_file != ""):
            self.scanZip(most_recent_file)

    def scanZip(self,path):
        print "---"
        print "   --Most recent : " + path
        print "---"
        zf = zipfile.ZipFile(path)
        datas = zf.infolist()
        #print datas
        for data in datas:
            filen = data.filename
            if (filen.endswith("/addon.xml")):
                self.__addToAddonXML(zf.open(data))
            elif (filen.endswith("/icon.png")):
                zf.extract(data)
            elif (filen.endswith("/fanart.jpg")):
                zf.extract(data)
            elif (filen.endswith("/changelog.txt")):
                zf.extract(data)
    def getVersion(self,filename):
        try:
            versionStr= filename[filename.rfind('-')+1:filename.rfind('.')]
            m = re.match('(?P<_0>.+)\.(?P<_1>.+)\.(?P<_2>.+)', versionStr)
            mdict = m.groupdict()
            return [mdict['_0'],mdict['_1'],mdict['_2']]

        except Exception:
            return ['0','0','0']
    def isRecent(self, thisVersion, versionMostRecent):
        return (versionMostRecent[0] < thisVersion[0] or \
                    (versionMostRecent[0] == thisVersion[0] and versionMostRecent[1] < thisVersion[1]) or \
                    (versionMostRecent[0] == thisVersion[0] and versionMostRecent[1] == thisVersion[1] and versionMostRecent[2] < thisVersion[2])) 

    def __addToAddonXML(self, data):
        xml_lines = data.read().splitlines()
        # new addon
        addon_xml = ""
        # loop thru cleaning each line
        for line in xml_lines:
            # skip encoding format line
            if ( line.find( "<?xml" ) >= 0 ): continue
            # add line
            if sys.version < '3':
                addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )
            else:
                addon_xml += line.rstrip() + "\n"
        # we succeeded so add to our final addons.xml text
        self.addons_xml += addon_xml.rstrip() + "\n\n"
        
    
    def _generate_md5_file( self,filename ):
        # create a new md5 hash
        try:
                       
            m = md5.new( open( filename, "r" ).read() ).hexdigest()
            print "MD5 of " + filename + " : " + m
        except ImportError:
            import hashlib
            m = hashlib.md5( open( filename, "r", encoding="UTF-8" ).read().encode( "UTF-8" ) ).hexdigest()
        
        # save file
        try:
            self._save_file( m.encode( "UTF-8" ), file=filename+".md5" )
        except Exception as e:
            # oops
            print("An error occurred creating " + filename + ".md5 file!\n%s" % e)
    
    def _save_file( self, data, file ):
        try:
            # write data to the file (use b for Python 3)
            open( file, "wb" ).write( data )
        except Exception as e:
            # oops
            print("An error occurred saving %s file!\n%s" % ( file, e ))


if ( __name__ == "__main__" ):
    # start
    Generator()
