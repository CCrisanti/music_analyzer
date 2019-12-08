#!/usr/bin/env python
# coding: utf-8

# In[1]:

import sys
import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[1])
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

# Rule 1: Avoid Tritone and seven semitone intervals over three notes
# This rule takes in the pitch two notes ago, a note ago, and the current note
# If the pitch difference between the two previous notes is less than 6 in one 
# direction and the difference in pitch between the previous and current note
# is 6, in the same direction, than a tritone has been formed over the interval
# Returns true if this rule is violated
def rule1(prev_prev_pitch, prev_pitch, cur_pitch):
    if prev_prev_pitch - prev_pitch > 0 and prev_prev_pitch - prev_pitch > 6:
        return prev_prev_pitch - cur_pitch == 6
    if prev_prev_pitch - prev_pitch < 0 and prev_prev_pitch - prev_pitch > -6:
        return prev_prev_pitch - cur_pitch == -6        

# Rule 2: Check if notes follow allowed intervals
# This rule takes in the pitch two notes ago, a note ago, and the current note
# First we check if the interval between the two previous notes is acceptable
# Then we check if the interval of the previous two notes is an ascending minor sixth.
# If it is, we check if the following note is downward motion.
# If this rule is violated, return True
def rule2(prev_prev_pitch, prev_pitch, cur_pitch):
    diff = abs(prev_prev_pitch - prev_pitch)
    if  diff == 6 or diff == 9 or diff == 10 or diff == 11 or diff > 12 or (prev_prev_pitch - prev_pitch) == 8:
        return True
    elif (prev_prev_pitch - prev_pitch) == -8:
        if cur_pitch is not None:
            return cur_pitch > prev_pitch
    return False

# Rule 3: Check if consectutive skips are in opposite directions
# This rule takes in the pitch two notes ago, a note ago, and the current note
# Checks is the difference between the two previous notes and the difference between 
# the current not and the previous note are both greater than two or both
# less than -2.
# If this rule is violated, return True
def rule3(prev_prev_pitch, prev_pitch, cur_pitch):
    if prev_prev_pitch - prev_pitch > 2 and prev_pitch - cur_pitch > 2:
        return True
    elif prev_prev_pitch - prev_pitch < -2 and prev_pitch - cur_pitch < -2:
        return True
    return False

# Rule 4: Rule for dealing with two skips in a row
# This rule takes in the pitch two notes ago, a note ago, and the current note
# Checks if the difference between the two previous notes is less than the 
# current and previous note. Next, check if the note two notes ago is disonant
# to the current note. Finally, check if the three notes form a triad.
# If this rule is violated, return True
def rule4(prev_prev_pitch, prev_pitch, cur_pitch):
    if rule3(prev_prev_pitch, prev_pitch, cur_pitch):
        ppp_dif = abs(prev_prev_pitch - prev_pitch) 
        pc_dif = abs(prev_pitch - cur_pitch)
        ppc_dif = abs(prev_prev_pitch - cur_pitch)
        if ppp_dif < pc_dif:
            return True
        if ppc_dif == 1 or ppc_dif == 2 or ppc_dif == 10 or ppc_dif == 11 or ppc_dif == 13 or ppc_dif == 13:
            return True
        if (ppp_dif != 3 and ppp_dif != 4) or (pc_dif != 3 and pc_dif != 4):
            return True
    return False

# Should be called once for beginning notes and once for last notes 
def rule5(notes):
    rest=[]
    consecutive_notes = False
    for note1 in range(len(notes)):
        for note2 in range(note1, len(notes)):
            if notes[note1] != rest and notes[note2] != rest:
                consecutive_notes = True
                dif = abs(notes[note1] - notes[note2])
                if dif == 0 or dif == 5 or dif == 7 or dif == 12:
                    return False
    return consecutive_notes

# Contrary motion should be the norm
# This checks a single example, perhaps we loop it for the entire song, and see if it is followed most of the time?
def rule6(prev_pitch_one, cur_pitch_one,prev_pitch_two, cur_pitch_two):
    interval = abs(cur_pitch_one - cur_pitch_two)
    prev_interval = abs(prev_pitch_one - prev_pitch_two)
          
    #If they approach or stay the same (in other words not apart)
    if interval <= prev_interval:
        return False
    
    return True

# Perfect consonances must be approached through oblique or contrary motion
# This needs to examine two staffs
def rule7(prev_prev_pitch_one, prev_pitch_one, cur_pitch_one, prev_prev_pitch_two, prev_pitch_two, cur_pitch_two):
    perfect_fifth = 7
    perfect_octave = 12
    interval = abs(cur_pitch_one - cur_pitch_two)
    if interval == perfect_fifth or interval == perfect_octave:
          prev_interval = abs(prev_pitch_one - prev_pitch_two)
          prev_prev_interval = abs(prev_prev_pitch_one - prev_prev_pitch_two)
          
          #If they approach or stay the same (in other words not apart)
          if prev_interval <= prev_prev_interval:
              return False
    return True
        
