#!/usr/bin/env python
# coding: utf-8

# In[1]:

import sys
import xml.etree.ElementTree as ET
from scipy.special import comb
tree = ET.parse(sys.argv[1])
root = tree.getroot()
verbose=int(sys.argv[2])

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
    def __init__( self, isRest=False):
        self.duration = None
        self.notes = []
        self.isRest = isRest
        #print( "Created new chord." )
    
    def __str__( self ):
        return_string = "Chord with duration of " + self.duration + "\n"
        for i in self.notes:
            return_string += str(i)
        if self.notes == [] :
            return_string += "this is a rest"
        return return_string
    
    def getDuration( self ) :
        if self.duration == "quarter" :
            return 0.25
        elif self.duration == "half" :
            return 0.5
        elif self.duration == "whole" or "measure":
            return 1
        else :
            print( "duration of", self.duration )
    
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

# Must define what a rest is later
# Should be called once for beginning notes and once for last notes 
def rule5(notes):
    rest=[] #DEFINE LATER
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
def rule8(pre_pitch, cur_pitch):
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
rule6Evaluations = 0
rule7Violations = 0
rule8Violations = 0
rule8Violations = 0


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
                    if verbose:
                        print("Rule 1 Violation by", instrument.name ,"at measure", measureNum)
                        print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1],'\n')
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule2(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule2Violations +=1
                    if verbose:
                        print("Rule 2 Violation by", instrument.name ,"at measure", measureNum)
                        print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1],'\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule3(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule3Violations +=1
                    if verbose:
                        print("Rule 3 Violation by", instrument.name ,"at measure", measureNum)
                        print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule4(prev_prev_pitch, prev_pitch, cur_pitch):
                    rule4Violations +=1
                    if verbose:
                        print("Rule 4 Violation by", instrument.name ,"at measure", measureNum)
                        print("Note sequence:", tpcToLetter[prev_prev_tpc+1], ",", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
                    #print("prev_pitch:", prev_pitch)
                    #print("cur_pitch:", cur_pitch)
                if rule8(prev_prev_pitch, prev_pitch):
                    rule8Violations +=1
                    if verbose:
                        print("Rule 9 Violation by", instrument.name ,"at measure", measureNum)
                        print("Note sequence:", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
                    #print("prev_prev_pitch:", prev_prev_pitch)
        
        measureNum+=1            #print("prev_pitch:", prev_pitch)
    if prev_pitch is not None and cur_pitch is not None:
        if rule2(prev_pitch, cur_pitch, None):
            rule2Violations +=1
            if verbose:
                print("Rule 2 Violation by", instrument.name ,"at measure", measureNum)
                print("Note sequence:", tpcToLetter[prev_tpc+1], ",", tpcToLetter[cur_tpc+1], '\n')                    
            #print("prev_prev_pitch:", prev_prev_pitch)
            #print("prev_pitch:", prev_pitch)
            #print("cur_pitch:", cur_pitch)
        if rule8(prev_pitch, cur_pitch):
            rule8Violations +=1
            if verbose:
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
                    
                    if( child.tag == "Chord" or child.tag == "Rest" ):
                        current_chord += 1
                        current_note = -1
                        is_chord = True
                        is_rest = False
                        if child.tag == "Rest" :
                            is_rest = True
                        instruments[currId].measures[ current_measure ].chords.append(Chord(is_rest))
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
#print(len(instruments[0].measures), "measures")
for i in instruments:
    for j in range(len(i.measures)):
        for k in range(len(i.measures[j].chords)):
            #print(i.measures[j].chords[k])
            pass
                  
            
for instrument_1 in instruments:
    for instrument_2 in instruments:
        if(instrument_2.id > instrument_1.id) :
            
            if verbose:
                print("Comparing", instrument_1, "with", instrument_2)

            i1_cur_pitch = None
            i1_prev_pitch = None
            i1_prev_prev_pitch = None

            #for display purposes
            i1_cur_tpc = None
            i1_prev_tpc = None
            i1_prev_prev_tpc = None

            
            i2_cur_pitch = None
            i2_prev_pitch = None
            i2_prev_prev_pitch = None

            #for display purposes
            i2_cur_tpc = None
            i2_prev_tpc = None
            i2_prev_prev_tpc = None
            
            
            i1_measureNum = 0
            i2_measureNum = 0
            i1_beat = 0
            i2_beat = 0
            
            #keep looping until one of the instruments runs out of measures
            while(i1_measureNum < len(instrument_1.measures) and i2_measureNum < len(instrument_2.measures)) :
                #print("started loop at measure", i1_measureNum, "for 1 and ", i2_measureNum, "for 2")
                #get all the chords for the measure we are looking at for each instrument
                i1_chords = instrument_1.measures[i1_measureNum].chords
                i2_chords = instrument_2.measures[i2_measureNum].chords
                
                
                #start looping through the chords 
                while i1_chords != [] and i2_chords != [] :
                    #print("started looping through chords")
                    #print("len of i1 chords", len(i1_chords))
                    #print("len of i2 chords", len(i2_chords))
                    #print("beat of i1", i1_beat, "beat of i2", i2_beat)
                    #remove rests but keep beat count
                    if i1_chords[0].isRest or i2_chords[0].isRest:
                        if i2_chords[0].isRest :
                            i2_beat += i2_chords[0].getDuration()
                            del i2_chords[0]
                        else :
                            i1_beat += i1_chords[0].getDuration()
                            del i1_chords[0]
                    
                    else :   
                        #if we are on the same beat we can start to examine pitches
                        if i1_beat == i2_beat :
                            #print("beats are the same")
                            if i1_prev_pitch is not None :
                                i1_prev_prev_pitch = int(i1_prev_pitch)
                                i1_prev_prev_tpc = int(i1_prev_tpc)

                            if i1_cur_pitch is not None :
                                i1_prev_pitch = int(i1_cur_pitch)
                                i1_prev_tpc = int(i1_cur_tpc)
                            
                            #print(i1_chords[0].notes[0])
                            i1_cur_pitch = int(i1_chords[0].notes[0].pitch)
                            i1_cur_tpc = int(i1_chords[0].notes[0].tpc)

                            if i2_prev_pitch is not None :
                                i2_prev_prev_pitch = int(i2_prev_pitch)
                                i2_prev_prev_tpc = int(i2_prev_tpc)

                            if i2_cur_pitch is not None :
                                i2_prev_pitch = int(i2_cur_pitch)
                                i2_prev_tpc = int(i2_cur_tpc)

                            i2_cur_pitch = int(i2_chords[0].notes[0].pitch)
                            i2_cur_tpc = int(i2_chords[0].notes[0].tpc)

                            #Here we can look at rules that need 3 notes from both instruments                            
                            if i1_prev_prev_pitch is not None and i2_prev_prev_pitch is not None:
                                if(rule7(i1_prev_prev_pitch, i1_prev_pitch, i1_cur_pitch, i2_prev_prev_pitch, i2_prev_pitch, i2_cur_pitch)) :
                                    rule7Violations += 1
                                    if verbose:
                                        print("Rule 7 Violation by", instrument_1.name, "and", instrument_2.name ,"at measure", i2_measureNum, "\n")
                             
                            #Here we can look at rules that need 2 notes from both instruments
                            if i1_prev_pitch is not None and i1_cur_pitch is not None and i2_prev_pitch is not None and i2_cur_pitch is not None:
                                rule6Evaluations+=1
                                if(rule6(i1_prev_pitch, i1_cur_pitch, i2_prev_pitch, i2_cur_pitch)) :
                                    rule6Violations += 1
                                    if verbose:
                                        print("Rule 6 Violation by", instrument_1.name, "and", instrument_2.name ,"at measure", i2_measureNum, "\n")
                            
                            #now we move the first instrument forwards
                            i1_beat += i1_chords[0].getDuration()
                            del i1_chords[0]
                        # if we are not on the same beat we need to advance to the next chord    
                        elif i1_beat < i2_beat :
                            #print("i1_beat is smaller")
                            i1_beat += i1_chords[0].getDuration()
                            del i1_chords[0]
                        elif i2_beat < i1_beat :
                            #print("i2_beat is smaller")
                            i2_beat += i2_chords[0].getDuration()
                            del i2_chords[0]
                        else:
                            print("We should not be here")
                            
                    #print("end of inner while")
                #end while
                
                #now we need to see which measure we have look at all the notes from
                #if i1_chords == [] :
                i1_measureNum += 1
                #if i2_chords == [] :
                i2_measureNum += 1
                 
                #print("End of loop")
rule6Severity = 0

if len(instruments)>1:
    rule6Violations=round((rule6Violations/comb(len(instruments), 2))) 
    rule6Severity = 1-rule6Violations/rule6Evaluations

print("Rule 1 Violations:",rule1Violations)
print("Rule 2 Violations:",rule2Violations)
print("Rule 3 Violations:",rule3Violations)
print("Rule 4 Violations:",rule4Violations)
if len(instruments)>1:
    print("Rule 5 Violations:",rule5Violations)
    if rule6Severity > .75:
        print("Rule 6 Violation Level: ", 0, ". " , round(rule6Severity*100,3), "% of time follows rule", sep="")
    elif rule6Severity > .5:
        print("Rule 6 Violation Level: ", 1, ". " , round(rule6Severity*100,3), "% of time follows rule", sep="")
    elif rule6Severity > .25:
        print("Rule 6 Violation Level: ", 2, ". " , round(rule6Severity*100,3), "% of time follows rule", sep="")
    else:
        print("Rule 6 Violation Level: ", 3, ". " , round(rule6Severity*100,3), "% of time follows rule", sep="")
    print("Rule 7 Violations:",rule7Violations)
else:
    print("Rules 5-7 don't apply. There is only one voice.")
print("Rule 8 Violations:",rule8Violations)

outfile = open("outFile.txt", 'a')
outfile.write(str(rule1Violations) + " " + str(rule2Violations) + " " + str(rule3Violations) + " " + str(rule4Violations) + " " + str(rule5Violations) + " " + str(rule6Severity*3) + " " + str(rule7Violations) + " " + str(rule8Violations)+"\n")