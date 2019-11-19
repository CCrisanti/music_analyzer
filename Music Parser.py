#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xml.etree.ElementTree as ET
tree = ET.parse( "SimpleGifts.mscx" )
root = tree.getroot()


# In[12]:

class Instrument:
    def __init__( self ):
        self.id = None
        self.name = None
        self.measures = []
    
    def __str__( self ):
        return str(self.id) + ": " + self.name

class Measure:
    def __init__( self ):
        self.chords = []
        #print( "Created new measure." )
                
    def __str__( self ):
        if ( len( self.chords ) != 0):
            return_string = ""
            for i in self.chords:
                return_string += str(i) + "\n"
                
            return_string += "End measure"
        else:
            return_string = "Empty measure"
        return return_string
    
class Chord:
    def __init__( self ):
        self.duration = None
        self.notes = []
        #print( "Created new chord." )
    
    def __str__( self ):
        return_string = "Chord with duration of " + self.duration + "\n"
        for i in self.notes:
            return_string += str(i)
        return return_string
    
class Note:
    def __init__( self ):
        self.pitch = None
        self.tpc = None
        self.chromaticNote = None
        #print(" Created new note." )
        
    def __str__( self ):
        return_string = "Note with pitch of " + self.pitch + " and TPC of " + self.tpc + " and chromatic note of " + self.chromaticNote
        return return_string


# In[13]:

tpcToLetter = ["Fbb", "Cbb", "Gbb", "Dbb", "Abb", "Ebb", "Bbb", "Fb", "Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "E#", "B#","F##", "C##", "G##", "D##", "A##", "E##", "B##",]

measures = []
print(list(root))
#for child in root:
#    print (child.tag, child.attrib)
score = root[2]
instruments = []
currId = -1
#print(list(score))
for staff in score:
    if( staff.tag == "Part" ):
        for instrument in staff:
            if( instrument.tag == "Staff" ):
                instruments.append(Instrument())
                currId = int(instrument.attrib["id"])
                instruments[currId-1].id = currId
            if( instrument.tag == "trackName" ):
                instruments[(currId-1)].name = (instrument.text)
            

    #print (staff.tag, staff.attrib)
    if( staff.tag == "Staff" ):
        current_measure = -1
        currId = int(staff.attrib['id'])-1
        for measure in staff:
            current_measure += 1
            current_chord = -1
            instruments[currId].measures.append(Measure())
            #print( "\t", measure.tag, measure.attrib )
            nv = 1
            
            for voice in measure:
                nv += 1
                #print( "\t\t", voice.tag, voice.attrib )
                
                for child in voice:
                    is_chord = False
                    
                    if( child.tag == "Chord" ):
                        current_chord += 1
                        current_note = -1
                        is_chord = True
                        instruments[currId].measures[ current_measure ].chords.append(Chord())
                    #print( "\t\t\t", child.tag, child.attrib )
                    
                    for gchild in child:
                        is_note = False
                        if ( is_chord ):
                            if( gchild.tag == "durationType" ):
                                instruments[currId].measures[ current_measure ].chords[ current_chord ].duration = gchild.text
                            elif ( gchild.tag == "Note" ):
                                instruments[currId].measures[ current_measure ].chords[ current_chord ].notes.append(Note())
                                is_note = True
                                current_note += 1
                                
                        #print( "\t\t\t\t", gchild.tag, gchild.attrib, gchild.text )
                        for ggchild in gchild:
                            if ( is_note ):
                                if( ggchild.tag == "pitch" ):
                                    instruments[currId].measures[
                                        current_measure ].chords[
                                        current_chord ].notes[
                                        current_note ].pitch = ggchild.text
                                elif (ggchild.tag == "tpc" ):
                                    instruments[currId].measures[
                                        current_measure ].chords[
                                        current_chord ].notes[
                                        current_note ].tpc = ggchild.text
                                    instruments[currId].measures[
                                        current_measure ].chords[
                                        current_chord ].notes[
                                        current_note ].chromaticNote = tpcToLetter[int(ggchild.text)+1]
            
                            #print( "\t\t\t\t\t", ggchild.tag, ggchild.attrib, ggchild.text )
                            
        #print( "End Staff" ) 


# In[14]:
print(len(measures), "measures")
#for i in measures:
#    print(i)
for instrument in instruments:
    print(instrument)
    for measure in instrument.measures:
        print(measure)