# Avoid intervals of ten
def rule9(pre_pitch, cur_pitch):
    #15 half steps is a minor tenth, 16 half steps is a major tenth
    major_tenth = 15
    minor_tenth = 16
    interval = abs(prev_pitch - cur_pitch)
    if interval == major_tenth or interval == minor_tenth:
        return True
    return False
            

# In[13]:

tpcToLetter = ["Fbb", "Cbb", "Gbb", "Dbb", "Abb", "Ebb", "Bbb", "Fb", "Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "E#", "B#","F##", "C##", "G##", "D##", "A##", "E##", "B##",]

measures = []
#print(list(root))
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
instruments[0].measures.remove(instruments[0].measures[0])

# In[14]:
# print(len(instruments[0].measures), "measures")
# for i in measures:
#     print(i)

rule1Violations = 0
rule2Violations = 0
rule3Violations = 0
rule4Violations = 0
rule5Violations = 0
rule6Violations = 0
rule7Violations = 0
rule8Violations = 0
rule9Violations = 0


first_notes = []
last_notes = []
for instrument in instruments:
    #print(instrument)
    cur_pitch = None
    prev_pitch = None
    prev_prev_pitch = None
    
    #for display purposes
    cur_tpc = None
    prev_tpc = None
    prev_prev_tpc = None
    
    measureNum = 0
    for measure in instrument.measures:
        #print(measure)
        for chord in measure.chords:
            for note in chord.notes:
                if prev_pitch is not None:
                    prev_prev_pitch = int(prev_pitch)
                    prev_prev_tpc = int(prev_tpc)    
                    
                if cur_pitch is not None:
                    prev_pitch = int(cur_pitch)
                    prev_tpc = int(cur_tpc)
                    
                cur_pitch = int(note.pitch)
                cur_tpc = int(note.tpc)
            if prev_prev_pitch is not None:
                if rule1(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule1Violations += 1
                    print("Rule 1 Violation by", instrument.name ,"at measure", measureNum)
                    print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1],'\n')
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule2(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule2Violations +=1
                    print("Rule 2 Violation by", instrument.name ,"at measure", measureNum)
                    print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1],'\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule3(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule3Violations +=1
                    print("Rule 3 Violation by", instrument.name ,"at measure", measureNum)
                    print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule4(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule4Violations +=1
                    print("Rule 4 Violation by", instrument.name ,"at measure", measureNum)
                    print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule9(prev_prev_pitch, prev_pitch):
                    rule9Violations +=1
                    print("Rule 9 Violation by", instrument.name ,"at measure", measureNum)
                    print("Note sequence:", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
        
        measureNum+=1            #print("prev_pitch:", prev_pitch)
    if prev_pitch is not None and cur_pitch is not None:
        if rule2(prev_pitch, cur_pitch, None):
            rule2Violations +=1
            print("Rule 2 Violation by", instrument.name ,"at measure", measureNum)
            print("Note sequence:", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
            #print("prev_prev_pitch:", prev_prev_pitch)
            #print("prev_pitch:", prev_pitch)
            #print("cur_pitch:", cur_pitch)
        if rule9(prev_pitch, cur_pitch):
            rule9Violations +=1
            print("Rule 9 Violation by", instrument.name ,"at measure", measureNum)
            print("Note sequence:", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
            #print("prev_pitch:", prev_pitch)
            #print("cur_pitch:", cur_pitch)
    first_note = instrument.measures[0].chords
    last_note = instrument.measures[len(instrument.measures)-1].chords

    if first_note != []:
        first_notes.append(int(first_note[0].notes[0].pitch))
    else:
        first_notes.append([])
    
    if last_note != []:
        last_notes.append(int(last_note[len(last_note)-1].notes[0].pitch))

# for instr1 in range(len(instruments)):
#     for instr2 in range(instr1,len(instruments)):
#         instr1_cur_pitch = None
#         instr1_prev_pitch = None
#         instr1_loc = 0

#         instr2_cur_pitch = None
#         instr2_prev_pitch = None
#         instr2_loc = 0

#         currMeasure1 = []
#         currMeasure2 = [] 
#         for measure in range(len(instruments[0].measures)):
#             if instruments[instr1].measures[measure]
#             for chord in instruments[instr1].measures[measure].chords:
#                 print(chord)


if rule5(first_notes):
    rule5Violations+=1
if rule5(last_notes):
    rule5Violations+=1

print("Rule 1 Violations:", rule1Violations)
print("Rule 2 Violations:",rule2Violations)
print("Rule 3 Violations:",rule3Violations)
print("Rule 4 Violations:",rule4Violations)
print("Rule 5 Violations:",rule5Violations)
#print("Rule 9 Violations:",rule9Violations)
